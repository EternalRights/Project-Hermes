import pytest
from unittest.mock import patch, MagicMock

from hermes_server.services.report_service import ReportService
from hermes_server.services.exceptions import NotFoundError, ValidationError


class TestReportServiceGetReport:
    @patch('hermes_server.services.report_service.db')
    def test_get_report_not_found(self, mock_db):
        mock_db.session.get.return_value = None
        with pytest.raises(NotFoundError, match='execution not found'):
            ReportService.get_report(999)

    @patch('hermes_server.services.report_service.TestStepResult')
    @patch('hermes_server.services.report_service.db')
    def test_get_report_success(self, mock_db, MockStepResult):
        mock_execution = MagicMock()
        mock_execution.total_count = 10
        mock_execution.pass_count = 8
        mock_execution.fail_count = 2
        mock_execution.error_count = 0
        mock_execution.skip_count = 0
        mock_execution.duration = 5.5
        mock_execution.started_at = None
        mock_execution.finished_at = None
        mock_db.session.get.return_value = mock_execution

        mock_step = MagicMock()
        mock_step.response_time = 100
        mock_step.to_dict.return_value = {'id': 1, 'status': 'pass'}
        MockStepResult.query.filter_by.return_value.all.return_value = [mock_step]

        result = ReportService.get_report(1)
        assert 'summary' in result
        assert 'step_results' in result
        assert 'failed_cases' in result
        assert result['summary']['total_count'] == 10
        assert result['summary']['pass_rate'] == 80.0


class TestReportServiceGetTrend:
    def test_get_trend_missing_suite_id(self):
        with pytest.raises(ValidationError, match='suite_id is required'):
            ReportService.get_trend(None)


class TestReportServiceExportHtml:
    @patch('hermes_server.services.report_service.db')
    def test_export_html_not_found(self, mock_db):
        mock_db.session.get.return_value = None
        with pytest.raises(NotFoundError, match='execution not found'):
            ReportService.export_report_html(999)
