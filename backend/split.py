from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama.chat_models import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever

pdf_path = './code.pdf'
loader = UnstructuredPDFLoader(pdf_path)
data = loader.load()

local_model = "deepseek-r1:1.5b"
llm  = ChatOllama(model = local_model, temperature = 0)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_documents(data)
print(f"Text split into {len(chunks)} chunks")

vector_store = Chroma.from_documents(documents=chunks,
    embedding=OllamaEmbeddings(model="nomic-embed-text"),
    collection_name="local-rag")


QUERY_PROMPT = PromptTemplate(
    input_variables=["question"],
    template="""You are an AI language model assistant. Your task is to generate 2
    different versions of the given user question to retrieve relevant documents from
    a vector database. By generating multiple perspectives on the user question, your
    goal is to help the user overcome some of the limitations of the distance-based
    similarity search. Provide these alternative questions separated by newlines.
    Original question: {question}""",
)

# Set up retriever
retriever = MultiQueryRetriever.from_llm(
    vector_store.as_retriever(), 
    llm,
    prompt=QUERY_PROMPT
)



template = """Answer the question based ONLY on the following context:
{context}
Question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
def chat_with_pdf(question):
    """
    Chat with the PDF using the RAG chain.
    """
    return display(Markdown(chain.invoke(question)))

print(chat_with_pdf("Code for Source file layout please"))

