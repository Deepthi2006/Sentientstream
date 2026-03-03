FROM node:20 AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
# We must inject the production API URL here. 
# Defaults to relative /api routing which we will configure FastAPI to serve
ENV VITE_API_BASE_URL=""
RUN npm run build


FROM python:3.10-slim AS backend

# Install system dependencies for OpenCV and FAISS
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the HuggingFace sentence transformer model into the Docker image 
# so it doesn't crash on boot downloading models
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy the entire backend
COPY . .

# Copy the built React frontend into the static directory of FastAPI
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Expose exactly the port expected by AWS Elastic Beanstalk / App Runner
EXPOSE 8080
ENV BACKEND_PORT=8080

# Use Uvicorn for ASGI deployment
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
