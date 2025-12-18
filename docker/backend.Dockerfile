FROM python:3.12-slim

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements/base.txt /app/requirements/base.txt
COPY backend/requirements/local.txt /app/requirements/local.txt
RUN pip install --no-cache-dir -r requirements/local.txt

# Copy project
COPY backend /app

# Create directory for static files
RUN mkdir -p /app/staticfiles

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
