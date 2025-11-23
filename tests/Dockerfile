FROM python:3.11-slim
WORKDIR /tests

COPY requirements.txt .
RUN pip install -r requirements.txt

CMD ["pytest", "-v"]
