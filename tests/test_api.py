import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx
from app.main import app

def _run_async(coro):
    return asyncio.run(coro)

def test_read_main():
    async def _test():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
            response = await client.get("/")
            assert response.status_code == 200
            assert response.json() == {"message": "Stock Market Analysis API"}
    _run_async(_test())

def test_health_check():
    async def _test():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            assert response.json() == {"status": "healthy"}
    _run_async(_test())

def test_search_stock():
    async def _test():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
            response = await client.get("/stocks/search/AAPL")
            assert response.status_code in [200, 404]
    _run_async(_test())

def test_register_user():
    async def _test():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
            import uuid
            uid = uuid.uuid4().hex[:6]
            user_data = {
                "username": f"user_{uid}",
                "email": f"user_{uid}@example.com",
                "password": "testpass123"
            }
            response = await client.post("/auth/register", json=user_data)
            assert response.status_code in [200, 400]
    _run_async(_test())

def test_register_rejects_password_over_bcrypt_limit():
    async def _test():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
            import uuid
            uid = uuid.uuid4().hex[:6]
            response = await client.post(
                "/auth/register",
                json={
                    "username": f"long_password_{uid}",
                    "email": f"long_password_{uid}@example.com",
                    "password": "p" * 73,
                },
            )
            assert response.status_code == 422
            assert "72 UTF-8 bytes" in response.json()["detail"][0]["msg"]
    _run_async(_test())

def test_login_user():
    async def _test():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
            login_data = {
                "username": "testuser",
                "password": "testpass"
            }
            response = await client.post("/auth/login", json=login_data)
            assert response.status_code in [200, 401]
    _run_async(_test())

if __name__ == "__main__":
    print("Running API tests...")
    test_read_main()
    print("  [OK] test_read_main passed")
    test_health_check()
    print("  [OK] test_health_check passed")
    test_search_stock()
    print("  [OK] test_search_stock passed")
    test_register_user()
    print("  [OK] test_register_user passed")
    test_register_rejects_password_over_bcrypt_limit()
    print("  [OK] test_register_rejects_password_over_bcrypt_limit passed")
    test_login_user()
    print("  [OK] test_login_user passed")
    print("All tests passed successfully!")