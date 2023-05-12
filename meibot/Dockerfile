FROM python:3.8-slim

WORKDIR /app
ADD . /app
RUN pip install --no-cache-dir -r requirements.txt

#use port 80
EXPOSE 80

CMD ["python", "MeiBotMain.py"]

# Instructions to run:
# 1. Navigate to meibot dir in console
# 2. Build the image with: 'docker build -t meibot .'
# 3. Create the volume with: 'docker volume create meibot-memory'
# 4. Run the container with: 'docker run -v meibot-memory:/app/Memory meibot'
