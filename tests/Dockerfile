FROM python:3.11-slim
WORKDIR /tests
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
COPY init.sh .
RUN pip install -r requirements.txt
RUN chmod +x init.sh
CMD ["./init.sh"]
