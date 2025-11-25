FROM python:3.12-slim

WORKDIR /app


RUN apt-get update && \
    apt-get install -y git docker.io docker-compose curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ci_service.py .
COPY ci_pipeline.sh .
COPY run_unit_tests.sh .
COPY run_integartion_tests.sh .
COPY deploy.sh .
COPY rollback.sh .
COPY send_email.py .
COPY github_api.py .

RUN chmod +x ci_pipeline.sh run_unit_tests.sh run_integartion_tests.sh deploy.sh rollback.sh

CMD ["python", "ci_service.py"]
