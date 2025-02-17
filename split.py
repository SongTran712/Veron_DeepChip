import pdfplumber
import re
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.embeddings import OllamaEmbeddings
from langchain.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_core.runnables import RunnablePassthrough
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pdfplumber
from langchain import hub
from langchain_community.vectorstores import Chroma
from langchain.document_loaders import PDFPlumberLoader
from langchain_core.output_parsers import StrOutputParser
import pandas as pd
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.storage import InMemoryStore
import uuid
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

def chunk_content(content, chunk_size=500, overlap=0):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n", " ", ""]
    )
    return text_splitter.split_text(content)

    
embeddings = OllamaEmbeddings(model = "deepseek-r1:1.5b")
llm = ChatOllama(
    model = "deepseek-r1:1.5b",
    temperature = 0,
)
def starts_with_number_dot(s):
    pattern = r"^\d+(?:\.\d+)*\.?\s+\S.*"  
    return bool(re.match(pattern, s))

def chunk_content(content, chunk_size=500, overlap=50):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n", " ", ""]
    )
    return text_splitter.split_text(content)

def starts_with_double_slash(line):
    """Check if a line starts with '//' (comment line)."""
    return bool(re.match(r'^\s*//', line))


def check_session(pdf_path):
    sessions = []
    contents = []
    types = []
    session = ""
    content = ""
    # typeD = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page_number in range(len(pdf.pages)):
            page = pdf.pages[page_number]
            text = page.extract_text()
            tables = page.extract_tables()
            if page_number < 3:
                if text:
                    contents.append(text)
                    sessions.append("begin")
                    types.append("text")
            else:
                if text:
                    lines = text.split("\n") 
                    for index, line in enumerate(lines):
                        # print(line)
                        if not line or index in [0, 1, len(lines) - 2, len(lines) - 1] or starts_with_double_slash(line):
                            # print("here")
                            continue  # Skip empty, header/footer, or comment lines
                        if starts_with_number_dot(line):
                            sessions.append(session)
                            types.append("text")
                            contents.append(content.strip())
                            session = line  # Start new session
                            content = ""  # Reset content
                        else:
                            content +=  line + "\n"  # Append to session content

                if tables:
                    for table in tables:
                        df = pd.DataFrame(table)
                        markdown_table = df.to_markdown(index=False, tablefmt="pipe")
                        
                        # Assign table to the latest session (if exists)
                        latest_session = sessions[-1] if sessions else "Unknown"
                        contents.append(f"### Table (Page {page_number + 1})\n{markdown_table}")
                        sessions.append(latest_session)
                        types.append("table")
    return sessions, contents, types

from langchain_core.documents import Document
pdf_path = "./code.pdf"
sessions, texts, types = check_session(pdf_path)

docs = [
    Document(
        page_content=text,
        metadata={
            # id_key: doc_ids[i],
            "session": sessions[i],  # Add session info
            "type": types[i],  # Add type (text/table)
            # "content": texts[i]
        }
    ) for i, text in enumerate(texts)
]

vector_store = InMemoryVectorStore(embeddings)
vector_store.add_documents(documents = docs)
retriever = vector_store.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 5, "fetch_k": 10, "lambda_mult": 0.5},
)

def format_docs(docs):
    return "\n\n".join(
        f"Session: {doc.metadata['session']}\nType: {doc.metadata['type']}\nContent: {doc.page_content}"
        for doc in docs
    )

# Define metadata-aware prompt template
template = """Answer the question based ONLY on the following context as most detailed as possible
Moreover, you can return example code if suitable:

{context}

Question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)

# Define RAG pipeline with metadata-aware retrieval
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | ChatOllama(model="deepseek-r1:1.5b", temperature=0)
    | StrOutputParser()
)

# Run query and save output
output = rag_chain.invoke("example code for module ds_sm")
with open('output.txt', "w", encoding="utf-8") as f:
    f.write(output)
