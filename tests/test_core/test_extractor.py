from unittest.mock import MagicMock

import pytest

from hermes_core.executor.extractor import VariableExtractor


@pytest.fixture
def extractor():
    return VariableExtractor()


@pytest.fixture
def mock_response():
    resp = MagicMock()
    resp.json.return_value = {
        "code": 200,
        "data": {"id": 42, "name": "hermes", "tags": ["api", "test"]},
    }
    resp.text = '{"code": 200, "data": {"id": 42, "name": "hermes"}}'
    return resp


class TestExtractByJsonPath:

    def test_matching_path(self, extractor, mock_response):
        result = extractor.extract_by_json_path(mock_response, "$.data.name", "var_name")
        assert result == {"var_name": "hermes"}

    def test_matching_path_nested(self, extractor, mock_response):
        result = extractor.extract_by_json_path(mock_response, "$.data.id", "user_id")
        assert result == {"user_id": 42}

    def test_matching_path_list_element(self, extractor, mock_response):
        result = extractor.extract_by_json_path(mock_response, "$.data.tags[0]", "first_tag")
        assert result == {"first_tag": "api"}

    def test_non_matching_path(self, extractor, mock_response):
        result = extractor.extract_by_json_path(mock_response, "$.nonexistent.path", "var_name")
        assert result == {}

    def test_invalid_json_response(self, extractor):
        resp = MagicMock()
        resp.json.side_effect = ValueError("invalid json")
        result = extractor.extract_by_json_path(resp, "$.data", "var_name")
        assert result == {}

    def test_invalid_json_path_expression(self, extractor, mock_response):
        result = extractor.extract_by_json_path(mock_response, "not[a]valid", "var_name")
        assert result == {}


class TestExtractByRegex:

    def test_matching_pattern(self, extractor, mock_response):
        result = extractor.extract_by_regex(mock_response, r"hermes", "var_name")
        assert result == {"var_name": "hermes"}

    def test_matching_pattern_with_digits(self, extractor, mock_response):
        result = extractor.extract_by_regex(mock_response, r"\d+", "code")
        assert result == {"code": "200"}

    def test_non_matching_pattern(self, extractor, mock_response):
        result = extractor.extract_by_regex(mock_response, r"not_found_pattern", "var_name")
        assert result == {}

    def test_group_parameter(self, extractor, mock_response):
        result = extractor.extract_by_regex(mock_response, r"(\d+)", "code", group=1)
        assert result == {"code": "200"}

    def test_group_parameter_named_group(self, extractor):
        resp = MagicMock()
        resp.text = "user_id=12345"
        result = extractor.extract_by_regex(resp, r"user_id=(\d+)", "uid", group=1)
        assert result == {"uid": "12345"}

    def test_invalid_regex_pattern(self, extractor, mock_response):
        result = extractor.extract_by_regex(mock_response, r"[invalid", "var_name")
        assert result == {}


class TestExtractVariables:

    def test_json_path_type(self, extractor, mock_response):
        config = [
            {"type": "json_path", "path": "$.data.name", "variable": "name"},
        ]
        result = extractor.extract_variables(mock_response, config)
        assert result == {"name": "hermes"}

    def test_regex_type(self, extractor, mock_response):
        config = [
            {"type": "regex", "pattern": r"\d+", "variable": "code"},
        ]
        result = extractor.extract_variables(mock_response, config)
        assert result == {"code": "200"}

    def test_regex_type_with_group(self, extractor, mock_response):
        config = [
            {"type": "regex", "pattern": r"(\d+)", "variable": "code", "group": 1},
        ]
        result = extractor.extract_variables(mock_response, config)
        assert result == {"code": "200"}

    def test_multiple_extractions(self, extractor, mock_response):
        config = [
            {"type": "json_path", "path": "$.data.name", "variable": "name"},
            {"type": "regex", "pattern": r"\d+", "variable": "code"},
        ]
        result = extractor.extract_variables(mock_response, config)
        assert result == {"name": "hermes", "code": "200"}

    def test_missing_variable_name(self, extractor, mock_response):
        config = [
            {"type": "json_path", "path": "$.data.name"},
        ]
        result = extractor.extract_variables(mock_response, config)
        assert result == {}

    def test_empty_config(self, extractor, mock_response):
        result = extractor.extract_variables(mock_response, [])
        assert result == {}

    def test_unknown_type_skipped(self, extractor, mock_response):
        config = [
            {"type": "unknown_type", "variable": "val"},
        ]
        result = extractor.extract_variables(mock_response, config)
        assert result == {}

    def test_default_source_body(self, extractor, mock_response):
        config = [
            {"type": "json_path", "path": "$.data.id", "variable": "id"},
        ]
        result = extractor.extract_variables(mock_response, config)
        assert result == {"id": 42}
