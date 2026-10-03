from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.api.dependencies import get_classifier
from app.classifier import FakeClassifier
from app.main import create_app


def test_health_success(monkeypatch, settings):
    calls = []
    monkeypatch.setattr("app.main.check_database", lambda engine: calls.append(engine))
    with TestClient(create_app(settings)) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}
    assert len(calls) == 1


def test_health_safe_failure(monkeypatch, settings):
    def fail(engine):
        raise OperationalError("SELECT secret", {}, Exception("private password"))

    monkeypatch.setattr("app.main.check_database", fail)
    with TestClient(create_app(settings)) as client:
        response = client.get("/health")
    assert response.status_code == 503
    assert response.json() == {"status": "unavailable", "database": "unavailable"}
    assert "private" not in response.text


def test_classifier_dependency_can_be_replaced(settings):
    fake = FakeClassifier(fail=True)
    app = create_app(settings, classifier=fake)

    @app.get("/test-dependency")
    def dependency(classifier=Depends(get_classifier)):
        return {"injected": classifier is fake}

    with TestClient(app) as client:
        assert client.get("/test-dependency").json() == {"injected": True}


def test_cors_and_scope(settings):
    with TestClient(create_app(settings)) as client:
        allowed = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        rejected = client.options(
            "/health",
            headers={
                "Origin": "https://other.example",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert allowed.status_code == 200
        assert rejected.status_code == 400
        assert client.post("/api/comments/analyze", json={"text": "test"}).status_code == 404
