import streamlit as st
import openai

from services.text_processing import retrieve_information

client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def generate_file_response(query, vectorstore, agent):
  context = retrieve_information(query, vectorstore)
  
  prompt = f"Use as informações a seguir para responder:\n{context}\n\nPergunta: {query}"
  return agent.predict(prompt)