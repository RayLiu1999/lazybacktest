# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 複製依賴檔案
COPY pyproject.toml .

# 安裝 Python 依賴
RUN pip install --no-cache-dir .

# 複製程式碼
COPY app ./app
COPY scripts ./scripts

# 暴露端口
EXPOSE 8000

# 啟動命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
