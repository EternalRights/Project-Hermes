# Project Hermes - High-Performance API Automation Testing Platform

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/yourusername/project-hermes)
[![Docker](https://img.shields.io/badge/docker-supported-blue)](https://www.docker.com/)

## Overview

Project Hermes is a high-performance API automation testing platform designed to address complex API testing challenges in microservice architectures. Through visual management, distributed execution, and intelligent parameterization, the platform significantly improves testing efficiency and system stability.

### Background

In microservice architectures with 500+ APIs, teams face challenges such as complex test environments, deep API dependencies, and regression tests taking up to 6 hours. Project Hermes aims to solve these problems by providing an integrated API testing solution.

### Core Features

- **High-Performance Distributed Execution** - Multi-node parallel execution for improved testing efficiency
- **Visual Case Management** - Intuitive web interface for managing test cases
- **Full-Link Tracing** - TraceID injection for performance bottleneck identification
- **Intelligent Rate Limiting and Circuit Breaking** - Protects the system under test from overload
- **Containerized Environment** - Docker one-click deployment with environment isolation
- **Real-time Monitoring and Alerting** - Prometheus integration for real-time metric monitoring

## System Architecture

<img width="1739" height="1268" alt="System Architecture" src="https://github.com/user-attachments/assets/a531a767-6872-4fa9-aeae-c6741052cc41" />

## Project Results

- **Regression Test Duration**: From 6 hours to 15 minutes (24x improvement)
- **System Throughput**: From 500 QPS to 3000 QPS (6x improvement)
- **API Response Time**: From 2.5s to 1.5s (40% improvement)
- **Team Collaboration**: Shift-left testing enabled, lowering barriers for non-technical team members

## Directory Structure

```
project-hermes/
├── hermes-web/              # Frontend management platform (Vue.js + Element UI)
│   ├── src/
│   ├── public/
│   └── package.json
├── hermes-server/           # Backend API service (Flask/FastAPI)
│   ├── app/
│   ├── config/
│   └── requirements.txt
├── hermes-core/             # Core engine module
│   ├── scheduler/
│   ├── executor/
│   └── utils/
├── hermes-worker/           # Distributed execution node
│   ├── worker.py
│   └── task_handler.py
├── docker/                  # Docker configuration
│   ├── Dockerfile
│   └── docker-compose.yml
├── docs/                    # Project documentation
│   ├── api.md
│   └── deployment.md
├── tests/                   # Test cases
├── scripts/                 # Deployment scripts
└── README.md
```

## Technology Stack

### Backend
- **Python**: Flask/FastAPI, Celery, Redis, MySQL
- **Testing Framework**: Pytest, Requests
- **Task Queue**: Celery + Redis
- **Data Storage**: MySQL (primary data), Redis (cache)

### Frontend
- **Vue.js**: 2.x/3.x + Element UI
- **Build Tools**: Webpack, npm/yarn
- **UI Components**: Element UI

### Containerization and DevOps
- **Docker**: Containerized deployment
- **Docker-Compose**: Multi-service orchestration
- **Nginx**: Reverse proxy
- **Prometheus**: Metric collection
- **Grafana**: Monitoring visualization

### Performance Testing
- **JMeter**: High-performance load testing
- **Custom Load Testing Engine**: Lightweight Python-based load testing

## Quick Start

### Requirements
- Docker >= 19.03
- Docker Compose >= 1.25
- Python >= 3.8
- Node.js >= 14.0

### Local Deployment

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/project-hermes.git
cd project-hermes
```

2. **Start Docker environment**
```bash
cd docker
docker-compose up -d
```

3. **Start backend service**
```bash
cd hermes-server
pip install -r requirements.txt
python app.py
```

4. **Start frontend service**
```bash
cd hermes-web
npm install
npm run serve
```

5. **Access the platform**

Web Management Platform: http://localhost:8080
API Documentation: http://localhost:5000/docs
Monitoring Dashboard: http://localhost:3000

6. **Docker one-click deployment**

```bash
# Build and start all services
docker-compose -f docker/docker-compose.yml up -d

# View service status
docker-compose -f docker/docker-compose.yml ps

# Stop all services
docker-compose -f docker/docker-compose.yml down
```

## Contributing

Issues and Pull Requests are welcome!
