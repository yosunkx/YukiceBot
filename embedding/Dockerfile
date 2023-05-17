FROM nvidia/cuda:10.0-cudnn7-runtime-ubuntu18.04

WORKDIR /app
ADD . /app

# Install python3.8 and pip3
RUN apt-get update && apt-get install -y python3.8 python3-pip
RUN python3.8 -m pip install --upgrade pip

# Install your Python dependencies
RUN python3.8 -m pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main_embedding:app", "--host", "0.0.0.0", "--port", "8000"]