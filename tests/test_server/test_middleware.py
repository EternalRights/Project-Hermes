from unittest.mock import patch, MagicMock

from middleware.permission import require_permission


def test_require_permission_user_has_permission():
    mock_user = MagicMock()
    mock_user.has_permission.return_value = True

    with patch("middleware.permission.get_current_user", return_value=mock_user):
        @require_permission("project:create")
        def sample_view():
            return "ok"

        result = sample_view()
        assert result == "ok"
        mock_user.has_permission.assert_called_with("project:create")


def test_require_permission_user_lacks_permission():
    mock_user = MagicMock()
    mock_user.has_permission.return_value = False

    with patch("middleware.permission.get_current_user", return_value=mock_user):
        @require_permission("project:delete")
        def sample_view():
            return "ok"

        result, status_code = sample_view()
        assert status_code == 403
        assert result["code"] == 403
        assert result["message"] == "permission denied"


def test_require_permission_no_user():
    with patch("middleware.permission.get_current_user", return_value=None):
        @require_permission("project:create")
        def sample_view():
            return "ok"

        result, status_code = sample_view()
        assert status_code == 401
        assert result["code"] == 401
        assert result["message"] == "user not found"
