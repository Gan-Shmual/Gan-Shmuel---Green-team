# 💰 Billing Team

## How to run this project:

```bash
pip install -r requirements.txt
flask --app flaskr run --debug
```

## Run using Docker:

```bash
docker-compose up --build
```
You should use virtual environment for installing dependencies.

this is a flask app for chatting. it is currently under development.

We're building: The payment system that generates invoices for fruit producers.

Core responsibilities:

   - Manage producers and their registered trucks
   - Upload and manage pricing rates
   - Generate accurate invoices using Weight data
   - Track payment history
  
Billing Team:

✅ GET /health
✅ POST /provider
✅ PUT /provider/<id>