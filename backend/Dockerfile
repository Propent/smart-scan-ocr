FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for Tesseract, Pandoc, and WeasyPrint
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    tesseract-ocr \
    libtesseract-dev \
    pandoc \
    libpango-1.0-0 \
    libharfbuzz0b \
    libpangoft2-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Install uv for package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set uv to use the system Python
ENV UV_PYTHON_PREFERENCE=only-system

# Copy only the project file
COPY pyproject.toml ./

# Install dependencies (will now include pytesseract instead of easyocr/torch)
RUN uv sync --no-dev

# Copy the application code
COPY . .

# Command to run the application using the Render $PORT
CMD [".venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
