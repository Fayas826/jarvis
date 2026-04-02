from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import run_multi_agent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    message: str

def detect_mode(text: str):
    text = text.lower()
    if any(word in text for word in ["analyze", "market", "trend", "price", "data", "hud"]):
        return "hud"
    elif any(word in text for word in ["activate", "youtube", "google", "override", "reactor"]):
        return "reactor"
    elif any(word in text for word in ["scan", "system", "time", "date", "grid"]):
        return "grid"
    else:
        return "default"

@app.post("/jarvis")
def jarvis(query: Query):
    result = run_multi_agent(query.message)
    mode = detect_mode(str(result))
    return {
        "response": str(result),
        "mode": mode
    }
