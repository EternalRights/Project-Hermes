# Iteration v2 - Critical Fixes and Core Feature Completion Spec

## Why
Project Hermes 经历大规模重构和测试补充后，通过深度代码审查发现了多个阻塞性问题（Docker健康检查缺失导致容器无法启动、Celery任务参数不匹配导致执行功能不可用、前后端登录字段不匹配导致登录失败）和严重安全漏洞（exec()注入、XSS存储型漏洞、硬编码密钥）。同时，调度器模块为空、权限装饰器未使用、输入验证缺失等核心功能短板也必须补齐，否则平台无法达到生产可用状态。

## What Changes
- 修复 Docker 健康检查端点缺失（新增 /api/v1/health）
- 修复 Celery 任务参数不匹配和配置错误
- 修复前后端登录字段名不匹配
- 修复报告导出 XSS 存储型漏洞
- 加固 exec() 沙箱安全（AST白名单+超时控制）
- 替换硬编码默认密钥为启动时强制检查
- 实现 /auth/me 端点
- 实现 Dashboard 统计 API
- 实现调度器核心模块（cron解析+下次执行时间计算+Celery Beat配置）
- 实现邮件通知功能
- 为所有 API 端点添加输入验证（marshmallow schema）
- 为所有 API 端点添加权限装饰器
- 修复 datetime.utcnow() 弃用（37处 → datetime.now(timezone.utc)）
- 修复 SQLAlchemy Query.get() 弃用（39处 → db.session.get()）
- 统一 API 响应格式
- 添加数据库迁移初始化
- 修复 Dockerfile 和 docker-compose 配置
- 更新 README 使其与实际代码一致

## Impact
- Affected specs: hermes-core (scheduler, executor/hooks), hermes-server (all API endpoints, models, config, middleware), hermes-worker (tasks, celery config), hermes-web (auth store, API calls), docker (Dockerfile, docker-compose)
- Affected code: 几乎所有模块均有改动

## ADDED Requirements

### Requirement: Health Check Endpoint
The system SHALL provide a /api/v1/health endpoint that returns system status.

#### Scenario: Health check returns OK
- **WHEN** GET /api/v1/health is called
- **THEN** it SHALL return 200 with JSON {"status": "healthy", "version": "1.0.0", "database": "connected"}

#### Scenario: Database unavailable
- **WHEN** GET /api/v1/health is called and database is unreachable
- **THEN** it SHALL return 503 with JSON {"status": "unhealthy", "database": "disconnected"}

### Requirement: Celery Task Dispatch Fix
The system SHALL correctly dispatch Celery tasks with matching parameters.

#### Scenario: Create execution dispatches task correctly
- **WHEN** POST /api/v1/executions creates a new execution
- **THEN** it SHALL dispatch execute_test_suite with args=[execution_id, suite_id, environment_id] using the shared celery_app

### Requirement: Frontend-Backend Auth Field Alignment
The system SHALL return auth tokens in a format the frontend expects.

#### Scenario: Login response field names
- **WHEN** POST /api/v1/auth/login succeeds
- **THEN** it SHALL return both snake_case (access_token, refresh_token) and camelCase (token, refreshToken) field names for backward compatibility

### Requirement: XSS Prevention in Report Export
The system SHALL escape HTML in report export.

#### Scenario: Export report with XSS in case name
- **WHEN** a test case name contains HTML tags and report is exported as HTML
- **THEN** the tags SHALL be HTML-escaped (e.g., &lt;script&gt; instead of <script>)

### Requirement: exec() Sandbox Hardening
The system SHALL restrict exec() in hook scripts with AST validation and timeout.

#### Scenario: Dangerous AST node in hook script
- **WHEN** a hook script contains Import, ImportFrom, or Attribute AST nodes accessing __globals__, __code__, etc.
- **THEN** the script SHALL be rejected with a ValueError

#### Scenario: Hook script execution timeout
- **WHEN** a hook script runs longer than the configured timeout (default 30s)
- **THEN** the script SHALL be terminated and a TimeoutError recorded in context.errors

### Requirement: Secret Key Enforcement
The system SHALL refuse to start with default/insecure secret keys in production.

#### Scenario: Production mode with default key
- **WHEN** FLASK_ENV=production and SECRET_KEY equals the default value
- **THEN** the application SHALL raise a RuntimeError and refuse to start

### Requirement: Auth Me Endpoint
The system SHALL provide /api/v1/auth/me to get current user info.

#### Scenario: Get current user info
- **WHEN** GET /api/v1/auth/me is called with a valid JWT
- **THEN** it SHALL return the user's id, username, email, and roles

### Requirement: Dashboard Statistics API
The system SHALL provide /api/v1/dashboard/stats for dashboard data.

#### Scenario: Get dashboard stats
- **WHEN** GET /api/v1/dashboard/stats is called
- **THEN** it SHALL return todayExecutions, passRate, activeCases, activeSuites, recentExecutions

### Requirement: Scheduler Core Module
The system SHALL implement cron expression parsing and next run time calculation.

#### Scenario: Parse cron expression
- **WHEN** CronParser.parse("*/5 * * * *") is called
- **THEN** it SHALL return the next execution datetime after the current time

#### Scenario: Invalid cron expression
- **WHEN** CronParser.parse("invalid") is called
- **THEN** it SHALL raise ValueError

### Requirement: Email Notification Implementation
The system SHALL implement email notification sending.

#### Scenario: Send email notification
- **WHEN** an email notification is triggered with SMTP config
- **THEN** it SHALL connect to SMTP server, authenticate, and send the email

### Requirement: Input Validation with Marshmallow
The system SHALL validate all API request bodies using marshmallow schemas.

#### Scenario: Create project with missing name
- **WHEN** POST /api/v1/projects is called without name field
- **THEN** it SHALL return 400 with validation error details

#### Scenario: Create test case with invalid priority
- **WHEN** POST /api/v1/test-cases is called with priority not in [P0, P1, P2, P3]
- **THEN** it SHALL return 400 with validation error details

### Requirement: Permission Decorator Applied to All APIs
The system SHALL enforce permission checks on all API endpoints.

#### Scenario: User without permission creates project
- **WHEN** a user without project:create permission calls POST /api/v1/projects
- **THEN** it SHALL return 403

### Requirement: datetime.utcnow() Migration
The system SHALL use datetime.now(timezone.utc) instead of datetime.utcnow().

#### Scenario: All datetime calls use timezone-aware UTC
- **WHEN** any model or service creates a datetime
- **THEN** it SHALL use datetime.now(timezone.utc) and store timezone-aware datetimes

### Requirement: SQLAlchemy Query.get() Migration
The system SHALL use db.session.get(Model, id) instead of Model.query.get(id).

#### Scenario: All model lookups use new API
- **WHEN** any API endpoint retrieves a model by primary key
- **THEN** it SHALL use db.session.get(Model, id) pattern

### Requirement: Unified API Response Format
The system SHALL return consistent JSON response format across all endpoints.

#### Scenario: All successful responses
- **WHEN** any API endpoint returns a successful response
- **THEN** it SHALL use jsonify(success_response(...)) format with code, message, data keys

### Requirement: Database Migration Initialization
The system SHALL support Flask-Migrate for schema management.

#### Scenario: Initialize migrations
- **WHEN** flask db init && flask db migrate is run
- **THEN** it SHALL create migrations/ directory with initial migration

### Requirement: Docker Configuration Fix
The system SHALL have correct Dockerfile and docker-compose configuration.

#### Scenario: Server Dockerfile uses correct WSGI entry point
- **WHEN** the server Docker image is built and run
- **THEN** Gunicorn SHALL correctly load the Flask application factory

#### Scenario: docker-compose includes Celery Beat
- **WHEN** docker-compose up is run
- **THEN** a Celery Beat container SHALL be started for scheduled task dispatch

### Requirement: README Accuracy
The system SHALL have a README that matches the actual codebase.

#### Scenario: README references correct file paths
- **WHEN** README mentions a file path or command
- **THEN** it SHALL match the actual project structure

## MODIFIED Requirements
(None - all changes are additions or bug fixes)

## REMOVED Requirements
(None)
