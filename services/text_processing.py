from langchain.embeddings.openai import OpenAIEmbeddings 
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter

def store_in_faiss(text):
  text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
  chunks = text_splitter.split_text(text)

  embeddings = OpenAIEmbeddings()
  vectorstore = FAISS.from_texts(chunks, embeddings)

  return vectorstore

def retrieve_information(query, vectorstore):
  docs = vectorstore.similarity_search(query, k=5)
  return "\n".join([doc.page_content for doc in docs])