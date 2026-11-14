from __future__ import annotations

import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None

load_dotenv()

app = FastAPI(title="Hi Rainbow AI App", version="1.0.0")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


class ToolRequest(BaseModel):
    tool: str
    prompt: str = ""
    language: str = "en"


def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        return None
    return OpenAI(api_key=api_key)


def local_fallback(tool: str, prompt: str, language: str) -> str:
    prompt_clean = (prompt or "").strip()
    if not prompt_clean:
        prompt_clean = "general learning"

    tool_map = {
        "math": f"Here is a quick math challenge: 12 + 8 = 20. Explain the steps to a child in a simple way. Topic: {prompt_clean}",
        "quiz": f"Quiz time! Question: What is the capital of India? A) Delhi B) Mumbai C) Chennai D) Kolkata. Correct answer: A) Delhi. Topic: {prompt_clean}",
        "story": f"Story: A little child named Asha found a rainbow in the garden and learned that every color teaches kindness. Story topic: {prompt_clean}",
        "resume": f"Resume summary for {prompt_clean}: Organized, cheerful, eager learner with strong communication skills, teamwork, and a growth mindset.",
        "translate": f"Translated content for '{prompt_clean}' in {language}: 'This is a simple and friendly translation for learning.'",
        "tutor": f"Tutor response: Let's break this into easy steps. First understand the idea, then practice with one example, and finally try a similar question.
Topic: {prompt_clean}",
    }
    return tool_map.get(tool, f"I can help with: {prompt_clean}. Let's keep it simple and friendly.")


def ai_response(tool: str, prompt: str, language: str) -> str:
    client = get_openai_client()
    if not client:
        return local_fallback(tool, prompt, language)

    system_prompt = "You are a friendly educational AI assistant for children. Keep answers simple, correct, and encouraging."
    user_prompt = f"Tool: {tool}\nLanguage: {language}\nRequest: {prompt}"

    try:
        completion = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        if hasattr(completion, "output_text") and completion.output_text:
            return completion.output_text
        if hasattr(completion, "output"):
            for item in completion.output:
                if getattr(item, "type", None) == "message":
                    parts = []
                    for block in getattr(item, "content", []):
                        if hasattr(block, "text"):
                            parts.append(block.text)
                    if parts:
                        return "\n".join(parts)
    except Exception:
        pass

    return local_fallback(tool, prompt, language)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/health")
async def health():
    return JSONResponse({"status": "ok", "service": "Hi Rainbow AI App"})


@app.post("/api/tool")
async def tool_endpoint(req: ToolRequest):
    result = ai_response(req.tool, req.prompt, req.language)
    return JSONResponse({"tool": req.tool, "response": result})


@app.get("/api/demo")
async def api_demo():
    return JSONResponse({
        "status": "demo",
        "message": "The AI backend is ready. Send a POST to /api/tool with {\"tool\":\"quiz\", \"prompt\":\"...\"}",
    })


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
