# Use slim Python base
FROM python:3.14-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Command to run the application
CMD flask --app flaskr run --debug --host=0.0.0.0 --port=${APP_PORT:-5000}