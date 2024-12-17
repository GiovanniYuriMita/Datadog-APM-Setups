# Dockerfile

FROM python:3.9-slim

# Upgrade PIP
RUN pip install --upgrade pip

# Install dependencies
RUN pip install ddtrace

# Copy application code
COPY app /app

# Set working directory
WORKDIR /app

# Run the application
CMD ["python", "app.py"]