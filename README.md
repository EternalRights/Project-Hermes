# Project Hermes - High-Performance API Automation Testing Platform

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/yourusername/project-hermes)
[![Docker](https://img.shields.io/badge/docker-supported-blue)](https://www.docker.com/)

## Overview

Project Hermes is a high-performance API automation testing platform designed to address complex API testing challenges in microservice architectures. Through visual management, distributed execution, and intelligent parameterization, the platform significantly improves testing efficiency and system stability.

### Background

In microservice architectures with 500+ APIs, teams face challenges such as complex test environments, deep API dependencies, and regression tests taking up to 6 hours. Project Hermes aims to solve these problems by providing an integrated API testing solution.

### Core Features

- **High-Performance Distributed Execution** - Multi-node parallel execution with Celery
- **Visual Case Management** - Vue 3 web interface with Element Plus
- **Full-Link Tracing** - TraceID injection for performance bottleneck identification
- **Intelligent Rate Limiting and Circuit Breaking** - Protects the system under test from overload
- **Containerized Environment** - Docker one-click deployment with environment isolation
- **Real-time Monitoring and Alerting** - Prometheus integration for real-time metric monitoring
- **Scheduled Test Execution** - Cron-based scheduling with Celery Beat
- **Multi-Notification Channels** - Webhook and Email notifications

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        hermes-web (Vue 3)                        │
│                    Frontend Management Platform                  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      hermes-server (Flask)                       │
│                         Backend API Service                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │  Auth    │ │ Projects │ │  Tests   │ │ Reports  │           │
│  │  (JWT)   │ │          │ │          │ │          │           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
└─────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────────────────┐
│   MySQL     │    │    Redis    │    │     hermes-worker       │
│  (Storage)  │    │   (Cache)   │    │   (Celery Workers)      │
└─────────────┘    └─────────────┘    │  ┌─────────────────┐   │
                                      │  │ execute_test_*  │   │
                                      │  │ heartbeat       │   │
                                      │  └─────────────────┘   │
                                      └─────────────────────────┘
```

## Project Results

- **Regression Test Duration**: From 6 hours to 15 minutes (24x improvement)
- **System Throughput**: From 500 QPS to 3000 QPS (6x improvement)
- **API Response Time**: From 2.5s to 1.5s (40% improvement)
- **Team Collaboration**: Shift-left testing enabled, lowering barriers for non-technical team members

## Directory Structure

```
project-hermes/
├── hermes-web/               # Frontend management platform (Vue 3 + Element Plus)
│   ├── src/
│   ├── public/
│   └── package.json
├── hermes-server/            # Backend API service (Flask)
│   ├── api/                  # API endpoints
│   ├── app/                  # Application factory
│   ├── config/               # Configuration
│   ├── middleware/           # Auth, permissions, logging
│   ├── models/               # SQLAlchemy models
│   ├── schemas/              # Marshmallow validation schemas
│   ├── services/             # Business logic layer
│   ├── migrations/           # Database migrations
│   ├── requirements.txt
│   └── run.py                # Application entry point
├── hermes-core/              # Core engine module
│   ├── assertions/           # Assertion engine
│   ├── executor/             # Test case runner
│   ├── parametrize/          # Parameterization engine
│   ├── scheduler/            # Cron parser and scheduler
│   ├── tracing/              # Distributed tracing
│   └── utils/                # Utilities (rate limiter, circuit breaker)
├── hermes-worker/            # Distributed execution node
│   ├── tasks/                # Celery tasks
│   ├── celery_app.py         # Celery configuration
│   └── config.py             # Worker configuration
├── tests/                    # Test suite
│   ├── test_core/            # Core module tests
│   ├── test_server/          # API integration tests
│   ├── test_worker/          # Worker task tests
│   ├── test_integration/     # Cross-module integration tests
│   ├── test_security/        # Security tests
│   └── test_concurrency/     # Concurrency tests
├── docker-compose.yml        # Docker orchestration
├── .env.example              # Environment variables template
└── README.md
```

## Technology Stack

### Backend
- **Python**: Flask, Celery, Redis, MySQL
- **Testing Framework**: Pytest
- **Task Queue**: Celery + Redis
- **Data Storage**: MySQL (primary data), Redis (cache)
- **Authentication**: JWT with Flask-JWT-Extended
- **Validation**: Marshmallow schemas

### Frontend
- **Vue.js**: 3.x + Composition API
- **Build Tools**: Vite
- **UI Components**: Element Plus
- **State Management**: Pinia

### Containerization and DevOps
- **Docker**: Containerized deployment
- **Docker-Compose**: Multi-service orchestration
- **Nginx**: Reverse proxy
- **Prometheus**: Metric collection
- **Grafana**: Monitoring visualization

## Quick Start

### Requirements
- Docker >= 19.03
- Docker Compose >= 1.25
- Python >= 3.11
- Node.js >= 18.0

### Docker Deployment (Recommended)

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/project-hermes.git
cd project-hermes
```

2. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start all services**
```bash
docker-compose up -d
```

4. **Access the platform**

- Web Management Platform: http://localhost:8080
- API Health Check: http://localhost:5000/api/v1/health
- Monitoring Dashboard (Grafana): http://localhost:3000
- Prometheus: http://localhost:9090

### Local Development

1. **Backend setup**
```bash
cd hermes-server
pip install -r requirements.txt
python run.py
```

2. **Frontend setup**
```bash
cd hermes-web
npm install
npm run dev
```

3. **Worker setup**
```bash
cd hermes-worker
pip install -r requirements.txt
celery -A hermes_worker.celery_app worker --loglevel=info
```

4. **Beat scheduler (for scheduled tasks)**
```bash
celery -A hermes_worker.celery_app beat --loglevel=info
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=hermes_core --cov=hermes_server --cov-report=html
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/auth/login` | User login |
| `POST /api/v1/auth/register` | User registration |
| `GET /api/v1/auth/me` | Get current user info |
| `GET /api/v1/projects` | List projects |
| `POST /api/v1/projects` | Create project |
| `GET /api/v1/test-cases` | List test cases |
| `POST /api/v1/test-cases` | Create test case |
| `GET /api/v1/test-suites` | List test suites |
| `POST /api/v1/executions` | Create execution |
| `GET /api/v1/dashboard/stats` | Dashboard statistics |
| `GET /api/v1/health` | Health check |

## Default Credentials

After running the seed script:
- Username: `admin`
- Password: `admin123`

**Important**: Change the default password immediately in production!

## Contributing

Issues and Pull Requests are welcome!

## License

MIT License
