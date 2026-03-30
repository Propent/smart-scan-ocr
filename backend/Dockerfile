FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for OCR and opencv
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv for package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set uv to use the system Python and not try to download 3.14
ENV UV_PYTHON_PREFERENCE=only-system

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv sync
RUN uv sync --no-dev

# Pre-download EasyOCR models to avoid timeouts and high memory usage during the first request
# This ensures the model is baked into the image.
RUN .venv/bin/python -c "import easyocr; reader = easyocr.Reader(['en'], gpu=False)"

# Copy the application code
COPY . .

# Expose port
EXPOSE 8080

# Command to run the application
# Use uv run to ensure we use the installed virtualenv
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
