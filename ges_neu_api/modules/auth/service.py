"""
Implementación de los servicios de autenticación y gestión de usuarios.

Este módulo contiene las implementaciones concretas de los servicios definidos
en los contratos del módulo de autenticación.
"""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List
from uuid import UUID

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from ges_neu_api.core.config import settings
from ges_neu_api.core.exceptions import (
    UnauthorizedException,
    NotFoundException,
    BadRequestException
)
from ges_neu_api.core.security import verify_password, get_password_hash
from .models_fixed import Usuario
from . import schemas

logger = logging.getLogger(__name__)

class AuthService:
    """Implementación del servicio de autenticación."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def authenticate_user(self, username: str, password: str) -> Optional[Usuario]:
        stmt = select(Usuario).where(
            or_(
                Usuario.username == username,
                Usuario.email == username
            )
        )
        result = await self.db.execute(stmt)
        user = result.scalars().first()
        
        if not user:
            logger.warning(f"Usuario no encontrado: {username}")
            raise UnauthorizedException(f"El usuario '{username}' no existe en el sistema")
            
        if not user.activo:
            logger.warning(f"Intento de inicio de sesión para usuario inactivo: {username}")
            raise UnauthorizedException("Esta cuenta está desactivada")
            
        if not verify_password(password, user.password_hash):
            logger.warning(f"Contraseña incorrecta para el usuario: {username}")
            raise UnauthorizedException("La contraseña es incorrecta")
            
        user.ultimo_login = datetime.utcnow()
        self.db.add(user)
        await self.db.commit()
        
        logger.info(f"Usuario autenticado correctamente: {username}")
        return user

    def create_access_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )
            
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        return encoded_jwt

    async def get_current_user(self, token: str) -> Usuario:
        credentials_exception = UnauthorizedException(
            "No se pudieron validar las credenciales"
        )
        
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
                
        except JWTError as e:
            logger.error(f"Error decodificando token JWT: {str(e)}")
            raise credentials_exception from e
            
        stmt = select(Usuario).where(
            or_(
                Usuario.username == username,
                Usuario.email == username
            )
        )
        result = await self.db.execute(stmt)
        user = result.scalars().first()
        
        if user is None:
            logger.warning(f"Usuario no encontrado para el token: {username}")
            raise credentials_exception
            
        if not user.activo:
            logger.warning(f"Intento de acceso para usuario inactivo: {username}")
            raise UnauthorizedException("Usuario inactivo")
            
        return user

class UserService:
    """Implementación del servicio de gestión de usuarios."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[Usuario]:
        result = await self.db.execute(
            select(Usuario).where(Usuario.id == user_id)
        )
        return result.scalars().first()
    
    async def get_by_email(self, email: str, db: AsyncSession) -> Optional[Usuario]:
        result = await db.execute(select(Usuario).where(Usuario.email == email))
        return result.scalars().first()

    async def create(self, obj_in: schemas.UserCreate, db: AsyncSession) -> Usuario:
        db_obj = Usuario(
            username=obj_in.username,
            email=obj_in.email,
            nombre_completo=obj_in.nombre_completo,
            password_hash=get_password_hash(obj_in.password),
            activo=obj_in.activo
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db_obj: Usuario, obj_in: schemas.UserUpdate, db: AsyncSession) -> Usuario:
        update_data = obj_in.dict(exclude_unset=True)
        if "password" in update_data and update_data["password"]:
            update_data["password_hash"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

class RoleService:
    """Implementación del servicio de gestión de roles."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_role(self, role_data: schemas.RoleCreate, created_by: UUID):  # -> models.Rol:
        # existing = await self.db.execute(select(models.Rol).where(models.Rol.nombre == role_data.nombre))
        # if existing.scalars().first():
        #     raise ValueError("Ya existe un rol con este nombre")
        # db_role = models.Rol(**role_data.dict(), creado_por=created_by)
        # self.db.add(db_role)
        # await self.db.commit()
        # await self.db.refresh(db_role)
        # return db_role
        pass  # Temporalmente deshabilitado hasta tener modelo Rol corregido

    async def get_role(self, role_id: UUID):  # -> Optional[models.Rol]:
        # result = await self.db.execute(select(models.Rol).where(models.Rol.id == role_id))
        # return result.scalars().first()
        pass  # Temporalmente deshabilitado

    async def get_roles(self, skip: int, limit: int, nombre: Optional[str]):  # -> List[models.Rol]:
        # query = select(models.Rol)
        # if nombre:
        #     query = query.where(models.Rol.nombre.ilike(f"%{nombre}%"))
        # result = await self.db.execute(query.offset(skip).limit(limit))
        # return result.scalars().all()
        return []  # Temporalmente deshabilitado

    async def update_role(self, db_role, role_data: schemas.RoleUpdate, updated_by: UUID):  # -> models.Rol:
        # ... (lógica de update)
        return db_role

    async def delete_role(self, role_id: UUID) -> bool:
        # ... (lógica de delete)
        return True

    async def assign_role_to_user(self, user_id: UUID, role_id: UUID, db: AsyncSession) -> Usuario:
        user = await self.db.get(Usuario, user_id)
        # role = await self.db.get(models.Rol, role_id)  # Comentado hasta tener modelo Rol corregido
        if not user:  # or not role:
            raise ValueError("Usuario no encontrado")
        # user.usuarios_roles.append(role)  # Comentado hasta tener relaciones
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def revoke_role_from_user(self, user_id: UUID, role_id: UUID, db: AsyncSession) -> Usuario:
        user = await self.db.get(Usuario, user_id)
        # role = await self.db.get(models.Rol, role_id)  # Comentado hasta tener modelo Rol corregido
        if not user:  # or not role or role not in user.usuarios_roles:
            raise ValueError("Usuario no encontrado")
        # user.usuarios_roles.remove(role)  # Comentado hasta tener relaciones
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

class PermissionService:
    """Implementación del servicio de gestión de permisos."""
    def __init__(self, db: AsyncSession):
        self.db = db
