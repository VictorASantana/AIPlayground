import openai
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def chat_with_openai(prompt, user_message, model="gpt-3.5-turbo"):
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_message}
        ]
    )
    return response['choices'][0]['message']['content']
