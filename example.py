from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()
app = FastAPI()

# Разрешаем фронтенду делать запросы
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # для теста
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модель для запроса
class Message(BaseModel):
    prompt: str

@app.post("/chat")
async def chat(msg: Message):
    response = client.responses.create(
        model="gpt-5-nano",
        input=[
            {"role": "system", "content": "You are a helpful and energetic assistant."},
            {"role": "user", "content": msg.prompt}
        ]
    )
    return {"reply": response.output_text}
