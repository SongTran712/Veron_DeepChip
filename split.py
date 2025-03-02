import pdfplumber
import re
import elastic
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
# from langchain_openai import ChatOpenAI
# from langchain_openai import OpenAIEmbedding

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

# print(starts_with_number_dot("dsadasddad"))
# assert 1 == 0

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
    with pdfplumber.open(pdf_path) as pdf:
        for page_number in range(len(pdf.pages)):
            page = pdf.pages[page_number]
            text = page.extract_text()
            # tables = page.extract_tables()
            if page_number < 3:
                if text:
                    contents.append(text)
                    sessions.append("Begin of Doc")
                    types.append("Text")
            else:
                if text:
                    lines = text.split("\n") 
                    for index, line in enumerate(lines):
                        # print(line)
                        if index in [0, 1, len(lines) - 2, len(lines) - 1] or starts_with_double_slash(line):
                            # print("here")
                            continue  # Skip empty, header/footer, or comment lines
                        if starts_with_number_dot(line):
                            sessions.append(session)
                            types.append("'Text")
                            contents.append(content)
                            session = line  # Start new session
                            content = ""  # Reset content
                        else:
                            # print(line)
                            content +=  line + "\n"  # Append to session content    types.append("table")
    return sessions, contents, types

from langchain_core.documents import Document
pdf_path = "./code.pdf"
sessions, texts, types = check_session(pdf_path)
# assert 1 == 0
def format_docs(docs):
    return "\n\n".join(
        f"Session: {doc.metadata['session']}\nType: {doc.metadata['type']}\nContent: {doc.page_content}"
        for doc in docs
    )

template = """  
You are an assistant specializing in extract most important text information and identifying code within it.  

Provide a **concise summary** of the text, including a description of any code present.  

Respond **only** with the summary—no introductions, explanations, or additional comments.  

Content: {context}  
"""

prompt = ChatPromptTemplate.from_template(template)

# Define RAG pipeline with metadata-aware retrieval

prompting = ChatOllama(model="llama3.2:1b", temperature=0)
text_summarizes = []
for i in range(len(sessions)):
    try:
        text_summarize = f"This is {types[i]} of Session {sessions[i]} \n"
        rag_chain = (
        RunnablePassthrough()  
        | prompt
        | prompting
        | StrOutputParser()
    )
        text_summarize += rag_chain.invoke({"context":texts[i]})   
        text_summarizes.append(text_summarize)    
        print("Text: ", texts[i])
        print("text Summary: ", text_summarize)
        print(f"Summarize {i} success")
    except Exception:
        print("error in {i}")
        
embed = OllamaEmbeddings(model="llama3.2:1b")
vector_summarizes = [embed.embed_query(x) for x in text_summarizes]

import pandas as pd
df = pd.DataFrame({
    'Sessions': sessions[:10],
    'Types': types[:10],
    'Summary': text_summarizes,
    'Data': texts[:10],
    'Vector Summary': vector_summarizes
})

df.to_csv('data.csv', index=False)

print("CSV file 'data.csv' has been saved successfully!")


import pandas as pd

# Read the CSV file
# df = pd.read_csv('data.csv')

# Print the DataFrame
print(df['Summary'], df['Data'])

# if not elastic.init_and_check():
#     print("Elastic Server not connected")
#     exit(1)
# else:
#     print("Elastic connect successful")
# # assert 1 == 0

# index_name = "lang_app"
# if not elastic.create_index(index_name):
#     print("Create Index fail")   
#     exit(1)


# if elastic.add_to_index(sessions, types, texts, summarizes, vector_summarizes):
#     print("Add success")
# else:
#     exit(1)
    
# print(elastic.query_extract("If else code"))



# # Run query and save output
# output = rag_chain.invoke({"context": text})
# with open('output.txt', "w", encoding="utf-8") as f:
#     f.write(output)
