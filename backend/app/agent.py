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
from google.adk.models import Gemini
from google.genai import types

from app.tools.ocr_tool import run_ocr
from app.tools.dictionary_tool import lookup_vocab
from app.tools.vocab_tool import manage_vocab

MODEL = "gemini-3.6-flash"

INSTRUCTION = """You are a highly capable AI Manhua Tutor designed to help users read Mandarin Chinese manhua, manga, and comics.

You are page-aware and receive real-time context about the manhua page currently being displayed in the reader, including its Image URL and extracted Chinese OCR text.

Key Guidelines & Behaviors:
1. **Page Context Integration**:
   - When the user asks about the page (e.g. "What is happening here?", "Translate this page", "Explain the grammar on this page"), check the `System Context` provided in the message.
   - Use the extracted Chinese text lines in the context directly to provide accurate character-by-character breakdowns, pinyin, and English translations.
   - If the system context text is empty or unavailable but an Image URL is provided, call the `run_ocr` tool with that Image URL to extract text.

2. **Language & Learning Assistance**:
   - Break down complex sentences into individual words/characters.
   - Detail pinyin, grammar structures (e.g. 把 construction, 了 aspect markers, 吧/呢 sentence particles), and nuance.
   - Use `lookup_vocab` to retrieve official CC-CEDICT definitions when asked for deeper dictionary entries.
   - Use `manage_vocab` to save words to the user's vocabulary list or quiz them on saved words.

3. **Tone**:
   - Friendly, encouraging, educational, and clear. Format responses nicely using Markdown (bold, lists, code blocks).
"""

root_agent = Agent(
    name="manhua_tutor",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=INSTRUCTION,
    tools=[run_ocr, lookup_vocab, manage_vocab],
)

app = App(
    root_agent=root_agent,
    name="app",
)
