FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY monitor_service.py .
COPY templates/ templates/

CMD ["python", "monitor_service.py"]