from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_mistralai import ChatMistralAI
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field
import os

def get_llm():
    return ChatMistralAI(
        model_name="mistral-small-latest",
        api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=0.3
    )

def split_text(transcript:str)->list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 3000,
        chunk_overlap = 500
    )

    return splitter.split_text(transcript)

class Output(BaseModel):
    title:str = Field(description="tittle of the text")
    summary:str = Field(description="Generated Summary")

def get_summary(transcript:str)->str:
    llm = get_llm()
    parser = PydanticOutputParser(pydantic_object=Output)

    prompt = ChatPromptTemplate.from_messages([
    ("system", "Summarize this portion of a meeting transcript concisely."),
    ("human", "{text}"),
    ])

    summary_chain = prompt | llm | StrOutputParser()

    chunks = split_text(transcript)
    chunk_summary = [summary_chain.invoke({'text':chunk}) for chunk in chunks]

    combined = "\n".join(chunk_summary)

    combined_prompt = PromptTemplate(
        template="""You are an expert meeting analyst.

    Your task is to combine the partial meeting summaries into a single, coherent summary.

    IMPORTANT:
    - The `title` is NOT a summary heading.
    - Infer the actual meeting title from the meeting content, as if it were the title of the original transcript.
    - The title should describe what the meeting was actually about.
    - Do NOT prefix it with words like:
    - "Meeting Summary"
    - "Summary"
    - "Discussion on"
    - "Overview"
    - Keep the title concise (3-8 words).
    - If a project name, feature name, sprint name, client name, or product name is discussed, use it in the title.
    - If no explicit title exists, generate the most natural meeting name based on the discussion.

    Generate the final summary in clear bullet points.

    Partial summaries:
    {text}\n{format_instruction}""",
        input_variables=["text"],
        partial_variables={"format_instruction": parser.get_format_instructions()}
    )
 
    final_chain = combined_prompt | llm | parser

    summary = final_chain.invoke({
        "text": combined
    })

    return summary
