import pytest
from app.services.auth_service import AuthService, User

@pytest.mark.asyncio
async def test_authenticate_user_success():
    auth_service = AuthService()
    user = await auth_service.authenticate_user("testuser", "testpassword")
    assert user is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"

@pytest.mark.asyncio
async def test_authenticate_user_failure_wrong_password():
    auth_service = AuthService()
    user = await auth_service.authenticate_user("testuser", "wrongpassword")
    assert user is None

@pytest.mark.asyncio
async def test_authenticate_user_failure_wrong_username():
    auth_service = AuthService()
    user = await auth_service.authenticate_user("wronguser", "testpassword")
    assert user is None

@pytest.mark.asyncio
async def test_authenticate_user_failure_empty_credentials():
    auth_service = AuthService()
    user = await auth_service.authenticate_user("", "")
    assert user is None
