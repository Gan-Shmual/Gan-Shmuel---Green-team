FROM python:3.12-slim

WORKDIR /app

RUN pip install flask

COPY app.py .

ENV PORT=8000
ENV SERVICE_NAME=billing

CMD ["python", "app.py"]
