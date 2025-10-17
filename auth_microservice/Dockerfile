FROM python:3.11-slim
WORKDIR /src
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . /src
EXPOSE 8001
# Use SERVICE_PORT env var from docker-compose, with a default of 8001
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${SERVICE_PORT:-8001} --reload"]
