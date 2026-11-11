import pytest
from fastapi import HTTPException

from app import main


class EmptyCollection:
    def find_one(self, query):
        return None


def test_authority_login_sends_otp_to_any_valid_email(monkeypatch):
    sent_to = []
    monkeypatch.setattr(main.store, "collection", lambda _name: EmptyCollection())
    monkeypatch.setattr(main, "send_authority_otp", lambda email, _otp: sent_to.append(email) or True)
    main.PENDING_OTPS.clear()

    result = main.login(main.LoginRequest(
        role="authority",
        identifier="  New.Staff@Example.org ",
    ))

    assert result["otp_required"] is True
    assert result["email"] == "new.staff@example.org"
    assert sent_to == ["new.staff@example.org"]
    challenge = main.PENDING_OTPS[result["challenge_id"]]
    assert challenge["email"] == "new.staff@example.org"
    assert challenge["account_id"] == "AUTH001"

    verified = main.verify_authority_otp(main.OtpRequest(
        challenge_id=result["challenge_id"],
        otp=challenge["otp"],
    ))
    assert verified["role"] == "authority"
    assert verified["account_id"] == "AUTH001"
    main.PENDING_OTPS.clear()


def test_authority_login_rejects_invalid_email(monkeypatch):
    monkeypatch.setattr(main.store, "collection", lambda _name: EmptyCollection())

    with pytest.raises(HTTPException) as error:
        main.login(main.LoginRequest(role="authority", identifier="not-an-email"))

    assert error.value.status_code == 400
    assert error.value.detail == "Enter a valid email address."
