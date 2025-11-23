FROM python:3.12-slim

WORKDIR /app

# Copy requirements first
COPY requirements.txt .

RUN pip install -r requirements.txt

# Copy post-api code
COPY post.py .

EXPOSE 5000

ENV MYSQL_HOST=weight-db

ENTRYPOINT ["python", "post.py"]
