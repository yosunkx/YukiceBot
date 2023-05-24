# Base image
FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Install SQLite
RUN apt-get update && apt-get install -y sqlite3 libsqlite3-dev
RUN mkdir -p /var/lib/sqlite

# Copy only requirements.txt first, to cache the pip install step
COPY ./requirements.txt /app/requirements.txt

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Now copy your whole application
COPY . /app

# Expose port
EXPOSE 8080

CMD ["uvicorn", "main_SQLite:app", "--host", "0.0.0.0", "--port", "8080"]

