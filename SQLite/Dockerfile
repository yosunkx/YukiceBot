FROM python:3.8-slim

WORKDIR /app
ADD . /app

# Install SQLite
RUN apt-get update && apt-get install -y sqlite3 libsqlite3-dev
RUN mkdir -p /var/lib/sqlite
# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main_SQLite:app", "--host", "0.0.0.0", "--port", "8000"]
