FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY data/ ./data/
COPY templates/ ./templates/

ENV PYTHONPATH=/app
ENV APP_MODE=production
ENV WEB_APP_PORT=7777

EXPOSE 7777

CMD ["python", "src/main.py", "--web"]
