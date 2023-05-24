# Base image
FROM nvidia/cuda:10.0-cudnn7-runtime-ubuntu18.04

# Set working directory
WORKDIR /app

# Install python3.8 and pip3
RUN apt-get update && apt-get install -y python3.8 python3-pip
RUN python3.8 -m pip install --upgrade pip

# Copy only requirements.txt first, to cache the pip install step
COPY ./requirements.txt /app/requirements.txt

# Install your Python dependencies
RUN python3.8 -m pip install --no-cache-dir -r requirements.txt

# Now copy your whole application
COPY . /app

EXPOSE 8000

CMD ["uvicorn", "main_embedding:app", "--host", "0.0.0.0", "--port", "8000"]
