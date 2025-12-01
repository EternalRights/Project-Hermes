# Project Hermes - 高性能接口自动化测试平台

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/yourusername/project-hermes)
[![Docker](https://img.shields.io/badge/docker-supported-blue)](https://www.docker.com/)

## 项目简介

Project Hermes 是一个高性能的接口自动化测试平台，专为解决微服务架构下复杂的接口测试挑战而设计。该平台通过可视化管理、分布式执行、智能参数化等技术手段，显著提升了测试效率和系统稳定性。

### 项目背景
在微服务架构下，系统包含500+个接口，面临测试环境复杂、接口依赖深、回归测试耗时长达6小时等典型工程难题。Project Hermes旨在解决这些问题，提供一体化的接口测试解决方案。

### 核心特性
- 🚀 **高性能分布式执行** - 支持多节点并行执行，大幅提升测试效率
- 🎨 **可视化用例管理** - 提供直观的Web界面管理测试用例
- 📊 **全链路追踪** - 注入TraceID，便于定位性能瓶颈
- 🛡️ **智能限流熔断** - 保护被测系统，防止压测过载
- 🐳 **容器化环境** - Docker一键部署，环境隔离
- 📈 **实时监控告警** - 集成Prometheus，实时监控关键指标

## 系统架构

<img width="1739" height="1268" alt="exported_image" src="https://github.com/user-attachments/assets/a531a767-6872-4fa9-aeae-c6741052cc41" />

## 项目成果

- ✅ **回归测试时间**：从6小时 → 15分钟 (性能提升24倍)
- ✅ **系统吞吐量**：从500 QPS → 3000 QPS (性能提升6倍)  
- ✅ **接口响应时间**：从2.5秒 → 1.5秒 (性能提升40%)
- ✅ **团队协作效率**：促进测试左移，降低非技术人员参与门槛

## 目录结构

project-hermes/

├── hermes-web/              # 前端管理平台 (Vue.js + Element UI)

│   ├── src/

│   ├── public/

│   └── package.json

├── hermes-server/           # 后端API服务 (Flask/FastAPI)

│   ├── app/

│   ├── config/

│   └── requirements.txt

├── hermes-core/             # 核心引擎模块

│   ├── scheduler/

│   ├── executor/

│   └── utils/

├── hermes-worker/           # 分布式执行节点

│   ├── worker.py

│   └── task_handler.py

├── docker/                  # Docker相关配置

│   ├── Dockerfile

│   └── docker-compose.yml

├── docs/                    # 项目文档

│   ├── api.md

│   └── deployment.md

├── tests/                   # 测试用例

├── scripts/                 # 部署脚本

└── README.md




## 技术栈

### 后端技术
- **Python**: Flask/FastAPI, Celery, Redis, MySQL
- **测试框架**: Pytest, Requests
- **任务队列**: Celery + Redis
- **数据存储**: MySQL (主数据), Redis (缓存)

### 前端技术
- **Vue.js**: 2.x/3.x + Element UI
- **构建工具**: Webpack, npm/yarn
- **UI组件**: Element UI

### 容器化与运维
- **Docker**: 容器化部署
- **Docker-Compose**: 多服务编排
- **Nginx**: 反向代理
- **Prometheus**: 监控指标收集
- **Grafana**: 监控可视化

### 性能测试
- **JMeter**: 高性能压测
- **自定义压测引擎**: Python实现的轻量级压测

## 快速开始

### 环境要求
- Docker >= 19.03
- Docker Compose >= 1.25
- Python >= 3.8
- Node.js >= 14.0

### 本地部署

1. **克隆项目**
```bash
git clone https://github.com/yourusername/project-hermes.git
cd project-hermes
```

2. **启动Docker环境**
```bash
cd docker
docker-compose up -d
```

3. **启动后端服务**
```bash
cd hermes-server
pip install -r requirements.txt
python app.py
```
4. **启动前端服务**
```
cd hermes-web
npm install
npm run serve
```

5. **访问平台**

Web管理平台: http://localhost:8080
API文档: http://localhost:5000/docs
监控面板: http://localhost:3000

6. **Docker一键部署**

```bash
# 构建并启动所有服务
docker-compose -f docker/docker-compose.yml up -d

# 查看服务状态
docker-compose -f docker/docker-compose.yml ps

# 停止所有服务
docker-compose -f docker/docker-compose.yml down
```
