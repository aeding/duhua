import os
import sys
import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from google.adk.cli import fast_api
from pydantic import BaseModel
from typing import Optional, Any
import uuid
from google.genai import types

from app.tools.ocr_tool import run_ocr, get_ocr_instance
from app.tools.dictionary_tool import lookup_vocab, load_dictionary
from app.tools.vocab_tool import manage_vocab

# Setup root path to backend root
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

AGENT_DIR = os.path.join(BACKEND_DIR, "app")

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Preload CC-CEDICT Trie dictionary asynchronously during server startup
    logger.info("Lifespan startup: Preloading CC-CEDICT dictionary into memory...")
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, load_dictionary)
    logger.info("Lifespan startup: CC-CEDICT dictionary preloaded successfully.")

    # Preload PaddleOCR engine into memory
    logger.info("Lifespan startup: Preloading PaddleOCR engine...")
    await loop.run_in_executor(None, get_ocr_instance)
    logger.info("Lifespan startup: PaddleOCR preloaded successfully.")

    yield
    logger.info("Lifespan shutdown.")

app = fast_api.get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    allow_origins=["*"],
    otel_to_cloud=True,
    lifespan=lifespan,
)
app.title = "backend"
app.description = "API for interacting with the Agent backend"

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from app.agent import app as adk_app

session_service = InMemorySessionService()
adk_runner = Runner(app=adk_app, session_service=session_service)

class OcrRequest(BaseModel):
    image_url: str

class DictRequest(BaseModel):
    text: str

class VocabRequest(BaseModel):
    action: str
    word_data: Optional[dict[str, Any]] = None

class PageContext(BaseModel):
    image_url: Optional[str] = None
    extracted_text: Optional[list[str]] = None

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    page_context: Optional[PageContext] = None

@app.post("/api/ocr")
def api_ocr(req: OcrRequest):
    return run_ocr(req.image_url)

@app.post("/api/dictionary")
def api_dictionary(req: DictRequest):
    return lookup_vocab(req.text)

@app.post("/api/vocab")
def api_vocab(req: VocabRequest):
    return manage_vocab(req.action, req.word_data)

@app.post("/api/chat")
async def api_chat(req: ChatRequest):
    runner = getattr(app.state, "runner", None) or adk_runner
    session_id = req.session_id or str(uuid.uuid4())
    
    # Ensure session exists in session_service
    try:
        sess = await session_service.get_session(app_name=adk_app.name, user_id="default_user", session_id=session_id)
        if not sess:
            await session_service.create_session(app_name=adk_app.name, user_id="default_user", session_id=session_id)
    except Exception as e:
        logger.warning(f"Session lookup error, creating new session: {e}")
        await session_service.create_session(app_name=adk_app.name, user_id="default_user", session_id=session_id)

    if req.page_context:
        ctx_parts = []
        if req.page_context.image_url:
            ctx_parts.append(f"Image URL: {req.page_context.image_url}")
        if req.page_context.extracted_text and len(req.page_context.extracted_text) > 0:
            context_str = "\n".join([f"- {t}" for t in req.page_context.extracted_text[:50]])
            ctx_parts.append(f"Extracted Chinese Text on Page:\n{context_str}")
        else:
            ctx_parts.append("Extracted Chinese Text on Page: [None extracted yet - use run_ocr if needed]")

        full_text = (
            f"[System Context: The user is currently reading a manhua page.\n"
            + "\n".join(ctx_parts)
            + "\n]\n\n"
            f"User Message: {req.message}"
        )
    else:
        full_text = req.message

    user_message = types.Content(parts=[types.Part(text=full_text)], role="user")
    
    response_text = ""
    async for event in runner.run_async(user_id="default_user", session_id=session_id, new_message=user_message):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response_text += part.text
                    
    return {"response": response_text, "session_id": session_id}

# Main execution
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
