"""Test data factories for the auth module."""
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

# Use test models for SQLite compatibility
from ges_neu_api.core.test_models import Rol, Usuario
from ges_neu_api.core.security import get_password_hash
from tests.factories import ModelFactory


class UsuarioFactory(ModelFactory):
    """Factory for creating Usuario test data."""

    @classmethod
    def build(cls, **overrides: Any) -> Dict[str, Any]:
        """Build user data dictionary with proper password hashing."""
        # Use timestamp to ensure uniqueness across tests
        import time
        timestamp = str(int(time.time() * 1000))[-8:]  # Last 8 digits of timestamp
        uid = str(uuid4())
        
        # Extract parameters with defaults
        username = overrides.pop("username", None)
        email = overrides.pop("email", None)
        nombre_completo = overrides.pop("nombre_completo", None)
        password = overrides.pop("password", "testpassword123")
        activo = overrides.pop("activo", True)
        
        # Hash the password properly
        password_hash = get_password_hash(password)
        
        return {
            "username": username or f"user_{timestamp}_{uid[:4]}",
            "email": email or f"user-{timestamp}-{uid[:4]}@example.com",
            "nombre_completo": nombre_completo or f"User Test {timestamp}",
            "password_hash": password_hash,
            "activo": activo,
            **overrides
        }

    @classmethod
    async def create(cls, db: AsyncSession, **overrides: Any) -> Usuario:
        """Create a user in the database with commit for persistence in tests."""
        data = cls.build(**overrides)
        
        # Handle password hashing
        if "password" in data:
            password = data.pop("password")
            data["password_hash"] = get_password_hash(password)
        
        # Remove any fields not in the actual PostgreSQL schema
        data.pop("rol", None)  # Remove rol field as it's not in usuarios table
        
        # Create user with only valid fields according to PostgreSQL schema
        user = Usuario(**data)
        
        db.add(user)
        await db.commit()  # Commit to persist for authentication tests
        await db.refresh(user)
        return user
