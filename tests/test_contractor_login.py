import secrets

import pytest
from fastapi import HTTPException

from app import main, mongo_store
from app.auth import verify_password
from app.mongo_store import MongoStore


def test_seeded_contractor_password_comes_from_local_environment(monkeypatch):
    password = secrets.token_urlsafe(24)
    monkeypatch.setattr(mongo_store, "MONGO_URI", "")
    monkeypatch.setenv("DEMO_CONTRACTOR_PASSWORD", password)

    store = MongoStore()
    store.seed()
    contractor = store.collection("contractors").find_one({"email": "contact@metrofix.com"})

    assert verify_password(password, contractor["password_hash"])


def test_contractor_login_requires_configured_password(monkeypatch):
    monkeypatch.setattr(mongo_store, "MONGO_URI", "")
    monkeypatch.delenv("DEMO_CONTRACTOR_PASSWORD", raising=False)
    store = MongoStore()
    store.seed()
    contractors = store.collection("contractors")
    monkeypatch.setattr(main.store, "collection", lambda _name: contractors)

    with pytest.raises(HTTPException) as error:
        main.login(main.LoginRequest(
            role="contractor",
            identifier="contact@metrofix.com",
        ))

    assert error.value.status_code == 503
    assert "DEMO_CONTRACTOR_PASSWORD" in error.value.detail
