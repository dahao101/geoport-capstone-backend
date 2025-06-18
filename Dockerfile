# Use the official Python image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Install Rust and Cargo (necessary for pywinpty)
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libssl-dev \
    pkg-config \
    libffi-dev \
    libzmq3-dev \
    libjpeg-dev \
    libfreetype6-dev \
    rustc \
    cargo

# Copy project files into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the correct port
EXPOSE 8001

# Start FastAPI server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]

