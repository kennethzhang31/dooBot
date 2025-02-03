import os
import fitz
from dotenv import load_dotenv
from huggingface_hub import login
from langchain_community.chat_models import ChatOllama
from langchain_community.vectorstores import Chroma
from langchain_experimental.text_splitter import SemanticChunker
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

load_dotenv()
hf_key = os.getenv('HUGGINFACE_API_KEY')
login(token=hf_key)
model_kwargs = {'trust_remote_code': True}
encode_kwargs = {'normalize_embeddings': False}

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    text = ""
    with fitz.open(pdf_path) as pdf:
        for page in pdf:
            text += page.get_text()
    return text

def preprocess_text(text):
    """Cleans extracted text by removing unnecessary newlines and spaces."""
    text = text.replace('\n', ' ').replace('- ', '')
    text = ' '.join(text.split())
    return text

def get_documents(pdf_path):
    """Processes a PDF and splits it into semantic chunks."""
    raw_text = extract_text_from_pdf(pdf_path)
    cleaned_text = preprocess_text(raw_text)
    
    embeddings = HuggingFaceEmbeddings(
        model_name='jinaai/jina-embeddings-v2-base-en',
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )

    text_splitter = SemanticChunker(
        embeddings=embeddings,
        breakpoint_threshold_type='percentile'
    )
    
    return text_splitter.create_documents([cleaned_text])

def load_or_create_vector_store(chunks, persist_directory="./chroma_db"):
    """Loads Chroma vectorstore if it exists, otherwise creates and saves it."""
    embeddings = HuggingFaceEmbeddings(
        model_name='jinaai/jina-embeddings-v2-base-en',
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )

    if os.path.exists(persist_directory):
        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings
        )
    else:
        texts = [chunk.page_content for chunk in chunks]
        vectorstore = Chroma.from_texts(
            texts=texts,
            embedding=embeddings,
            persist_directory=persist_directory
        )
    
    return vectorstore

PDF_PATH = '../data/dorm_rules_nthu.pdf'
documents = get_documents(PDF_PATH)
vectorstore = load_or_create_vector_store(documents)

retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 2}
)
template = """
You are a dormitory secretary who answers questions from students about the rules.
Based on the provided context, answer the question clearly.
Context: {context}

If the context does **not** contain relevant information, **only say you don't know**.

Question: {question}

Answer:
"""
prompt = ChatPromptTemplate.from_template(template)

llm = ChatOllama(model='mistral')

rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)