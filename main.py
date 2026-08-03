from utils.audio_processor import process_audio
from core.transcibe import transcribe_all
from core.summarize import get_summary

audio_chunks = process_audio("https://www.youtube.com/watch?v=CHvB1qgWAoI")
transcript = transcribe_all(audio_chunks)
summary = get_summary(transcript)
print(summary)