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

st.markdown(
    """
    <style>
    .wf-hero {
        padding: 3.5rem 0 1.5rem 0;
    }
    .wf-eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-family: monospace;
        font-size: 0.8rem;
        letter-spacing: 0.04em;
        color: #E8A33D;
        margin-bottom: 1.2rem;
    }
    .wf-eyebrow-dot {
        width: 6px; height: 6px;
        border-radius: 50%;
        background: #E8A33D;
        box-shadow: 0 0 0 4px rgba(232,163,61,0.16);
    }
    .wf-hero h1 {
        font-size: 2.8rem;
        font-weight: 700;
        line-height: 1.1;
        margin-bottom: 1rem;
    }
    .wf-hero p {
        font-size: 1.05rem;
        color: rgba(250,250,250,0.6);
        max-width: 46ch;
        margin-bottom: 0;
    }
    .wf-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 1.3rem 1.4rem;
        height: 100%;
    }
    .wf-card .wf-num {
        font-family: monospace;
        font-size: 0.75rem;
        color: #E8A33D;
        display: block;
        margin-bottom: 0.5rem;
    }
    .wf-card .wf-card-title {
        font-weight: 600;
        font-size: 0.98rem;
        margin-bottom: 0.35rem;
    }
    .wf-card .wf-card-desc {
        font-size: 0.85rem;
        color: rgba(250,250,250,0.55);
        line-height: 1.5;
    }
    .wf-steps {
        margin-top: 2.5rem;
    }
    .wf-steps-label {
        font-family: monospace;
        font-size: 0.75rem;
        letter-spacing: 0.04em;
        color: rgba(250,250,250,0.4);
        text-transform: uppercase;
        margin-bottom: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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
    st.markdown(
        """
        <div class="wf-hero">
            <div class="wf-eyebrow"><span class="wf-eyebrow-dot"></span> Local &amp; YouTube sources supported</div>
            <h1>Every recording,<br>heard once,<br>understood forever.</h1>
            <p>Drop in a call, a lecture, or a YouTube link. Waveform transcribes it, pulls out the
            decisions and open questions, and stays around afterward so you can ask it anything.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cards = [
        ("01", "Transcribe", "English or Hinglish, straight from a YouTube link or local file."),
        ("02", "Extract", "Action items, key decisions, and open questions — pulled out automatically."),
        ("03", "Chat", "Ask follow-up questions and get answers grounded in the transcript."),
    ]
    cols = st.columns(3)
    for col, (num, title, desc) in zip(cols, cards):
        with col:
            st.markdown(
                f"""
                <div class="wf-card">
                    <span class="wf-num">{num}</span>
                    <div class="wf-card-title">{title}</div>
                    <div class="wf-card-desc">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown('<div class="wf-steps">', unsafe_allow_html=True)
    st.markdown('<div class="wf-steps-label">Get started</div>', unsafe_allow_html=True)
    st.markdown(
        "1. Choose a **source** in the sidebar — YouTube URL or a local file.\n"
        "2. Pick a **language**.\n"
        "3. Hit **Process recording** and wait for the pipeline to finish."
    )
    st.markdown("</div>", unsafe_allow_html=True)
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