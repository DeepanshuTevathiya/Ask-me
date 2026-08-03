import os 
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpointEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

CHROMA_DIR = "vector_db"
COLLECTION_NAME = "meeting_transcript"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

def get_embedding():
    return HuggingFaceEndpointEmbeddings(
        model=EMBEDDING_MODEL
    )

def build_vector_store(transcript:str)->Chroma:
    print("Building VectorStore...")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap = 100
    )

    chunks = splitter.split_text(transcript)

    docs = [
        Document(page_content=chunk, metadata={"doc_index":i}) for i, chunk in enumerate(chunks)
    ]

    vector_store = Chroma.from_documents(
        documents=docs,
        embedding=get_embedding(),
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_DIR
    )

    return vector_store

def load_vector_store()->Chroma:
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embedding(),
        persist_directory=CHROMA_DIR
    )

def get_retriever(vector_store:Chroma, k:int = 4):
    return vector_store.as_retriever(
        search_type = "similarity",
        kwargs={"k":k}
    ) 