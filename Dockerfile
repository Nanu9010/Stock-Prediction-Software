FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first for better caching
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --default-timeout=100 -r requirements.txt

# Copy project files
COPY . .

# Run static collection on build (Moved to compose command to avoid DB crashes during build)
# RUN python manage.py collectstatic --noinput

EXPOSE 8000
