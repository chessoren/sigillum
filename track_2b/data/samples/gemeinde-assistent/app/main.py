import os
import httpx
from fastapi import FastAPI

LLM_BASE_URL = os.environ["LLM_BASE_URL"]  # e.g. http://apertus:8081/v1 on the municipal server
app = FastAPI()


@app.post("/ask")
def ask(question: str):
    r = httpx.post(f"{LLM_BASE_URL}/chat/completions", json={
        "model": os.environ.get("LLM_NAME", "swiss-ai/Apertus-v1.5-8B"),
        "messages": [{"role": "user", "content": question}],
    })
    return r.json()["choices"][0]["message"]
