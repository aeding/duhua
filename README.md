# Agentic Manhua Reader (读画 - Dú Huà)

An AI-powered interactive reader and tutor for Mandarin Chinese manhua (漫画), comics, and graphic novels. Powered by **Google ADK (Agent Development Kit)** and **Gemini 3.6 Flash**, with a high-performance **FastAPI** backend and a modern **React + Vite** glassmorphic web interface.

---

## 🌟 Key Features

1. **Native Percentage-Based Bounding Box Overlay**: Extracts Chinese text and bounding boxes from manhua URLs using PaddleOCR. Overlays are positioned using CSS percentage coordinates (`%`) to remain pixel-perfect across all screen sizes, device pixel ratios, and zoom levels.
2. **Hover-to-Lookup Character Dictionary**: Hovering over any character on the manhua image triggers a CC-CEDICT popup with pinyin, English definitions, and one-click "Add to Vocabulary" capability (backed by a high-speed Trie prefix tree).
3. **Page-Aware AI Tutor Chat**: Integrated sidebar chat powered by Google ADK and Gemini. Automatically receives the image URL and extracted Chinese text of the current page. The tutor provides character-by-character dialogue breakdowns, grammar analyses, and interactive quizzes.
4. **Agentic Vocabulary Flashcards**: Save vocabulary words to a persistent local JSON database, list saved words, and generate AI-driven flashcard quizzes.
5. **Instant Demo Examples**: Includes pre-computed instant demos (e.g. *One Piece*, *Battle Manhua*) for quick testing without waiting for live OCR analysis.

---

## 📁 Project Architecture

```
duhua/
├── backend/
│   ├── app/
│   │   ├── agent.py               # Google ADK agent definition with OCR, Dictionary, & Vocab tools
│   │   ├── fast_api_app.py        # FastAPI server exposing /api/ocr, /api/dictionary, /api/chat, & /api/vocab
│   │   └── tools/
│   │       ├── ocr_tool.py        # PaddleOCR wrapper (doc preprocessors disabled for 1:1 image scale)
│   │       ├── dictionary_tool.py # CC-CEDICT Trie prefix tree dictionary lookup
│   │       └── vocab_tool.py      # Flashcard JSON storage & quiz management
│   └── tests/
│       ├── unit/
│       │   └── test_ocr_tool.py   # Unit tests for OCR coordinate transforms & model settings
│       └── integration/
│           ├── test_ocr.py        # Integration tests for PaddleOCR pipeline
│           └── test_agent.py      # Integration tests for Google ADK agent
├── frontend/
│   ├── src/
│   │   ├── App.jsx                # Main layout connecting API endpoints & components
│   │   ├── mockOcrData.json       # Pre-computed OCR data for Demo 1
│   │   ├── mockOcrData2.json      # Pre-computed OCR data for Demo 2
│   │   ├── index.css              # Dark mode glassmorphic design system
│   │   └── components/
│   │       ├── ImageViewer.jsx    # Responsive image reader with percentage bounding boxes & popups
│   │       └── AgentChatPanel.jsx # Page-aware AI Tutor chat with quick prompts
│   ├── tests/
│   │   └── check_ocr_alignment.cjs# Playwright automated test for bounding box overlay alignment
│   └── vite.config.js             # Vite configuration with /api proxy to localhost:8000
├── scripts/                       # Maintenance, verification, & capture scripts
│   ├── capture_all_demos.cjs      # Captures full-page screenshots of demo pages
│   ├── capture_chat_verification.cjs# Captures agent chat interactions
│   ├── draw_mock_on_original.py   # Draws OCR boxes on source images using Pillow
│   └── print_img_info.py          # Prints raw image dimensions and metadata
└── AGENTS.md                      # Rules & architecture guidelines for AI agent contributors
```

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.12+
- Node.js 18+
- `uv` (Fast Python package installer) or `pip`

### 2. Configure API Key
Create a `gemini_key.txt` file in your home directory or set the `GEMINI_API_KEY` environment variable:
```bash
echo "YOUR_GEMINI_API_KEY" > ~/gemini_key.txt
```

### 3. Run the Backend API Server
```bash
cd backend
uv run uvicorn app.fast_api_app:app --reload --port 8000
```
*The FastAPI server will start on `http://localhost:8000` and automatically preload the CC-CEDICT dictionary into memory.*

### 4. Run the Frontend Application
In a separate terminal:
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 🧪 Testing & Verification

### Backend Unit & Integration Tests
Run pytest in the backend directory:
```bash
cd backend
uv run pytest tests/unit/test_ocr_tool.py
uv run pytest tests/integration/test_ocr.py
```

### Frontend E2E / Overlay Regression Tests
Run the Playwright test suite in the frontend directory:
```bash
cd frontend
npm test
```

---

## 🛠️ Utility Scripts (`scripts/`)

- **Capture Screenshots**: `node scripts/capture_all_demos.cjs`
- **Verify Chat Integration**: `node scripts/capture_chat_verification.cjs`
- **Verify Box Alignment with Pillow**: `uv run python scripts/draw_mock_on_original.py`

---

## 💡 How to Improve & Extend the Project

1. **OCR Engine Optimizations**:
   - Add support for manga-specific vertical text detection models (e.g. MangaOCR / PorOCR).
2. **Offline Dictionary Caching**:
   - Cache pre-rendered translations in IndexedDB for instant page reloads.
3. **Multi-Page Reader Support**:
   - Add page navigation (Next/Prev) for reading entire chapters.
4. **Export Flashcards**:
   - Add Anki CSV export for saved vocabulary words in `vocab_tool.py`.
