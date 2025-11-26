# Gan Shmuel - Green Team

A comprehensive fruit production management system with automated CI/CD pipeline for tracking truck weighing operations and billing.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Services](#services)
- [CI/CD Pipeline](#cicd-pipeline)
- [Getting Started](#getting-started)
- [Development](#development)
- [Deployment](#deployment)
- [Testing](#testing)
- [Contributing](#contributing)

## Overview

Gan Shmuel is a microservices-based system designed to manage the complete lifecycle of fruit production operations, from weighing trucks and containers to generating accurate invoices for producers.

### Key Features

- **Real-time Weight Tracking**: Monitor truck and container weights with session-based tracking
- **Automated Billing**: Generate invoices based on weight data and pricing rates
- **Service Monitoring**: Track health and status of all microservices
- **Automated CI/CD**: Complete pipeline from code commit to production deployment
- **Docker-based Deployment**: Containerized services for easy scaling and deployment

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Load Balancer / Monitor                   │
│                         (Port 8085)                          │
└────────────────┬────────────────────────┬───────────────────┘
                 │                        │
        ┌────────▼────────┐      ┌───────▼────────┐
        │ Weight Service  │      │ Billing Service │
        │   (Port 8082)   │◄─────┤   (Port 8081)   │
        └────────┬────────┘      └───────┬─────────┘
                 │                       │
        ┌────────▼────────┐      ┌───────▼─────────┐
        │   Weight DB     │      │   Billing DB    │
        │  MySQL (3309)   │      │  MySQL (3307)   │
        └─────────────────┘      └─────────────────┘

                    ┌──────────────────┐
                    │   DevOps CI/CD   │
                    │   (Port 8080)    │
                    └──────────────────┘
```

## Services

### 1. Weight Service (Port 8082)

Manages weighing operations for trucks and containers.

**Key Endpoints:**
- `POST /weight` - Record weight transaction
- `GET /weight` - Query weight history
- `GET /session/<id>` - Get session details
- `GET /item/<id>` - Get truck/container history
- `POST /batch-weight` - Bulk upload container weights

**Database:** MySQL (Port 3309)

[Full API Documentation →](./weight-service/README.md)

### 2. Billing Service (Port 8081)

Handles producer management, pricing, and invoice generation.

**Key Endpoints:**
- `POST /provider` - Register producer
- `POST /truck` - Register truck
- `POST /rates` - Upload pricing rates
- `GET /bill` - Generate invoice

**Database:** MySQL (Port 3307)

[Full API Documentation →](./billing-service/README.md)

### 3. Monitor Service (Port 8085)

Provides health monitoring and status tracking for all services.

**Features:**
- Service health checks
- Status dashboard
- Uptime monitoring

### 4. DevOps CI/CD (Port 8080)

Automated continuous integration and deployment pipeline.

**Features:**
- GitHub webhook integration
- Automated unit and integration testing
- Auto-merge to main branch
- Production deployment
- Email notifications

## CI/CD Pipeline

The project includes a fully automated CI/CD pipeline that triggers on pushes to the `development` branch.

### Pipeline Flow

```
Push to Development
    ↓
Unit Tests
    ↓
Integration Tests
    ↓
Create Pull Request (development → main)
    ↓
Auto-Merge PR
    ↓
Deploy to Production
    ↓
Send Notification Email
```

### Webhook Setup

Configure GitHub webhook:
- **URL:** `http://your-server:8080/webhook`
- **Content type:** `application/json`
- **Events:** Push events
- **Secret:** Set in `.env` as `GITHUB_WEBHOOK_SECRET`

### Manual Trigger

```bash
curl -X POST http://localhost:8080/trigger
```

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git
- GitHub account (for CI/CD)
- Gmail account (for notifications)

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/Gan-Shmual/Gan-Shmuel---Green-team.git
cd Gan-Shmuel---Green-team
```

2. **Create `.env` file**

```bash
# GitHub Configuration
GITHUB_WEBHOOK_SECRET=your-webhook-secret
GITHUB_TOKEN=your-github-token

# Email Configuration
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password
TEAM_EMAILS=email1@example.com,email2@example.com

# Billing Database
BILLING_DB_HOST=db
BILLING_DB_USER=root
BILLING_DB_NAME=billdb
BILLING_DB_PASSWORD=your-password
BILLING_DB_PORT=3307
APP_PORT=5001

# Weight Database
DB_HOST=weight-db
DB_USER=root
DB_PASSWORD=root
DB_NAME=weight
DB_PORT=3306
MYSQL_HOST=weight-db
MYSQL_ROOT_PASSWORD=root
MYSQL_DATABASE=weight
MYSQL_PASSWORD=root
MYSQL_PORT=3306

# Service Configuration
WEIGHTS_PORT=5000
WEIGHTS_HOST=weight-service
```

3. **Start the CI/CD Pipeline**

```bash
docker compose -f docker-compose.ci.yml up -d --build
```

4. **Start Production Services**

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

## Development

### Running Tests Locally

**Integration Tests:**
```bash
docker compose -f docker-compose.tests.yml up --build
```

**Unit Tests:**
```bash
# Weight service
cd weight-service
pytest

# Billing service
cd billing-service
pytest
```

### Project Structure

```
.
├── billing-service/       # Billing microservice
├── weight-service/        # Weight tracking microservice
├── monitor/               # Monitoring service
├── devops/               # CI/CD scripts and configuration
├── tests/                # Integration tests
├── docker-compose.ci.yml      # CI/CD pipeline configuration
├── docker-compose.prod.yml    # Production deployment
├── docker-compose.tests.yml   # Testing environment
└── .env                  # Environment variables (not in git)
```

### Environment Variables

All services use environment variables for configuration. Required variables:

**CI/CD:**
- `GITHUB_TOKEN` - GitHub personal access token
- `GITHUB_WEBHOOK_SECRET` - Webhook secret key
- `GMAIL_USER` - Email for notifications
- `GMAIL_APP_PASSWORD` - Gmail app password
- `TEAM_EMAILS` - Comma-separated list of notification recipients

**Databases:**
- `BILLING_DB_*` - Billing database credentials
- `DB_*` / `MYSQL_*` - Weight database credentials

## Deployment

### Production Deployment

The CI/CD pipeline automatically deploys to production after successful tests and PR merge.

**Manual deployment:**
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

### Scaling Services

Scale individual services:
```bash
docker compose -f docker-compose.prod.yml up -d --scale weight-service=3
```

### Monitoring

Access the monitor dashboard:
```
http://localhost:8085
```

Check service health:
```bash
# Weight service
curl http://localhost:8082/health

# Billing service
curl http://localhost:8081/health
```

## Testing

### Test Structure

```
tests/
├── test_service.py        # Integration tests
└── init.sh               # Test initialization script
```

### Running Tests

**Full integration test suite:**
```bash
docker compose -f docker-compose.tests.yml up --build
```

**View test results:**
```bash
docker compose -f docker-compose.tests.yml logs test-runner
```

### CI Test Flow

1. **Unit Tests** - Individual service tests
2. **Integration Tests** - Service interaction tests
3. **Health Checks** - Service availability verification

## Portability

The system is fully portable and can run on any machine with Docker installed.

**No configuration changes needed when moving to a new computer:**
- All paths use `${PWD}` (automatically resolved)
- Configuration via `.env` file
- Docker handles all dependencies

**To migrate:**
1. Clone the repository
2. Copy your `.env` file
3. Run `docker compose up`

## Contributing

### Branching Strategy

- `main` - Production branch
- `development` - Integration branch
- `feature/*` - Feature branches
- `dev/*` - Development branches

### Pull Request Process

1. Create feature branch from `development`
2. Make changes and commit
3. Push to `development` branch
4. CI pipeline runs automatically
5. Tests must pass before merge
6. Auto-merge to `main` after approval

### Commit Guidelines

- Use descriptive commit messages
- Reference issue numbers when applicable
- Keep commits focused and atomic

## Troubleshooting

### Common Issues

**Docker Socket Permission Denied:**
```bash
sudo chmod 666 /var/run/docker.sock
```

**Database Connection Failed:**
- Check `.env` file has correct credentials
- Ensure database containers are healthy: `docker ps`
- Check logs: `docker logs <container-name>`

**CI Pipeline Failing:**
- Check GitHub token permissions
- Verify webhook secret matches
- Review logs: `docker logs devops-ci`

**Tests Failing:**
- Ensure all containers are running
- Check database initialization
- Review test logs: `docker compose -f docker-compose.tests.yml logs`

## License

This project is developed as part of the Gan Shmuel bootcamp program.

## Team

Green Team - Gan Shmuel Bootcamp

## Support

For issues and questions:
- Create an issue on GitHub
- Contact team via email (configured in `TEAM_EMAILS`)
