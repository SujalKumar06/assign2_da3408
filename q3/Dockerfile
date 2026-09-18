FROM python:3.13-slim
WORKDIR /app
COPY validate_shard.py .
COPY data/ ./data/
CMD ["python", "validate_shard.py"]
