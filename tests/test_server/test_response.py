from unittest.mock import MagicMock

from app.response import success_response, error_response, paginate_response


class TestSuccessResponse:
    def test_with_data_message_code(self):
        result = success_response(data={"id": 1}, message="created", code=201)
        assert result == {"code": 201, "message": "created", "data": {"id": 1}}

    def test_with_defaults(self):
        result = success_response()
        assert result == {"code": 200, "message": "success", "data": None}

    def test_with_data_only(self):
        result = success_response(data=[1, 2, 3])
        assert result["code"] == 200
        assert result["message"] == "success"
        assert result["data"] == [1, 2, 3]


class TestErrorResponse:
    def test_with_message_and_code(self):
        result = error_response(message="not found", code=404)
        assert result == {"code": 404, "message": "not found", "data": None}

    def test_with_defaults(self):
        result = error_response()
        assert result == {"code": 400, "message": "error", "data": None}

    def test_with_data(self):
        result = error_response(message="validation failed", code=422, data={"field": "email"})
        assert result["code"] == 422
        assert result["message"] == "validation failed"
        assert result["data"] == {"field": "email"}


class TestPaginateResponse:
    def test_returns_paginated_dict(self):
        mock_pagination = MagicMock()
        mock_pagination.items = [{"id": 1}, {"id": 2}]
        mock_pagination.total = 50
        mock_pagination.page = 2
        mock_pagination.per_page = 10
        mock_pagination.pages = 5

        mock_query = MagicMock()
        mock_query.paginate.return_value = mock_pagination

        result = paginate_response(mock_query, page=2, per_page=10)

        mock_query.paginate.assert_called_once_with(page=2, per_page=10, error_out=False)
        assert result["items"] == [{"id": 1}, {"id": 2}]
        assert result["total"] == 50
        assert result["page"] == 2
        assert result["per_page"] == 10
        assert result["pages"] == 5
