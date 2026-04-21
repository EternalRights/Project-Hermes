import time
import json
import logging
import requests
from datetime import datetime, timezone

from hermes_worker.celery_app import celery_app

logger = logging.getLogger(__name__)

_flask_app = None


def _get_app():
    global _flask_app
    if _flask_app is None:
        from hermes_server.app import create_app
        _flask_app = create_app()
    return _flask_app


def _send_notification(notification_config, execution, suite):
    config = notification_config.config or {}
    trigger_condition = notification_config.trigger_condition or {}
    fail_threshold = trigger_condition.get('fail_threshold', 100)
    fail_rate = 0
    if execution.total_count > 0:
        fail_rate = ((execution.fail_count + execution.error_count) / execution.total_count) * 100
    if fail_rate < fail_threshold:
        return

    payload = {
        'execution_id': execution.id,
        'suite_name': suite.name,
        'status': execution.status,
        'total_count': execution.total_count,
        'pass_count': execution.pass_count,
        'fail_count': execution.fail_count,
        'error_count': execution.error_count,
        'duration': execution.duration,
        'fail_rate': fail_rate,
    }

    ntype = notification_config.type
    try:
        if ntype == 'webhook':
            url = config.get('url')
            headers = config.get('headers', {})
            if url:
                requests.post(url, json=payload, headers=headers, timeout=10)
        elif ntype == 'dingtalk':
            webhook = config.get('webhook')
            if webhook:
                msg = {
                    'msgtype': 'markdown',
                    'markdown': {
                        'title': f'Hermes Test Notification',
                        'text': f'### {suite.name}\n> Status: {execution.status}\n> Pass: {execution.pass_count}/{execution.total_count}\n> Fail: {execution.fail_count}\n> Error: {execution.error_count}\n> Duration: {execution.duration:.2f}s',
                    },
                }
                requests.post(webhook, json=msg, timeout=10)
        elif ntype == 'wechat':
            webhook = config.get('webhook')
            if webhook:
                msg = {
                    'msgtype': 'markdown',
                    'markdown': {
                        'content': f'**{suite.name}**\nStatus: {execution.status}\nPass: {execution.pass_count}/{execution.total_count}\nFail: {execution.fail_count}\nError: {execution.error_count}\nDuration: {execution.duration:.2f}s',
                    },
                }
                requests.post(webhook, json=msg, timeout=10)
        elif ntype == 'email':
            smtp_host = config.get('smtp_host', '')
            smtp_port = int(config.get('smtp_port', 587))
            sender = config.get('sender', '')
            receivers = config.get('receivers', [])
            use_tls = config.get('use_tls', True)
            username = config.get('smtp_username', '')
            password = config.get('smtp_password', '')

            if not smtp_host or not sender or not receivers:
                logger.warning('Email notification config incomplete: %s', notification_config.id)
                continue

            subject = f"[Hermes] Test Execution {'Passed' if execution.status == 'success' else 'Failed'}"
            body = f"Execution ID: {execution.id}\nStatus: {execution.status}\n"
            if execution.duration:
                body += f"Duration: {execution.duration:.2f}s\n"

            try:
                import smtplib
                from email.mime.text import MIMEText
                msg = MIMEText(body)
                msg['Subject'] = subject
                msg['From'] = sender
                msg['To'] = ', '.join(receivers) if isinstance(receivers, list) else receivers

                if use_tls:
                    server = smtplib.SMTP(smtp_host, smtp_port)
                    server.starttls()
                else:
                    server = smtplib.SMTP(smtp_host, smtp_port)

                if username and password:
                    server.login(username, password)

                server.sendmail(sender, receivers if isinstance(receivers, list) else [receivers], msg.as_string())
                server.quit()
                logger.info('Email notification sent for execution %s', execution.id)
            except Exception as e:
                logger.error('Failed to send email notification: %s', str(e))
    except Exception as e:
        logger.error('Notification send failed: %s', str(e))


@celery_app.task(name='hermes_worker.tasks.execute_test_case', bind=True, max_retries=3)
def execute_test_case(self, case_id, environment_id):
    app = _get_app()

    with app.app_context():
        from hermes_server.app import db
        from hermes_server.models.execution import TestExecution, TestStepResult
        from hermes_server.models.test_case import TestCase
        from hermes_server.models.project import Environment, GlobalVariable
        from hermes_core.executor.runner import TestCaseRunner
        from hermes_core.parametrize.scope import VariableScope
        from hermes_core.parametrize.template import TemplateRenderer

        case = db.session.get(TestCase, case_id)
        if case is None:
            logger.error('TestCase %s not found', case_id)
            return

        environment = db.session.get(Environment, environment_id)
        if environment is None:
            logger.error('Environment %s not found', environment_id)
            return

        execution = TestExecution()
        execution.suite_id = None
        execution.environment_id = environment_id
        execution.status = 'running'
        execution.created_by = case.created_by
        execution.started_at = datetime.now(timezone.utc)
        db.session.add(execution)
        db.session.commit()

        env_vars = environment.variables or {}
        base_url = environment.base_url or ''

        global_variables = GlobalVariable.query.filter_by(
            environment_id=environment_id
        ).all()
        for gv in global_variables:
            env_vars[gv.key] = gv.value

        scope = VariableScope()
        for k, v in env_vars.items():
            scope.set_environment(k, v)

        renderer = TemplateRenderer()
        runner = TestCaseRunner()

        scope.clear_scope('case')
        scope.clear_scope('step')

        case_vars = case.variables or {}
        for k, v in case_vars.items():
            scope.set_case(k, v)

        merged_vars = scope.merge()

        request_config = case.request_config or {}
        if base_url and 'url' in request_config:
            url_val = request_config['url']
            if not url_val.startswith('http'):
                request_config['url'] = base_url.rstrip('/') + '/' + url_val.lstrip('/')

        rendered_request = renderer.render_dict(request_config, merged_vars) if request_config else {}

        case_config = {
            'request': rendered_request,
            'assertions': case.assertions or [],
            'pre_hooks': case.pre_hooks or [],
            'post_hooks': case.post_hooks or [],
            'variables': merged_vars,
        }

        step_result = TestStepResult()
        step_result.execution_id = execution.id
        step_result.case_id = case.id
        step_result.case_name = case.name
        step_result.status = 'running'
        step_result.started_at = datetime.now(timezone.utc)
        db.session.add(step_result)
        db.session.commit()

        start_time = time.time()

        try:
            result = runner.run(case_config, variables=merged_vars)

            step_result.status = result.status
            step_result.response_time = result.duration
            step_result.finished_at = datetime.now(timezone.utc)

            if result.response:
                step_result.response_status_code = result.response.status_code
                step_result.response_headers = result.response.headers if hasattr(result.response, 'headers') else None
                try:
                    step_result.response_body = result.response.text if hasattr(result.response, 'text') else str(result.response.body)
                except Exception:
                    step_result.response_body = None

            if result.assertion_results:
                step_result.assertions_result = [
                    {'name': getattr(ar, 'name', ''), 'passed': ar.passed, 'message': getattr(ar, 'message', '')}
                    for ar in result.assertion_results
                ]

            if result.error_message:
                step_result.error_message = result.error_message

            if result.status == 'pass':
                execution.pass_count = 1
                execution.fail_count = 0
                execution.error_count = 0
            elif result.status == 'fail':
                execution.pass_count = 0
                execution.fail_count = 1
                execution.error_count = 0
            else:
                execution.pass_count = 0
                execution.fail_count = 0
                execution.error_count = 1

        except Exception as e:
            step_result.status = 'error'
            step_result.error_message = str(e)
            step_result.finished_at = datetime.now(timezone.utc)
            execution.pass_count = 0
            execution.fail_count = 0
            execution.error_count = 1

        db.session.commit()

        elapsed = time.time() - start_time
        execution.total_count = 1
        execution.duration = elapsed
        execution.finished_at = datetime.now(timezone.utc)

        if execution.error_count > 0:
            execution.status = 'error'
        elif execution.fail_count > 0:
            execution.status = 'failed'
        else:
            execution.status = 'success'

        db.session.commit()

        return {
            'execution_id': execution.id,
            'status': execution.status,
            'duration': execution.duration,
        }


@celery_app.task(name='hermes_worker.tasks.execute_test_suite', bind=True, max_retries=3)
def execute_test_suite(self, execution_id, suite_id, environment_id):
    app = _get_app()

    with app.app_context():
        from hermes_server.app import db
        from hermes_server.models.execution import TestExecution, TestStepResult
        from hermes_server.models.test_case import TestCase, TestSuite, TestSuiteCase
        from hermes_server.models.project import Environment, GlobalVariable
        from hermes_server.models.notification import NotificationConfig
        from hermes_core.executor.runner import TestCaseRunner
        from hermes_core.parametrize.scope import VariableScope
        from hermes_core.parametrize.template import TemplateRenderer

        execution = db.session.get(TestExecution, execution_id)
        if execution is None:
            logger.error('TestExecution %s not found', execution_id)
            return

        execution.status = 'running'
        execution.started_at = datetime.now(timezone.utc)
        db.session.commit()

        suite = db.session.get(TestSuite, suite_id)
        if suite is None:
            execution.status = 'error'
            execution.finished_at = datetime.now(timezone.utc)
            db.session.commit()
            return

        environment = db.session.get(Environment, environment_id)
        if environment is None:
            execution.status = 'error'
            execution.finished_at = datetime.now(timezone.utc)
            db.session.commit()
            return

        suite_cases = TestSuiteCase.query.filter_by(
            suite_id=suite_id, is_enabled=True
        ).order_by(TestSuiteCase.sort_order).all()

        case_ids = [sc.case_id for sc in suite_cases]
        cases = TestCase.query.filter(
            TestCase.id.in_(case_ids), TestCase.status == 'active'
        ).all()
        case_map = {c.id: c for c in cases}

        env_vars = environment.variables or {}
        base_url = environment.base_url or ''

        global_variables = GlobalVariable.query.filter_by(
            environment_id=environment_id
        ).all()
        for gv in global_variables:
            env_vars[gv.key] = gv.value

        scope = VariableScope()
        for k, v in env_vars.items():
            scope.set_environment(k, v)

        renderer = TemplateRenderer()
        runner = TestCaseRunner()

        total_count = 0
        pass_count = 0
        fail_count = 0
        error_count = 0
        start_time = time.time()

        for suite_case in suite_cases:
            case = case_map.get(suite_case.case_id)
            if case is None:
                continue

            total_count += 1

            scope.clear_scope('case')
            scope.clear_scope('step')

            case_vars = case.variables or {}
            for k, v in case_vars.items():
                scope.set_case(k, v)

            merged_vars = scope.merge()

            request_config = case.request_config or {}
            if base_url and 'url' in request_config:
                url_val = request_config['url']
                if not url_val.startswith('http'):
                    request_config['url'] = base_url.rstrip('/') + '/' + url_val.lstrip('/')

            rendered_request = renderer.render_dict(request_config, merged_vars) if request_config else {}

            case_config = {
                'request': rendered_request,
                'assertions': case.assertions or [],
                'pre_hooks': case.pre_hooks or [],
                'post_hooks': case.post_hooks or [],
                'variables': merged_vars,
            }

            step_result = TestStepResult()
            step_result.execution_id = execution_id
            step_result.case_id = case.id
            step_result.case_name = case.name
            step_result.status = 'running'
            step_result.started_at = datetime.now(timezone.utc)
            db.session.add(step_result)
            db.session.commit()

            try:
                result = runner.run(case_config, variables=merged_vars)

                step_result.status = result.status
                step_result.response_time = result.duration
                step_result.finished_at = datetime.now(timezone.utc)

                if result.response:
                    step_result.response_status_code = result.response.status_code
                    step_result.response_headers = result.response.headers if hasattr(result.response, 'headers') else None
                    try:
                        step_result.response_body = result.response.text if hasattr(result.response, 'text') else str(result.response.body)
                    except Exception:
                        step_result.response_body = None

                if result.assertion_results:
                    step_result.assertions_result = [
                        {'name': getattr(ar, 'name', ''), 'passed': ar.passed, 'message': getattr(ar, 'message', '')}
                        for ar in result.assertion_results
                    ]

                if result.error_message:
                    step_result.error_message = result.error_message

                if result.extracted_variables:
                    for k, v in result.extracted_variables.items():
                        scope.set_step(k, v)

                if result.status == 'pass':
                    pass_count += 1
                elif result.status == 'fail':
                    fail_count += 1
                else:
                    error_count += 1

            except Exception as e:
                step_result.status = 'error'
                step_result.error_message = str(e)
                step_result.finished_at = datetime.now(timezone.utc)
                error_count += 1

            db.session.commit()

        elapsed = time.time() - start_time

        execution.total_count = total_count
        execution.pass_count = pass_count
        execution.fail_count = fail_count
        execution.error_count = error_count
        execution.duration = elapsed
        execution.finished_at = datetime.now(timezone.utc)

        if error_count > 0:
            execution.status = 'error'
        elif fail_count > 0:
            execution.status = 'failed'
        else:
            execution.status = 'success'

        db.session.commit()

        notification_configs = NotificationConfig.query.filter_by(
            project_id=suite.project_id, is_enabled=True
        ).all()
        for nc in notification_configs:
            _send_notification(nc, execution, suite)


@celery_app.task(name='hermes_worker.tasks.execute_scheduled_task', bind=True)
def execute_scheduled_task(self, scheduled_task_id):
    app = _get_app()

    with app.app_context():
        from hermes_server.app import db
        from hermes_server.models.scheduled_task import ScheduledTask
        from hermes_server.models.execution import TestExecution

        scheduled_task = db.session.get(ScheduledTask, scheduled_task_id)
        if scheduled_task is None:
            logger.error('ScheduledTask %s not found', scheduled_task_id)
            return

        if not scheduled_task.is_enabled:
            return

        execution = TestExecution()
        execution.suite_id = scheduled_task.suite_id
        execution.environment_id = scheduled_task.environment_id
        execution.status = 'pending'
        execution.created_by = scheduled_task.created_by
        db.session.add(execution)
        db.session.commit()

        scheduled_task.last_run_at = datetime.now(timezone.utc)
        db.session.commit()

        execute_test_suite.delay(execution.id, scheduled_task.suite_id, scheduled_task.environment_id)
