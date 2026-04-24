from datetime import datetime, timedelta, timezone

from flask import make_response
from sqlalchemy import func

from hermes_server.app import db
from hermes_server.models.execution import TestExecution, TestStepResult
from hermes_core.utils.html_escape import html_escape
from hermes_server.services.exceptions import NotFoundError, ValidationError


class ReportService:
    @staticmethod
    def get_report(execution_id):
        execution = db.session.get(TestExecution, execution_id)
        if not execution:
            raise NotFoundError('execution not found')

        total = execution.total_count or 0
        pass_count = execution.pass_count or 0
        fail_count = execution.fail_count or 0
        pass_rate = round(pass_count / total * 100, 2) if total > 0 else 0
        fail_rate = round(fail_count / total * 100, 2) if total > 0 else 0

        step_results = TestStepResult.query.filter_by(execution_id=execution_id).all()
        response_times = [r.response_time for r in step_results if r.response_time and r.response_time > 0]
        avg_response_time = round(sum(response_times) / len(response_times), 2) if response_times else 0

        sorted_times = sorted(response_times)
        p95_response_time = 0
        p99_response_time = 0
        if sorted_times:
            p95_index = int(len(sorted_times) * 0.95)
            p99_index = int(len(sorted_times) * 0.99)
            p95_response_time = round(sorted_times[min(p95_index, len(sorted_times) - 1)], 2)
            p99_response_time = round(sorted_times[min(p99_index, len(sorted_times) - 1)], 2)

        summary = {
            'pass_rate': pass_rate,
            'fail_rate': fail_rate,
            'avg_response_time': avg_response_time,
            'p95_response_time': p95_response_time,
            'p99_response_time': p99_response_time,
            'total_count': total,
            'pass_count': pass_count,
            'fail_count': fail_count,
            'error_count': execution.error_count or 0,
            'skip_count': execution.skip_count or 0,
            'duration': execution.duration,
            'started_at': execution.started_at.isoformat() if execution.started_at else None,
            'finished_at': execution.finished_at.isoformat() if execution.finished_at else None,
        }

        steps = [r.to_dict() for r in step_results]
        failed_cases = [s for s in steps if s['status'] in ('fail', 'error')]

        return {
            'summary': summary,
            'step_results': steps,
            'failed_cases': failed_cases,
        }

    @staticmethod
    def get_trend(suite_id, days=30):
        if not suite_id:
            raise ValidationError('suite_id is required')

        start_date = datetime.now(timezone.utc) - timedelta(days=days)

        daily_stats = db.session.query(
            func.date(TestExecution.created_at).label('date'),
            func.sum(TestExecution.pass_count).label('total_pass'),
            func.sum(TestExecution.total_count).label('total_count'),
            func.avg(TestExecution.duration).label('avg_duration'),
        ).filter(
            TestExecution.suite_id == suite_id,
            TestExecution.created_at >= start_date,
        ).group_by(
            func.date(TestExecution.created_at),
        ).order_by(
            func.date(TestExecution.created_at),
        ).all()

        step_stats = db.session.query(
            func.date(TestExecution.created_at).label('date'),
            func.avg(TestStepResult.response_time).label('avg_response_time'),
        ).join(
            TestStepResult, TestStepResult.execution_id == TestExecution.id,
        ).filter(
            TestExecution.suite_id == suite_id,
            TestExecution.created_at >= start_date,
            TestStepResult.response_time > 0,
        ).group_by(
            func.date(TestExecution.created_at),
        ).order_by(
            func.date(TestExecution.created_at),
        ).all()

        step_time_map = {str(s.date): round(float(s.avg_response_time), 2) for s in step_stats}

        pass_rate_trend = []
        avg_response_time_trend = []

        for stat in daily_stats:
            date_str = str(stat.date)
            total = int(stat.total_count) if stat.total_count else 0
            total_pass = int(stat.total_pass) if stat.total_pass else 0
            rate = round(total_pass / total * 100, 2) if total > 0 else 0

            pass_rate_trend.append({
                'date': date_str,
                'pass_rate': rate,
            })
            avg_response_time_trend.append({
                'date': date_str,
                'avg_response_time': step_time_map.get(date_str, 0),
            })

        return {
            'pass_rate_trend': pass_rate_trend,
            'avg_response_time_trend': avg_response_time_trend,
        }

    @staticmethod
    def export_report_html(execution_id):
        execution = db.session.get(TestExecution, execution_id)
        if not execution:
            raise NotFoundError('execution not found')

        step_results = TestStepResult.query.filter_by(execution_id=execution_id).all()

        total = execution.total_count or 0
        pass_count = execution.pass_count or 0
        fail_count = execution.fail_count or 0
        pass_rate = round(pass_count / total * 100, 2) if total > 0 else 0
        fail_rate = round(fail_count / total * 100, 2) if total > 0 else 0

        rows = ''
        for r in step_results:
            status_color = '#52c41a' if r.status == 'pass' else '#ff4d4f' if r.status == 'fail' else '#faad14'
            rows += f'''<tr>
            <td style="padding:8px;border:1px solid #ddd;">{html_escape(r.case_name)}</td>
            <td style="padding:8px;border:1px solid #ddd;color:{status_color};font-weight:bold;">{html_escape(r.status)}</td>
            <td style="padding:8px;border:1px solid #ddd;">{r.response_status_code or '-'}</td>
            <td style="padding:8px;border:1px solid #ddd;">{r.response_time or 0}ms</td>
            <td style="padding:8px;border:1px solid #ddd;">{html_escape(r.error_message or '-')}</td>
        </tr>'''

        html = f'''<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Test Report - Execution #{execution_id}</title></head>
<body style="font-family:Arial,sans-serif;margin:20px;background:#f5f5f5;">
<div style="max-width:1000px;margin:0 auto;background:#fff;padding:30px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);">
<h1 style="color:#333;border-bottom:2px solid #1890ff;padding-bottom:10px;">Test Report - Execution #{execution_id}</h1>
<h2 style="color:#555;">Summary</h2>
<table style="width:100%;border-collapse:collapse;margin-bottom:20px;">
<tr><td style="padding:8px;border:1px solid #ddd;font-weight:bold;">Total</td><td style="padding:8px;border:1px solid #ddd;">{total}</td>
<td style="padding:8px;border:1px solid #ddd;font-weight:bold;">Pass</td><td style="padding:8px;border:1px solid #ddd;color:#52c41a;">{pass_count}</td>
<td style="padding:8px;border:1px solid #ddd;font-weight:bold;">Fail</td><td style="padding:8px;border:1px solid #ddd;color:#ff4d4f;">{fail_count}</td></tr>
<tr><td style="padding:8px;border:1px solid #ddd;font-weight:bold;">Pass Rate</td><td style="padding:8px;border:1px solid #ddd;">{pass_rate}%</td>
<td style="padding:8px;border:1px solid #ddd;font-weight:bold;">Fail Rate</td><td style="padding:8px;border:1px solid #ddd;">{fail_rate}%</td>
<td style="padding:8px;border:1px solid #ddd;font-weight:bold;">Duration</td><td style="padding:8px;border:1px solid #ddd;">{execution.duration or 0}s</td></tr>
</table>
<h2 style="color:#555;">Step Results</h2>
<table style="width:100%;border-collapse:collapse;">
<thead><tr style="background:#fafafa;">
<th style="padding:8px;border:1px solid #ddd;text-align:left;">Case Name</th>
<th style="padding:8px;border:1px solid #ddd;text-align:left;">Status</th>
<th style="padding:8px;border:1px solid #ddd;text-align:left;">Status Code</th>
<th style="padding:8px;border:1px solid #ddd;text-align:left;">Response Time</th>
<th style="padding:8px;border:1px solid #ddd;text-align:left;">Error</th>
</tr></thead>
<tbody>{rows}</tbody>
</table>
</div>
</body>
</html>'''

        response = make_response(html)
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        return response
