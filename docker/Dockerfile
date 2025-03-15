FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy requirements file
COPY requirements.txt .

# Install dependencies using uv with --system flag
RUN uv pip install --system -r requirements.txt

# Copy application code
COPY src/ ./src/

# Run FastAPI app
CMD ["uvicorn", "src.service.main:app", "--host", "0.0.0.0", "--port", "8000"]
