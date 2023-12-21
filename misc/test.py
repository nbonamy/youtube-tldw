#!/usr/bin/env python3

from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OllamaEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms import Ollama

print('initializing')
ollama = Ollama(base_url='http://localhost:11434', model="llama2")

print('downloading')
loader = WebBaseLoader("https://www.gutenberg.org/files/1727/1727-h/1727-h.htm")
data = loader.load()

print('splitting')
text_splitter=RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
all_splits = text_splitter.split_documents(data)

print('embedding')
oembed = OllamaEmbeddings(base_url="http://localhost:11434", model="llama2")
vectorstore = Chroma.from_documents(documents=all_splits, embedding=oembed)

print('similarity')
question="Who is Neleus and who is in Neleus' family?"
docs = vectorstore.similarity_search(question)

print('retrieving')
qachain=RetrievalQA.from_chain_type(ollama, retriever=vectorstore.as_retriever())
print(qachain({"query": question}))
