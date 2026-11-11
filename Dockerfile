FROM python:3.10-slim

# Install core system dependencies required for OpenCV and YOLO graphics compilation
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# Copy requirements and execute python installations
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy all repository components into the container execution context
COPY . /code

# Expose port 7860 (Hugging Face default entry port)
EXPOSE 7860

# Concurrently boot up the FastAPI API server on port 8001 and the Streamlit UI on port 7860
CMD uvicorn app.main:app --host 0.0.0.0 --port 8001 & \
    streamlit run frontend/app.py --server.port 7860 --server.address 0.0.0.0
