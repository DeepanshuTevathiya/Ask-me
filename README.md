# 🎙️ Waveform

**Turn any recording into a structured brief.**

Waveform takes a YouTube link or a local audio/video file, transcribes it, summarizes it, pulls out action items / key decisions / open questions, and indexes it so you can chat with the recording afterward.

🔗 **Live app:** [waveform-deepminds.streamlit.app](https://waveform-deepminds.streamlit.app/)
📦 **Repo:** [github.com/DeepanshuTevathiya/Waveform](https://github.com/DeepanshuTevathiya/Waveform)

---

## Overview

Meetings, lectures, and long-form videos are easy to record and hard to revisit. Waveform runs a recording through a full pipeline — audio extraction, transcription, summarization, structured extraction, and retrieval-augmented chat — so you get a searchable brief instead of an hour of raw audio.

It ships two interfaces on top of the same pipeline:
- **CLI** (`main.py`) — run the pipeline end-to-end from the terminal.
- **Web app** (`app.py`) — a Streamlit UI to process a recording and explore the results interactively.

## Features

- 🎧 **Audio ingestion** from a YouTube URL or an uploaded local file
- 📝 **Transcription** in English or Hinglish
- 🧠 **Summarization** — auto-generated title + summary
- 📌 **Structured extraction** — action items, key decisions, and open questions pulled out separately
- 💬 **Chat with the recording** — ask follow-up questions answered from the transcript via RAG
- 🖥️ **Two front ends** — a terminal pipeline and a Streamlit dashboard

## Tech stack

| Layer            | Choice                                      |
|-------------------|----------------------------------------------|
| Transcription      | OpenAI Whisper (local/open-source)          |
| LLM (summary, extraction, chat) | Mistral API (La Plateforme)      |
| Embeddings         | sentence-transformers (local, e.g. all-MiniLM) |
| Vector store        | ChromaDB                                   |
| Audio processing    | pydub                                      |
| UI                  | Streamlit                                  |
| Orchestration       | Python                                     |

## How it works

```
Source (YouTube URL / local file)
        │
        ▼
 process_audio()        → extracts & chunks audio
        │
        ▼
 transcribe_all()        → Whisper transcription (English/Hinglish)
        │
        ▼
 get_summary()           → title + summary via Mistral
        │
        ▼
 extract_action_items()
 extract_key_decisions()  → structured extraction via Mistral
 extract_questions()
        │
        ▼
 build_rag_chain()        → embeds transcript, indexes in ChromaDB
        │
        ▼
 ask_question()           → chat with the recording afterward
```

## Project structure

```
Waveform/
├── core/
│   ├── transcibe.py       # transcribe_all()
│   ├── summarize.py       # get_summary()
│   ├── extractor.py       # extract_action_items / extract_key_decisions / extract_questions
│   └── rag_engine.py      # build_rag_chain() / ask_question()
├── utils/
│   └── audio_processor.py # process_audio()
├── ui/                     # standalone HTML/CSS/JS front end
├── vector_db/              # ChromaDB persistence
├── app.py                  # Streamlit web app
├── main.py                 # CLI entry point
└── requirements.txt
```

## Getting started

### Prerequisites
- Python 3.11+ recommended
- A [Mistral API key](https://console.mistral.ai/)

### Installation

```bash
git clone https://github.com/DeepanshuTevathiya/Waveform.git
cd Waveform
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment variables

Create a `.env` file in the project root:

```
MISTRAL_API_KEY=your_key_here
```

### Run the CLI

```bash
python main.py
```

You'll be prompted for a YouTube URL or local file path and a language, then the full pipeline runs in the terminal, followed by an interactive chat loop.

### Run the Streamlit app

```bash
streamlit run app.py
```

## Known limitations

- **YouTube downloads on cloud hosting**: shared datacenter IPs (e.g. Streamlit Community Cloud) are sometimes blocked by YouTube with a `403 Forbidden` error. This works reliably when run locally. Workarounds include supplying cookies from a logged-in session or routing through a proxy.
- Local file upload is the more reliable path when running on cloud deployments.

## Roadmap

- [ ] Cookie-based auth for YouTube downloads on cloud deployments
- [ ] Speaker diarization in the transcript view
- [ ] Export brief as PDF/Markdown

## License

No license has been applied — all rights reserved. This code is public for portfolio/reference purposes; please don't reuse or redistribute without permission.

## Author

**Deepanshu Tevathiya**
AI/ML Engineer Intern · B.Tech CSE (Data Science), SRMIST
[LinkedIn](https://www.linkedin.com/in/deepanshu-tevathiya/) · [GitHub](https://github.com/DeepanshuTevathiya)
