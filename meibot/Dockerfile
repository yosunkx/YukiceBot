FROM python:3.8-slim

WORKDIR /app
ADD . /app

# Install dependencies for Playwright
RUN apt-get update && apt-get install -y wget gnupg2 ca-certificates \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable fonts-ipafont-gothic fonts-wqy-zenhei fonts-thai-tlwg fonts-kacst fonts-freefont-ttf libxss1 \
      --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Install Tesseract
RUN apt-get update && apt-get install -y tesseract-ocr libtesseract-dev

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Use port 80
EXPOSE 80

CMD ["python", "MeiBotMain.py"]


# Instructions to run:
# 1. Navigate to meibot dir in console
# 2. Build the image with: 'docker build -t meibot .'
# 3. Create the volume with: 'docker volume create meibot-memory'
# 4. Run the container with: 'docker run -m 2g -v meibot-memory:/app/memory meibot'
