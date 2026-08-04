import os
import streamlit as st
from dotenv import load_dotenv

from utils.audio_processor import process_audio
from core.transcibe import transcribe_all
from core.summarize import get_summary
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

st.set_page_config(page_title="Waveform", page_icon="🎙️", layout="wide")

if "result" not in st.session_state:
    st.session_state.result = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


def run_pipeline(source: str, language: str) -> dict:
    stage = st.empty()
    progress = st.progress(0)

    stage.info("🎧 Extracting audio...")
    chunks = process_audio(source)
    progress.progress(20)

    stage.info("📝 Transcribing...")
    transcript = transcribe_all(chunks, language)
    progress.progress(45)

    stage.info("🧠 Summarizing...")
    title_summary = get_summary(transcript)
    progress.progress(60)

    stage.info("📌 Extracting action items, decisions & questions...")
    action_items = extract_action_items(transcript)
    decisions = extract_key_decisions(transcript)
    questions = extract_questions(transcript)
    progress.progress(80)

    stage.info("🔗 Building chat index...")
    rag_chain = build_rag_chain(transcript)
    progress.progress(100)

    stage.empty()
    progress.empty()

    return {
        "title": title_summary.title,
        "transcript": transcript,
        "summary": title_summary.summary,
        "action_items": action_items,
        "key_decisions": decisions,
        "open_questions": questions,
        "rag_chain": rag_chain,
    }


# ---------------- sidebar: intake ----------------
st.sidebar.title("🎙️ Waveform")
st.sidebar.caption("Turn any recording into a structured brief.")

source_type = st.sidebar.radio("Source", ["YouTube URL", "Local file"])

source = None
if source_type == "YouTube URL":
    source = st.sidebar.text_input("Video URL", placeholder="https://youtube.com/watch?v=...").strip() or None
else:
    uploaded = st.sidebar.file_uploader(
        "Upload audio/video", type=["mp3", "wav", "m4a", "mp4", "mov", "mkv"]
    )
    if uploaded is not None:
        source = f"temp_{uploaded.name}"
        with open(source, "wb") as f:
            f.write(uploaded.getbuffer())

language = st.sidebar.selectbox("Language", ["english", "hinglish"])

process_clicked = st.sidebar.button(
    "Process recording", type="primary", use_container_width=True, disabled=not source
)

if st.sidebar.button("New session", use_container_width=True):
    st.session_state.result = None
    st.session_state.chat_history = []
    st.rerun()

if process_clicked and source:
    try:
        st.session_state.result = run_pipeline(source, language)
        st.session_state.chat_history = []
    except Exception as e:
        st.error(f"Pipeline failed: {e}")
    finally:
        if source_type == "Local file" and os.path.exists(source):
            os.remove(source)

# ---------------- main area ----------------
result = st.session_state.result

if result is None:
    st.title("Waveform")
    st.write("Add a YouTube URL or local file in the sidebar, then hit **Process recording**.")
else:
    st.title(result["title"])

    tab_summary, tab_actions, tab_decisions, tab_questions, tab_transcript, tab_chat = st.tabs(
        ["Summary", "Action Items", "Key Decisions", "Open Questions", "Transcript", "Chat"]
    )

    with tab_summary:
        st.write(result["summary"])

    with tab_actions:
        for item in result["action_items"]:
            st.markdown(f"- {item}")

    with tab_decisions:
        for item in result["key_decisions"]:
            st.markdown(f"- {item}")

    with tab_questions:
        for item in result["open_questions"]:
            st.markdown(f"- {item}")

    with tab_transcript:
        st.text_area("Full transcript", str(result["transcript"]), height=400)

    with tab_chat:
        for role, msg in st.session_state.chat_history:
            with st.chat_message(role):
                st.write(msg)

        question = st.chat_input("Ask something about this recording...")
        if question:
            st.session_state.chat_history.append(("user", question))
            with st.chat_message("user"):
                st.write(question)
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    answer = ask_question(result["rag_chain"], question)
                st.write(answer)
            st.session_state.chat_history.append(("assistant", answer))