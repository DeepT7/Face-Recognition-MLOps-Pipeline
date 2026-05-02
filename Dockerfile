FROM python:3.10-slim 

# Prevent Python from writing pyc files and buffering output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1  

# Install Opencv sýstem dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace 

RUN pip install --no-cache-dir "typing-extensions>=4.10.0"

RUN pip install --no-cache-dir --default-timeout=1000 \
    torch==2.8.0 \
    torchvision==0.23.0 \
    --index-url https://download.pytorch.org/whl/cpu

# Install Python dependencies 
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip 
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt 

# Copy the rest of the application code
COPY ./app ./app/
COPY ./edgeface ./edgeface/

# Expose the port the app runs on
EXPOSE 8080

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]

