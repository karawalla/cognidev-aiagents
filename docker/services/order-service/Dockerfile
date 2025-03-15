FROM python:3.11-slim

WORKDIR /app

RUN pip install uv
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

COPY src/ ./src/

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
