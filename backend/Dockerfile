FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

RUN apt-get update && apt-get install -y poppler-utils tesseract-ocr libmagic-dev ffmpeg libsm6 libxext6

RUN pip install -Uq "unstructured[all-docs]" pillow lxml pillow
RUN pip install -Uq chromadb tiktoken
RUN pip install -Uq langchain langchain-community langchain-ollama
RUN pip install -Uq python_dotenv
