# Smart Scan OCR (Searchable PDF Engine)

A high-performance, lightweight OCR engine that converts document images and PDFs into searchable, text-layered PDFs. Optimized for deployment on free-tier platforms like Render and Netlify.

## Project Structure

```text
smart-scan-ocr/
├── backend/                # FastAPI Backend
│   ├── app/                # Application logic (FastAPI)
│   ├── example/            # Sample input/output files
│   ├── Dockerfile          # Production Docker config
│   ├── pyproject.toml      # Python dependencies (uv)
│   └── test_accuracy.py    # Accuracy benchmarking script
├── frontend/               # React (Vite) Frontend
│   ├── src/                # React components & logic
│   ├── public/             # Static assets & Netlify config
│   └── package.json        # Node.js dependencies
└── docker-compose.yml      # Local development config
```

## Features

- **Asynchronous OCR:** Handles large documents in the background with real-time progress tracking.
- **Searchable PDFs:** Generates PDFs with invisible text layers for easy searching and copying.
- **Tesseract Integration:** Uses Tesseract OCR for fast, low-memory processing (fits in 512MB RAM).
- **Accuracy Preview:** View extracted text and confidence scores directly in the UI.
- **Multi-Format Support:** Processes images (JPG, PNG) and existing PDFs.

## Tech Stack

- **Backend:** FastAPI, Pytesseract, ReportLab, PyMuPDF (fitz), OpenCV.
- **Frontend:** React 19, Vite, Tailwind CSS, Lucide Icons, Axios.
- **Infrastructure:** Docker, Render (Backend), Netlify/Vercel (Frontend).

## Local Development

### Prerequisites

- [Tesseract OCR](https://tesseract-ocr.github.io/tessdoc/Installation.html) installed on your system.
- Python 3.12+ and [uv](https://github.com/astral-sh/uv) (recommended).
- Node.js 18+.

### Backend Setup

1. `cd backend`
2. `cp .env.example .env`
3. `uv sync`
4. `uv run uvicorn app.main:app --reload --port 8080`

### Frontend Setup

1. `cd frontend`
2. `npm install`
3. Set `VITE_API_URL=http://localhost:8080/api/v1` in `.env`
4. `npm run dev`

## Deployment

### Backend (Render)
- **Runtime:** Docker
- **Root Directory:** `backend`
- **Port:** 8080
- **Env Vars:**
    - `BACKEND_CORS_ORIGINS`: `["https://your-frontend-url.netlify.app"]`

### Frontend (Netlify / Vercel)
- **Build Command:** `npm run build`
- **Output Directory:** `dist`
- **Root Directory:** `frontend`
- **Env Vars:**
    - `VITE_API_URL`: `https://your-backend-url.onrender.com/api/v1`

---
&copy; 2026 Smart Scan OCR Engine
