import pdfplumber
import re
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import ChatOllama
# from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate



PROMPT_TEMPLATE = """

You are an expert research assistant. Use the provided context to answer the query. 
If unsure, state that you don't know. Be concise and factual (max 3 sentences).

Query: {user_query} 
Context: {document_context} 
Answer:
"""


def starts_with_number_dot(s):
    pattern = r"^\d+(?:\.\d+){0,2}\.\s+\S.*"
    return bool(re.match(pattern, s))

def check_session(pdf_path):
    session = []
    topic = ""
    content = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page_number in range(5,7):
            page = pdf.pages[page_number]
            text = page.extract_text()
            lines = text.split("\n")
            for index, line in enumerate(lines):
                if index != 0 and index !=1 and index!= len(lines)-2 and index!=len(lines) - 1:
                    # print(line)
                    if index == 2 and not starts_with_number_dot(line):
                        content = content+line+"\n"
                    if starts_with_number_dot(line):
                        # topic = line
                        session.append(f"Topic: {topic}\nContent: {content}")
                        topic = line
                        content = ""
                    else:
                        content = content + line +"\n"
        return session

# Example usage
pdf_path = "./code.pdf"
  # Matches "a.b.c" format

content = check_session(pdf_path)

embeddings = OllamaEmbeddings(model = 'deepseek-r1:1.5b')

llm = ChatOllama(
    model = "deepseek-r1:1.5b"
    # temperature = 0.8,
    # num_predict = 256,
)

vector_store = InMemoryVectorStore(embeddings)

vector_store.add_texts(content)


def generate_answer(user_query, context_documents):
  context_text = "\n\n".join([doc.page_content for doc in context_documents])
  conversation_prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
  response_chain = conversation_prompt | llm
  return response_chain.invoke({"user_query": user_query, "document_context": context_text})

def find_related_documents(query):
  return vector_store.similarity_search(query)
  
# ai_response = generate_answer("")
print("finding related...")
docs = find_related_documents("What is PE1000N?")
print("gen...")
output = generate_answer("What is PE1000N?", docs)
print(output.content)
