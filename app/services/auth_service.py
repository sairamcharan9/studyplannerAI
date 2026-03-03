from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    username: str
    email: str

class AuthService:
    def __init__(self):
        # Initial demo users
        # For test_auth.py: username is "testuser"
        # For frontend: identifier is "test@example.com"
        self.users = {
            "testuser": {
                "password": "testpassword",
                "email": "test@example.com"
            },
            "test@example.com": {
                "password": "testpassword",
                "username": "testuser"
            }
        }

    async def authenticate_user(self, identifier: str, password: str) -> Optional[User]:
        if not identifier or not password:
            return None

        user_data = self.users.get(identifier)
        if user_data and user_data["password"] == password:
            # Determine email and username from data
            if "email" in user_data: # identifier was username
                return User(username=identifier, email=user_data["email"])
            else: # identifier was email
                return User(username=user_data["username"], email=identifier)

        return None
