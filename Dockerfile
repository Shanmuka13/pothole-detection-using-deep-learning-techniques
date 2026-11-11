FROM python:3.10-slim

# Install system libraries required by OpenCV and YOLO.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code

ENV BACKEND_BASE_URL=http://127.0.0.1:8001

EXPOSE 7860 8001

CMD ["sh", "/code/start.sh"]
