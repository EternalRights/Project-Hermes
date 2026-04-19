from flask import Flask

from app.error_handlers import HermesBusinessError, register_error_handlers


class TestHermesBusinessError:
    def test_attributes(self):
        err = HermesBusinessError(message="custom error", code=422, data={"field": "name"})
        assert err.message == "custom error"
        assert err.code == 422
        assert err.data == {"field": "name"}

    def test_default_attributes(self):
        err = HermesBusinessError()
        assert err.message == "业务异常"
        assert err.code == 400
        assert err.data is None

    def test_is_exception(self):
        err = HermesBusinessError(message="test")
        assert isinstance(err, Exception)


class TestHTTPErrorHandlers:
    def test_404_error(self, client):
        resp = client.get("/api/v1/nonexistent-endpoint")
        assert resp.status_code == 404
        data = resp.get_json()
        assert data["code"] == 404

    def test_400_error(self):
        app = Flask(__name__)
        app.config["TESTING"] = True
        register_error_handlers(app)

        @app.route("/test-bad-request")
        def trigger_bad_request():
            from flask import abort
            abort(400)

        with app.test_client() as c:
            resp = c.get("/test-bad-request")
            assert resp.status_code == 400
            data = resp.get_json()
            assert data["code"] == 400


class TestBusinessErrorHandler:
    def test_business_error_handler(self):
        app = Flask(__name__)
        app.config["TESTING"] = True
        register_error_handlers(app)

        @app.route("/test-business-error")
        def trigger_business_error():
            raise HermesBusinessError(message="insufficient quota", code=409, data={"limit": 100})

        with app.test_client() as c:
            resp = c.get("/test-business-error")
            assert resp.status_code == 409
            data = resp.get_json()
            assert data["code"] == 409
            assert data["message"] == "insufficient quota"
            assert data["data"] == {"limit": 100}
