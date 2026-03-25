# OCR Scan-to-PDF Engine

A high-performance application designed to convert document images into searchable-style PDFs using OCR (EasyOCR).

## Features
- **OCR Text Extraction:** Powered by EasyOCR for accurate text recognition across multiple pages.
- **Asynchronous Workflow:** Background tasks ensure a responsive UI, even for large documents.
- **Real-time Progress Tracking:** Visual feedback for both OCR and PDF generation stages.
- **Searchable PDF Generation:** Automatically generates a PDF containing original images and extracted text overlay.
- **Modern UI:** Clean, two-step reactive workflow with a progress bar and automatic downloading.
- **Self-Contained Dependencies:** No external system binaries like Poppler required.

## Technical Improvements
- **Backend:** Switched from `pdf2image` to `PyMuPDF` (fitz) for reliable cross-platform PDF handling.
- **Task Management:** In-memory `TaskStore` for efficient job tracking and status polling.
- **Frontend:** Robust polling mechanism with progress-to-percentage mapping.

## Production Workflow
1. **Upload:** User uploads an image (JPG, PNG, WebP).
2. **Process:** Backend runs OCR and generates a PDF using ReportLab.
3. **Download:** User receives a downloadable PDF version of their document.

## Getting Started

### Using Docker (Recommended for Production)
The quickest way to deploy the entire stack:
```bash
docker-compose up --build -d
```
- **Frontend:** `http://localhost:5173`
- **Backend API:** `http://localhost:8080`
- **API Documentation:** `http://localhost:8080/docs`

### Manual Installation

#### Backend
1. Navigate to the backend directory: `cd backend`
2. Install dependencies: `uv sync`
3. Configure your `.env` file from `.env.example`.
4. Run the server: `uv run uvicorn app.main:app --port 8080`

#### Frontend
1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Configure your `.env` file from `.env.example`.
4. Run for development: `npm run dev`
5. Build for production: `npm run build`

## Environment Variables

### Backend (`backend/.env`)
- `PROJECT_NAME`: Title of the API.
- `BACKEND_CORS_ORIGINS`: JSON list of allowed origins.
- `OCR_LANGUAGES`: JSON list of languages for EasyOCR.

### Frontend (`frontend/.env`)
- `VITE_API_URL`: The full URL to the backend API (e.g., `http://localhost:8080/api/v1`).

## Tech Stack
- **Frontend:** React, TypeScript, Vite, Tailwind CSS, Lucide Icons.
- **Backend:** FastAPI, EasyOCR, ReportLab, Pydantic.
- **Infrastructure:** Docker, Docker Compose.

---
&copy; 2026 OCR Template Engine
