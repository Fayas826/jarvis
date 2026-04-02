import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_jarvis(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are Jarvis, a smart AI assistant like Tony Stark's assistant. Be concise and helpful."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content
