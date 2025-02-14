# import pydantic.v1 
from langchain_ollama import ChatOllama
# from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import PDFPlumberLoader
from langchain import hub
# # from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

import tiktoken  # If using OpenAI-compatible models

tokenizer = tiktoken.get_encoding("cl100k_base")  # Adjust for your model

PROMPT_TEMPLATE = """

You are an expert research assistant. Use the provided context to answer the query. 
If unsure, state that you don't know. Be concise and factual (max 3 sentences).

Query: {user_query} 
Context: {document_context} 
Answer:
"""

embeddings = OllamaEmbeddings(model = 'deepseek-r1:1.5b')

llm = ChatOllama(
    model = "deepseek-r1:1.5b"
    # temperature = 0.8,
    # num_predict = 256,
)

vector_store = InMemoryVectorStore(embeddings)
print('loading pdf...')
raw_docs = PDFPlumberLoader('./table.pdf').load() #support OCR
print("Splitting...")
text_splitter = CharacterTextSplitter(chunk_size=1000,chunk_overlap=10)
# documents = text_splitter.split_documents(raw_documents)
all_splits = text_splitter.split_documents(raw_docs)
print(all_splits)
# _ = vector_store.add_documents(documents=all_splits)

def generate_answer(user_query, context_documents):
  context_text = "\n\n".join([doc.page_content for doc in context_documents])
  conversation_prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
  response_chain = conversation_prompt | llm
  return response_chain.invoke({"user_query": user_query, "document_context": context_text})

def find_related_documents(query):
  return vector_store.similarity_search(query)
  
# # ai_response = generate_answer("")
# print("finding related...")
# docs = find_related_documents("What is PE1000N?")
# print("gen...")
# output = generate_answer("What is PE1000N?", docs)
# print(output.content)
