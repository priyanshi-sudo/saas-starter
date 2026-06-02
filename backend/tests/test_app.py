import os

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.core.security import ROLES_ORDER, Principal
from app.main import app


def test_health():
    # No context manager → DB-touching lifespan doesn't run.
    resp = TestClient(app).get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_role_ordering():
    assert ROLES_ORDER["owner"] > ROLES_ORDER["admin"] > ROLES_ORDER["member"]


def test_principal_defaults():
    p = Principal(user_id="u1", email="a@b.com")
    assert p.org_id is None
    assert p.role is None


def test_cors_list_parsing(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "http://a.com, http://b.com")
    s = Settings()
    assert s.cors_list == ["http://a.com", "http://b.com"]


def test_admin_allowlist_parsing(monkeypatch):
    monkeypatch.setenv("ADMIN_EMAILS", "root@x.com, ops@x.com")
    # Re-import to re-read the module-level allowlist.
    import importlib

    from app.api import admin

    importlib.reload(admin)
    assert "root@x.com" in admin._ADMIN_EMAILS
    assert "ops@x.com" in admin._ADMIN_EMAILS
    os.environ.pop("ADMIN_EMAILS", None)
