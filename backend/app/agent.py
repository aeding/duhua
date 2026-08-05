# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import logging
import datetime
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

# Automatically load GEMINI_API_KEY from gemini_key.txt if present
key_file = "/home/admin_/gemini_key.txt"
if not os.environ.get("GEMINI_API_KEY") and os.path.exists(key_file):
    try:
        with open(key_file, "r") as f:
            key_val = f.read().strip()
            if key_val:
                os.environ["GEMINI_API_KEY"] = key_val
                os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "false"
                logger.info("Loaded GEMINI_API_KEY from %s", key_file)
    except Exception as e:
        logger.error("Failed to read GEMINI_API_KEY from %s: %s", key_file, e)
        raise RuntimeError(f"Failed to read GEMINI_API_KEY from {key_file}: {e}") from e

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.apps.app import EventsCompactionConfig
from google.adk.models import Gemini
from google.genai import types
from google.adk.tools import FunctionTool, ToolContext
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.plugins.logging_plugin import LoggingPlugin
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.tools import BaseTool

import re
import json

from app.tools.ocr_tool import run_ocr
from app.tools.dictionary_tool import lookup_vocab
from app.tools.vocab_tool import manage_vocab

MODEL = "gemini-3.6-flash"

class SecurityGuardrailPlugin(BasePlugin):
    def __init__(self, name="security_guardrail_plugin", **kwargs):
        super().__init__(name=name, **kwargs)

    async def before_model_callback(self, *, callback_context: CallbackContext, llm_request: LlmRequest) -> LlmResponse | None:
        # Example guardrail: inspect input request
        return None
        
class PiiRedactionPlugin(BasePlugin):
    def __init__(self, name="pii_redaction_plugin", **kwargs):
        super().__init__(name=name, **kwargs)

    async def before_model_callback(self, *, callback_context: CallbackContext, llm_request: LlmRequest) -> LlmResponse | None:
        for p in llm_request.parts:
            if hasattr(p, 'text') and p.text:
                # Basic email redaction
                p.text = re.sub(r'[\w\.-]+@[\w\.-]+', '[REDACTED_EMAIL]', p.text)
        return None

class IntentOutcomeLoggingPlugin(BasePlugin):
    def __init__(self, name="intent_outcome_logging_plugin", **kwargs):
        super().__init__(name=name, **kwargs)

    async def before_tool_callback(self, *, callback_context: CallbackContext, tool: BaseTool, args: dict, tool_context: ToolContext) -> dict | None:
        logger.info(json.dumps({"event": "tool_intent", "tool": tool.name, "args": args}))
        return None
        
    async def after_tool_callback(self, *, callback_context: CallbackContext, tool: BaseTool, args: dict, tool_context: ToolContext, tool_response: dict) -> dict | None:
        # Avoid dumping huge OCR outputs, just log the keys or a summary
        log_resp = "success" if isinstance(tool_response, list) or "error" not in str(tool_response).lower() else "error"
        logger.info(json.dumps({"event": "tool_outcome", "tool": tool.name, "status": log_resp}))
        return None

async def generate_memories_callback(callback_context: CallbackContext):
    """Sends the session's events to Memory Service."""
    if callback_context.session:
        try:
            await callback_context.add_session_to_memory()
        except Exception as e:
            logger.error(f"Error saving to memory: {e}")
    return None

def confirm_vocab_clear(action: str, **kwargs) -> bool:
    return action == "clear"

manage_vocab_tool = FunctionTool(manage_vocab, require_confirmation=confirm_vocab_clear)

vision_agent = Agent(
    name="vision_agent",
    model=Gemini(model=MODEL, retry_options=types.HttpRetryOptions(attempts=3)),
    description="Extracts Chinese text and bounding boxes from images.",
    instruction="You are a Vision specialist. Call run_ocr when the user asks to read an image.",
    tools=[run_ocr],
    after_agent_callback=generate_memories_callback,
)

tutor_agent = Agent(
    name="tutor_agent",
    model=Gemini(model=MODEL, retry_options=types.HttpRetryOptions(attempts=3)),
    description="Looks up definitions and manages vocabulary.",
    instruction="You are a Tutor specialist. Call lookup_vocab for definitions and manage_vocab for flashcards.",
    tools=[lookup_vocab, manage_vocab_tool],
    after_agent_callback=generate_memories_callback,
)

INSTRUCTION = """You are a highly capable AI Manhua Tutor designed to help users read Mandarin Chinese manhua, manga, and comics.

You are page-aware and receive real-time context about the manhua page currently being displayed in the reader, including its Image URL and extracted Chinese OCR text.

Key Guidelines & Behaviors:
1. **Delegation**: Delegate to the `vision_agent` to extract text from images, and `tutor_agent` to lookup words or manage vocabulary.
2. **Page Context Integration**:
   - Check the `System Context` provided in the message.
   - Use the extracted Chinese text directly.
3. **Tone**: Friendly, encouraging, educational, and clear. Format responses nicely using Markdown.
"""

root_agent = Agent(
    name="manhua_tutor",
    model=Gemini(model=MODEL, retry_options=types.HttpRetryOptions(attempts=3)),
    instruction=INSTRUCTION,
    sub_agents=[vision_agent, tutor_agent],
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
    events_compaction_config=EventsCompactionConfig(compaction_interval=20, overlap_size=3),
    plugins=[
        LoggingPlugin(),
        SecurityGuardrailPlugin(),
        PiiRedactionPlugin(),
        IntentOutcomeLoggingPlugin()
    ]
)
