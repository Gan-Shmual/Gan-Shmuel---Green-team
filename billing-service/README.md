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
  
Billing APIs:

✅ GET /health
✅ POST /provider
✅ PUT /provider/<id>
✅ POST /truck
✅ PUT /truck/<id>
✅ GET /truck/<id>
✅ POST /rates
✅ GET /rates
✅ GET /bill

Dependencies:
GET /truck/<id> and GET /bill depend on weight-service
