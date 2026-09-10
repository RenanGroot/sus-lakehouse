FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
COPY data/ ./data/

RUN useradd -m -u 1000 appuser
USER appuser

CMD streamlit run app.py --server.port=$PORT --server.address=0.0.0.0