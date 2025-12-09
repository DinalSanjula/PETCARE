# app/tests/conftest.py
import os
import pytest
import secrets

# Ensure SECRET_KEY (already set by root conftest, but keep safe)
os.environ.setdefault("SECRET_KEY", os.getenv("SECRET_KEY", "test-secret-key"))

from typing import Dict

# Reuse the global async_client fixture defined in project-root conftest
# Provide a test_user_token fixture that registers/logins a test user and returns tokens

@pytest.fixture
async def test_user_token(async_client) -> Dict[str, str]:
    """
    Register a test user and return tokens dict {"access_token": "...", "refresh_token": "..."}
    Accepts 201 or 409 for registration (duplicate).
    """
    payload = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "strongpassword",
        "role": "owner"
    }

    # Register
    r = await async_client.post("/auth/register", json=payload)
    assert r.status_code in (201, 409)
    data = r.json()
    if not data.get("success"):
        # If registration conflict, login to obtain tokens
        login_r = await async_client.post("/auth/login", json={"email": payload["email"], "password": payload["password"]})
        assert login_r.status_code == 200
        tokens = login_r.json()["data"]
    else:
        tokens = data["data"]

    return tokens