import pdfplumber
import re
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.embeddings import OllamaEmbeddings
from langchain.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_core.runnables import RunnablePassthrough
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pdfplumber
from langchain import hub
from langchain_community.vectorstores import Chroma
from langchain.document_loaders import PDFPlumberLoader
from langchain_core.output_parsers import StrOutputParser

def chunk_content(content, chunk_size=500, overlap=0):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n", " ", ""]
    )
    return text_splitter.split_text(content)

PROMPT_TEMPLATE = """
You are an expert research assistant. Use the provided context to answer the query. 
Query: {user_query} 
Context: {document_context} 
Answer:
"""

def starts_with_number_dot(s):
    pattern = r"^\d+(?:\.\d+){0,3}\s+\S.*"
    return bool(re.match(pattern, s))

def check_session(pdf_path):
    session = []
    topic = ""
    content = ""
    keep = False
    with pdfplumber.open(pdf_path) as pdf:
        for page_number in range(len(pdf.pages)):
            page = pdf.pages[page_number]
            text = page.extract_text()
            lines = text.split("\n")
            for index, line in enumerate(lines):
                if index != 0 and index !=1 and index!= len(lines)-2 and index!=len(lines) - 1:
                    if starts_with_number_dot(line) and keep == False:
                        session.append(f"{topic}\n{content}")
                        topic = line
                        content = ""
                        keep = True
                    elif starts_with_number_dot(line) and keep == True:
                        topic = ""
                        content = content + line + "\n"
                        keep = True 
                    else:
                        keep = False
                        content = content + line +"\n"
        return session
from langchain_core.documents import Document
pdf_path = "./code.pdf"
content = check_session(pdf_path)
docs = []
for index, cont in enumerate(content):
    doc = Document(id=str(index+1), page_content = cont)
    docs.append(doc)
    
embeddings = OllamaEmbeddings(model = "deepseek-r1:1.5b")
llm = ChatOllama(
    model = "deepseek-r1:1.5b",
    temperature = 0,
)

vector_store = InMemoryVectorStore(embeddings)
vector_store.add_documents(documents = docs)
retriever = vector_store.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 5, "fetch_k": 10, "lambda_mult": 0.5},
)

template = """Answer the question based only on the following context:
{context}

Question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
    # return rag_chain.invoke(user_query)

output = rag_chain.invoke("if else condition structure")
print(output)