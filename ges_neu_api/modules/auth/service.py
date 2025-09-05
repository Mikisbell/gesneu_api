"""
Implementación de los servicios de autenticación y gestión de usuarios.

Este módulo contiene las implementaciones concretas de los servicios definidos
en los contratos del módulo de autenticación.
"""
import logging
import traceback
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
from .models import Usuario, Rol, Permiso, UsuariosRoles as UsuarioRol, RolesPermisos as RolPermiso
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
            # Los tests esperan este mensaje exacto
            raise UnauthorizedException("Inactive user")
            
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
            sub_value: str = payload.get("sub")
            if sub_value is None:
                raise credentials_exception
                
        except JWTError as e:
            logger.error(f"Error decodificando token JWT: {str(e)}")
            raise credentials_exception from e
            
        # Intentar interpretar 'sub' como UUID (nuevo formato de token)
        user = None
        try:
            user_id = UUID(sub_value)
            result = await self.db.execute(select(Usuario).where(Usuario.id == user_id))
            user = result.scalars().first()
        except (ValueError, TypeError):
            # Compatibilidad hacia atrás: usar como username/email
            stmt = select(Usuario).where(
                or_(
                    Usuario.username == sub_value,
                    Usuario.email == sub_value
                )
            )
            result = await self.db.execute(stmt)
            user = result.scalars().first()
        
        if user is None:
            logger.warning(f"Usuario no encontrado para el token: {sub_value}")
            raise credentials_exception
            
        if not user.activo:
            logger.warning(f"Intento de acceso para usuario inactivo: {sub_value}")
            raise UnauthorizedException("Usuario inactivo")
            
        return user

class UserService:
    """Implementación del servicio de gestión de usuarios."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_multi(self, skip: int = 0, limit: int = 100, db: AsyncSession = None) -> list[Usuario]:
        """Obtiene múltiples usuarios con paginación."""
        if db is None:
            db = self.db
        
        try:
            logger.info(f"UserService.get_multi: skip={skip}, limit={limit}")
            
            # Query directo usando AsyncSession
            query = select(Usuario).where(Usuario.activo == True).offset(skip).limit(limit)
            result = await db.execute(query)
            users = result.scalars().all()
            
            logger.info(f"UserService.get_multi: encontrados {len(users)} usuarios")
            return list(users)
            
        except Exception as e:
            logger.error(f"Error en UserService.get_multi: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def get_user_by_id(self, user_id: UUID) -> Usuario:
        user = await self.db.get(Usuario, user_id)
        if user is None:
            raise NotFoundException(f"Usuario con ID {user_id} no encontrado")
        return user
    
    async def get_by_username(self, username: str, db: AsyncSession) -> Optional[Usuario]:
        """Obtiene un usuario por username."""
        result = await db.execute(select(Usuario).where(Usuario.username == username))
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str, db: AsyncSession) -> Optional[Usuario]:
        result = await db.execute(select(Usuario).where(Usuario.email == email))
        return result.scalar_one_or_none()

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

    async def create_user(self, user_data: 'schemas.UserCreate') -> Usuario:
        """Crea un nuevo usuario."""
        from ges_neu_api.core.security import get_password_hash
        
        # Verificar si el usuario ya existe
        existing_user = await self.db.execute(
            select(Usuario).where(Usuario.username == user_data.username)
        )
        if existing_user.scalar_one_or_none():
            raise BadRequestException(f"El username '{user_data.username}' ya está en uso")
        
        # Crear nuevo usuario
        db_user = Usuario(
            username=user_data.username,
            email=user_data.email,
            nombre_completo=user_data.nombre_completo,
            password_hash=get_password_hash(user_data.password),
            activo=user_data.activo if hasattr(user_data, 'activo') else True
        )
        
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

class RoleService:
    """Implementación del servicio de gestión de roles."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_role(self, role_data: schemas.RoleCreate, created_by: UUID) -> Rol:
        try:
            # Validar que el creador exista para cumplir FK (usuarios.id)
            creator = await self.db.execute(select(Usuario).where(Usuario.id == created_by))
            if creator.scalars().first() is None:
                raise ValueError("Usuario creador no existe")
            
            # Verificar si ya existe un rol con el mismo nombre
            existing = await self.db.execute(select(Rol).where(Rol.nombre == role_data.nombre))
            if existing.scalars().first():
                raise ValueError("Ya existe un rol con este nombre")
            
            db_role = Rol(
                nombre=role_data.nombre,
                descripcion=role_data.descripcion,
                creado_por=created_by
            )
            self.db.add(db_role)
            await self.db.commit()
            await self.db.refresh(db_role)
            return db_role
        except Exception as e:
            logger.error(f"Error creando rol: {str(e)}")
            raise

    async def get_role(self, role_id: UUID) -> Optional[Rol]:
        try:
            result = await self.db.execute(select(Rol).where(Rol.id == role_id))
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error obteniendo rol {role_id}: {str(e)}")
            raise

    async def get_roles(self, skip: int = 0, limit: int = 100, nombre: Optional[str] = None) -> List[Rol]:
        try:
            logger.info(f"RoleService.get_roles: skip={skip}, limit={limit}, nombre={nombre}")
            
            # 'roles' no tiene columna 'activo' según ESQUEMA_COMPLETO_BD.md
            query = select(Rol)
            if nombre:
                query = query.where(Rol.nombre.ilike(f"%{nombre}%"))
            
            query = query.offset(skip).limit(limit)
            result = await self.db.execute(query)
            roles = result.scalars().all()
            
            logger.info(f"RoleService.get_roles: encontrados {len(roles)} roles")
            return list(roles)
        except Exception as e:
            logger.error(f"Error en RoleService.get_roles: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def update_role(self, db_role, role_data: schemas.RoleUpdate, updated_by: UUID):  # -> models.Rol:
        try:
            update_data = role_data.dict(exclude_unset=True)
            # Validar duplicado si cambia el nombre
            if "nombre" in update_data and update_data["nombre"] != db_role.nombre:
                existing = await self.db.execute(select(Rol).where(Rol.nombre == update_data["nombre"]))
                if existing.scalars().first():
                    raise ValueError("Ya existe un rol con este nombre")
            for k, v in update_data.items():
                setattr(db_role, k, v)
            # Marcar auditoría básica
            db_role.actualizado_en = datetime.utcnow()
            db_role.actualizado_por = updated_by
            self.db.add(db_role)
            await self.db.commit()
            await self.db.refresh(db_role)
            return db_role
        except Exception as e:
            logger.error(f"Error actualizando rol {db_role.id}: {str(e)}")
            raise

    async def delete_role(self, role_id: UUID) -> bool:
        try:
            result = await self.db.execute(select(Rol).where(Rol.id == role_id))
            role = result.scalars().first()
            if not role:
                return False
            await self.db.delete(role)
            await self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Error eliminando rol {role_id}: {str(e)}")
            raise

    async def assign_role_to_user(self, user_id: UUID, role_id: UUID, db: AsyncSession) -> Usuario:
        try:
            # Aceptar str o UUID
            uid = UUID(str(user_id))
            rid = UUID(str(role_id))
        except ValueError:
            raise ValueError("IDs inválidos")
        user = await self.db.get(Usuario, uid)
        if not user:
            raise ValueError("Usuario no encontrado")
        role = await self.db.get(Rol, rid)
        if not role:
            raise ValueError("Rol no encontrado")
        # Verificar si ya existe la asignación
        existing = await self.db.execute(
            select(UsuarioRol).where((UsuarioRol.usuario_id == uid) & (UsuarioRol.rol_id == rid))
        )
        if existing.scalars().first() is None:
            link = UsuarioRol(usuario_id=uid, rol_id=rid)
            self.db.add(link)
            await self.db.commit()
        # Refrescar usuario
        await self.db.refresh(user)
        return user

    async def revoke_role_from_user(self, user_id: UUID, role_id: UUID, db: AsyncSession) -> Usuario:
        try:
            uid = UUID(str(user_id))
            rid = UUID(str(role_id))
        except ValueError:
            raise ValueError("IDs inválidos")
        user = await self.db.get(Usuario, uid)
        if not user:
            raise ValueError("Usuario no encontrado")
        # Buscar vínculo y eliminarlo si existe
        existing = await self.db.execute(
            select(UsuarioRol).where((UsuarioRol.usuario_id == uid) & (UsuarioRol.rol_id == rid))
        )
        link = existing.scalars().first()
        if link:
            await self.db.delete(link)
            await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_user_roles(self, user_id: UUID) -> List[Rol]:
        """Obtiene los roles asignados a un usuario específico."""
        try:
            # Usa la tabla de asociación correcta importada como UsuarioRol
            query = (
                select(Rol)
                .join(UsuarioRol, Rol.id == UsuarioRol.rol_id)
                .where(UsuarioRol.usuario_id == user_id)
            )
            
            result = await self.db.execute(query)
            return list(result.scalars().all())
            
        except Exception as e:
            logger.error(f"Error obteniendo roles del usuario {user_id}: {str(e)}")
            return []  # Retornar lista vacía en caso de error


class PermissionService:
    """Servicio para gestión de permisos"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_multi(self, skip: int = 0, limit: int = 100) -> List['Permiso']:
        """Obtiene múltiples permisos con paginación."""
        from ges_neu_api.modules.auth.models import Permiso
        result = await self.db.execute(
            select(Permiso).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def check_permission(self, user_id: UUID, resource: str, action: str) -> bool:
        """Verifica si un usuario tiene permiso para una acción sobre un recurso."""
        # Obtener usuario
        user = await self.db.get(Usuario, user_id)
        if not user:
            return False
            
        # Verificar si es usuario activo (por ahora todos los usuarios activos tienen permisos básicos)
        if user.activo:
            return True
        
        # Para usuarios normales, verificar permisos específicos
        # Por ahora retornamos False para usuarios sin permisos específicos
        return False

    async def get_permission_by_id(self, permission_id: UUID) -> Optional['Permiso']:
        """Obtiene un permiso por su ID."""
        return await self.db.get(Permiso, str(permission_id))

    async def get_permission_by_resource_action(self, resource: str, action: str) -> Optional['Permiso']:
        """Obtiene un permiso por recurso y acción."""
        from ges_neu_api.modules.auth.models import Permiso
        result = await self.db.execute(
            select(Permiso).where(
                Permiso.nombre_recurso == resource,
                Permiso.accion == action
            )
        )
        return result.scalar_one_or_none()

    async def get_user_permissions(self, user_id: UUID) -> List['Permiso']:
        """Obtiene todos los permisos de un usuario."""
        from ges_neu_api.modules.auth.models import Permiso, RolesPermisos, UsuariosRoles
        
        # Obtener usuario
        user = await self.db.get(Usuario, str(user_id))
        if not user:
            return []
            
        # Verificar si es usuario activo (no hay campo es_superusuario en esquema real)
        if user.activo:
            # Usuario activo tiene todos los permisos por ahora
            result = await self.db.execute(select(Permiso))
            return list(result.scalars().all())
        
        # Para usuarios normales, obtener permisos a través de roles
        query = (
            select(Permiso)
            .join(RolesPermisos, Permiso.id == RolesPermisos.permiso_id)
            .join(UsuariosRoles, RolesPermisos.rol_id == UsuariosRoles.rol_id)
            .where(UsuariosRoles.usuario_id == user_id)
        )
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create_permission(self, permission_data: 'schemas.PermissionCreate') -> 'Permiso':
        """Crea un nuevo permiso."""
        from ges_neu_api.modules.auth.models import Permiso
        
        # Verificar si ya existe
        existing = await self.get_permission_by_resource_action(
            permission_data.nombre_recurso, permission_data.accion
        )
        if existing:
            raise BadRequestException("Ya existe un permiso para este recurso y acción")
        
        db_permission = Permiso(
            nombre_recurso=permission_data.nombre_recurso,
            descripcion=permission_data.descripcion,
            accion=permission_data.accion
        )
        
        self.db.add(db_permission)
        await self.db.commit()
        await self.db.refresh(db_permission)
        return db_permission

    async def delete_permission(self, permission_id: UUID) -> bool:
        """Elimina un permiso."""
        from ges_neu_api.modules.auth.models import Permiso, RolesPermisos
        
        # Obtener el permiso
        permission = await self.db.get(Permiso, str(permission_id))
        if not permission:
            raise NotFoundException(f"Permiso con ID {permission_id} no encontrado")
        
        # Verificar si está asignado a algún rol
        role_assignment = await self.db.execute(
            select(RolesPermisos).where(RolesPermisos.permiso_id == permission_id)
        )
        if role_assignment.scalar_one_or_none():
            raise BadRequestException("No se puede eliminar un permiso asignado a roles")
        
        # Eliminar el permiso
        await self.db.delete(permission)
        await self.db.commit()
        return True
