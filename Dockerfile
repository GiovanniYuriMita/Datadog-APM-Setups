# Dockerfile

FROM python:3.9-slim

# Upgrade PIP
RUN pip install --upgrade pip --no-cache-dir

# Install dependencies
RUN pip install --no-cache-dir ddtrace flask python-json-logger

# Copy application code
COPY app /app

# Set working directory
WORKDIR /app

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "app.py"]