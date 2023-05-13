FROM mcr.microsoft.com/playwright:v1.32.1-focal

WORKDIR /app
ADD . /app

# Install software-properties-common, and add deadsnakes PPA
RUN apt-get update && apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa

# Install python3.8 and pip3
RUN apt-get update && apt-get install -y python3.8 python3-pip

# Install Tesseract
RUN apt-get install -y tesseract-ocr libtesseract-dev

# Update pip3 to pip corresponding to Python 3.8
RUN python3.8 -m pip install --upgrade pip

# Install your Python dependencies
RUN python3.8 -m pip install --no-cache-dir -r requirements.txt

# Use port 80
EXPOSE 80

CMD ["python3.8", "MeiBotMain.py"]


# Instructions to run:
# 1. Navigate to meibot dir in console
# 2. Build the image with: 'docker build -t meibot .'
# 3. If not created yet: Create the volume with: 'docker volume create meibot-data'
# 4. Run the container with: 'docker run -m 2g -v meibot-data:/app/data meibot'
