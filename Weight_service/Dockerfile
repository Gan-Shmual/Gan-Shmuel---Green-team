# Use an official lightweight Python image as a parent image
FROM python:3.14-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

RUN mkdir -p /app/in

# Command to run the application
CMD ["python", "app.py"]