FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scoring_test/ ./scoring_test/
COPY backend/ ./backend/
COPY tests/ ./tests/

ENV PYTHONPATH=/app/scoring_test:/app/backend
EXPOSE 5000

CMD ["python", "scoring_test/flask_app.py"]
