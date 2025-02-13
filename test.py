from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from transformers import AutoTokenizer
from langchain.docstore.document import Document as LangchainDocument
from langchain.docstore.document import Document as LangchainDocument
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_ollama import ChatOllama
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.prompts import ChatPromptTemplate

embeddings = OllamaEmbeddings(model = 'deepseek-r1:1.5b')

llm = ChatOllama(
    model = "deepseek-r1:1.5b"
    # temperature = 0.8,
    # num_predict = 256,
)


vector_store = InMemoryVectorStore(embeddings)


ds = [
    './docs.pdf'
]
RAW_KNOWLEDGE_BASE = PDFPlumberLoader('./datasheet.pdf').load()
# print(RAW_KNOWLEDGE_BASE)
EMBEDDING_MODEL_NAME = "deepseek-r1:1.5b"
MARKDOWN_SEPARATORS = [
    "\n#{1,6} ",
    "```\n",
    "\n\\*\\*\\*+\n",
    "\n---+\n",
    "\n___+\n",
    "\n\n",
    "\n",
    " ",
    "",
]

    
PROMPT_TEMPLATE = """

You are an expert research assistant. Use the provided context to answer the query. 
If unsure, state that you don't know. Be concise and factual (max 3 sentences).

Query: {user_query} 
Context: {document_context} 
Answer:
"""

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # The maximum number of characters in a chunk: we selected this value arbitrarily
    chunk_overlap=100,  # The number of characters to overlap between chunks
    add_start_index=True,  # If `True`, includes chunk's start index in metadata
    strip_whitespace=True,  # If `True`, strips whitespace from the start and end of every document
    separators=MARKDOWN_SEPARATORS,
)


docs_processed = []
for doc in RAW_KNOWLEDGE_BASE:
    docs_processed += text_splitter.split_documents([doc])
unique_texts = {}

docs_processed_unique = []

for doc in docs_processed:

    if doc.page_content not in unique_texts:

        unique_texts[doc.page_content] = True

        docs_processed_unique.append(doc)                                                                           


_ = vector_store.add_documents(documents=docs_processed_unique)


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