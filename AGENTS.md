# AGENTS.md - Guidelines for AI Agent Contributors

Welcome! This document outlines mandatory architecture rules, coding standards, and testing procedures for any AI agent (or developer) contributing code to the **Agentic Manhua Reader (读画 - Dú Huà)** codebase.

---

## 🎯 Core Principles

1. **Preserve Existing Architecture & API Contracts**:
   - Do not modify core endpoint signatures (`/api/ocr`, `/api/dictionary`, `/api/vocab`, `/api/chat`) without updating both backend tools and frontend consumers.
2. **Fail Explicitly & Log Tracebacks**:
   - Never swallow exceptions using empty `try...except` blocks.
   - Log errors explicitly with Python `logging` or `console.error` and let startup/requests fail predictably.
3. **Security & Secrets**:
   - Never output, log, or commit API keys (`GEMINI_API_KEY`, `GOOGLE_API_KEY`, etc.) or private tokens.

---

## 📐 Bounding Box & Coordinate System Rules

1. **Percentage-Based Layout Only**:
   - Bounding box overlays in `ImageViewer.jsx` MUST be rendered using CSS percentage values (`left: X%`, `top: Y%`, `width: W%`, `height: H%`) calculated directly from the image's intrinsic `naturalWidth` and `naturalHeight`.
   - **DO NOT** use `getBoundingClientRect()` or JS resize listeners to compute absolute pixel coordinates for overlay positioning. CSS percentage layout guarantees responsiveness across Retina displays, viewport zooms, and container resizes.

2. **Backend OCR Preprocessor Restrictions**:
   - In `ocr_tool.py`, **NEVER** set `use_doc_orientation_classify=True` or `use_doc_unwarping=True` in PaddleOCR.
   - Document preprocessors crop white margins and stretch comic panels, which distorts coordinate alignment relative to the uncropped original source image displayed on the frontend.

3. **Coordinate Transformation Function**:
   - The `transform_point_back(pt, angle, img_w, img_h)` function in `ocr_tool.py` handles orientation inverse transformations for $0^\circ, 90^\circ, 180^\circ, 270^\circ$. Any modifications to rotation mapping must be verified against `backend/tests/unit/test_ocr_tool.py`.

---

## 🛠️ Codebase Structure & Conventions

### Backend (`backend/app/`)
- `agent.py`: Defortifies the Google ADK `root_agent` (`manhua_tutor`) and model configurations.
- `fast_api_app.py`: Exposes FastAPI REST endpoints and manages the ADK `Runner` and `InMemorySessionService`.
- `tools/`:
  - `ocr_tool.py`: Handles PaddleOCR execution and coordinate parsing.
  - `dictionary_tool.py`: CC-CEDICT Trie prefix tree lookup.
  - `vocab_tool.py`: Manages user flashcards in JSON storage.

### Frontend (`frontend/src/`)
- `components/ImageViewer.jsx`: Image rendering container with hover tooltips and percentage overlay boxes.
- `components/AgentChatPanel.jsx`: Page-aware chat sidebar communicating with `/api/chat`.
- `index.css`: Glassmorphic dark mode styling system using CSS custom properties (`var(--accent-color)`, `var(--border-color)`).

---

## 🧪 Verification Checklist for Agents

Before completing any task, you **MUST** execute and pass the full test suite:

1. **Backend Unit Tests**:
   ```bash
   cd backend
   uv run pytest tests/unit/test_ocr_tool.py
   ```
   *Must report 6/6 passed.*

2. **Frontend Playwright Alignment Tests**:
   ```bash
   cd frontend
   npm test
   ```
   *Must report ✅ OCR Alignment Regression Test Passed Successfully!*

3. **Server Verification**:
   - Verify that FastAPI server (`uv run uvicorn app.fast_api_app:app --port 8000`) and Vite server (`npm run dev`) start without errors.
