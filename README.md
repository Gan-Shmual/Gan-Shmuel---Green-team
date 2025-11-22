Gan-Shmuel-Green-Team/   (Root of Repo)
│
├── docker-compose.yml   (Orchestrates everyone)
├── .gitignore           (Ignores __pycache__, .env, venv)
├── README.md            (Instructions on how to run)
│
├── health-api/          (Microservice 1)
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
│
├── weight-api/          (Microservice 2)
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
│
└── db/                  (Database Setup)
    └── init.sql         (Schema creation)
