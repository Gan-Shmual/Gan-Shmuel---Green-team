FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY get-weight.py .

EXPOSE 5000

ENV MYSQL_HOST=weight-db

ENTRYPOINT [ "python", "get-weight.py" ]

