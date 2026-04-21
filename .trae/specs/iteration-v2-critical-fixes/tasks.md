# Tasks

- [ ] Task 1: Fix Docker health check - Add /api/v1/health endpoint
  - [ ] SubTask 1.1: Create hermes-server/api/v1/health.py with health check endpoint (database connectivity check, version info)
  - [ ] SubTask 1.2: Register health blueprint in hermes-server/api/v1/__init__.py
  - [ ] SubTask 1.3: Verify docker-compose healthcheck command matches the new endpoint

- [ ] Task 2: Fix Celery task dispatch
  - [ ] SubTask 2.1: Fix hermes-server/api/v1/executions.py - use shared celery_app instead of creating new Celery(), pass all 3 args (execution_id, suite_id, environment_id)
  - [ ] SubTask 2.2: Verify task signature matches between dispatch and worker

- [ ] Task 3: Fix frontend-backend auth field alignment
  - [ ] SubTask 3.1: Update hermes-server/api/v1/auth.py login response to include both snake_case and camelCase field names
  - [ ] SubTask 3.2: Fix hermes-web/src/api/auth.js refresh token request to use Authorization header instead of body

- [ ] Task 4: Fix XSS in report export
  - [ ] SubTask 4.1: Add html_escape utility function to hermes-core/utils/
  - [ ] SubTask 4.2: Update hermes-server/api/v1/reports.py export_html to escape all user-provided strings

- [ ] Task 5: Harden exec() sandbox in hooks
  - [ ] SubTask 5.1: Add AST validator to hermes-core/executor/hooks.py that rejects Import, ImportFrom, and dangerous Attribute nodes
  - [ ] SubTask 5.2: Add execution timeout (default 30s) using signal or threading.Timer
  - [ ] SubTask 5.3: Add tests for AST validation and timeout

- [ ] Task 6: Enforce secret key security
  - [ ] SubTask 6.1: Update hermes-server/config/config.py to check FLASK_ENV and raise RuntimeError if default key used in production
  - [ ] SubTask 6.2: Update seed.py to warn about default admin password

- [ ] Task 7: Implement /auth/me endpoint
  - [ ] SubTask 7.1: Add GET /api/v1/auth/me endpoint returning current user info (id, username, email, roles)

- [ ] Task 8: Implement Dashboard statistics API
  - [ ] SubTask 8.1: Create hermes-server/api/v1/dashboard.py with /api/v1/dashboard/stats endpoint
  - [ ] SubTask 8.2: Register dashboard blueprint in __init__.py

- [ ] Task 9: Implement scheduler core module
  - [ ] SubTask 9.1: Create hermes-core/scheduler/cron_parser.py with CronParser class (parse cron expression, calculate next run time)
  - [ ] SubTask 9.2: Create hermes-core/scheduler/scheduler.py with Scheduler class (update next_run_at for ScheduledTask)
  - [ ] SubTask 9.3: Add Celery Beat schedule configuration in hermes-worker/celery_app.py
  - [ ] SubTask 9.4: Add tests for CronParser

- [ ] Task 10: Implement email notification
  - [ ] SubTask 10.1: Replace pass in hermes-worker/tasks/test_execution.py email notification with actual SMTP sending logic
  - [ ] SubTask 10.2: Add email template for test execution results

- [ ] Task 11: Add marshmallow input validation schemas
  - [ ] SubTask 11.1: Create hermes-server/schemas/ directory with validation schemas for all models (ProjectSchema, TestCaseSchema, TestSuiteSchema, EnvironmentSchema, VariableSchema, ExecutionSchema, ScheduledTaskSchema, NotificationSchema)
  - [ ] SubTask 11.2: Apply schemas to all API endpoints for request validation

- [ ] Task 12: Apply permission decorators to all API endpoints
  - [ ] SubTask 12.1: Add require_permission decorators to all API endpoint functions with appropriate permission names

- [ ] Task 13: Fix datetime.utcnow() deprecation (37 occurrences)
  - [ ] SubTask 13.1: Replace all datetime.utcnow() with datetime.now(timezone.utc) in hermes-server/models/
  - [ ] SubTask 13.2: Replace all datetime.utcnow() with datetime.now(timezone.utc) in hermes-server/api/
  - [ ] SubTask 13.3: Replace all datetime.utcnow() with datetime.now(timezone.utc) in hermes-worker/tasks/

- [ ] Task 14: Fix SQLAlchemy Query.get() deprecation (39 occurrences)
  - [ ] SubTask 14.1: Replace Model.query.get(id) with db.session.get(Model, id) in all API files

- [ ] Task 15: Unify API response format
  - [ ] SubTask 15.1: Ensure all API endpoints use consistent jsonify(success_response(...)) pattern

- [ ] Task 16: Initialize database migrations
  - [ ] SubTask 16.1: Add Flask-Migrate initialization in hermes-server/app/__init__.py
  - [ ] SubTask 16.2: Create migrations/ directory structure

- [ ] Task 17: Fix Docker configuration
  - [ ] SubTask 17.1: Fix hermes-server/Dockerfile Gunicorn entry point
  - [ ] SubTask 17.2: Add Celery Beat service to docker-compose.yml
  - [ ] SubTask 17.3: Add database initialization step to docker-compose.yml

- [ ] Task 18: Update README for accuracy
  - [ ] SubTask 18.1: Fix file paths, technology references, and commands to match actual codebase

- [ ] Task 19: Add tests for all new features
  - [ ] SubTask 19.1: Add tests for health endpoint, auth/me, dashboard stats
  - [ ] SubTask 19.2: Add tests for scheduler/cron_parser
  - [ ] SubTask 19.3: Add tests for input validation schemas
  - [ ] SubTask 19.4: Add tests for exec() sandbox hardening
  - [ ] SubTask 19.5: Run full test suite and verify all pass

# Task Dependencies
- Task 1 (health endpoint) - no dependencies
- Task 2 (Celery fix) - no dependencies
- Task 3 (auth field fix) - no dependencies
- Task 4 (XSS fix) - no dependencies
- Task 5 (exec sandbox) - no dependencies
- Task 6 (secret key) - no dependencies
- Task 7 (auth/me) - depends on Task 3 (auth module being touched)
- Task 8 (dashboard) - no dependencies
- Task 9 (scheduler) - no dependencies
- Task 10 (email notification) - no dependencies
- Task 11 (input validation) - no dependencies
- Task 12 (permission decorators) - depends on Task 11 (schemas applied first)
- Task 13 (datetime fix) - no dependencies, can run in parallel
- Task 14 (Query.get fix) - no dependencies, can run in parallel
- Task 15 (response format) - no dependencies
- Task 16 (migrations) - no dependencies
- Task 17 (Docker fix) - depends on Task 1 (health endpoint) and Task 9 (Celery Beat)
- Task 18 (README) - depends on all other tasks being complete
- Task 19 (tests) - depends on Tasks 1-10 being complete
