# tests/debug_routes.py
import pytest
from main import app

@pytest.mark.anyio
async def test_routes_exist(async_client):
    r = await async_client.get("/openapi.json")
    print("OPENAPI PATHS:", r.json().get("paths", {}))