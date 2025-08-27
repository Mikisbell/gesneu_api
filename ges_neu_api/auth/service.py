"""
Servicio de autenticación y gestión de usuarios.

Este módulo implementa las operaciones de autenticación y gestión de usuarios
definidas en los contratos correspondientes.
"""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, TYPE_CHECKING

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..core.config import settings
from ..core.database import get_session
from ..core.security import verify_password, get_password_hash
from ..core.contracts import AuthServiceContract, UserServiceContract

if TYPE_CHECKING:
    from .models.usuario import Usuario

# Configuración de logging
logger = logging.getLogger(__name__)

# Configuración de OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")

class AuthService(AuthServiceContract):
    """
    Implementación del servicio de autenticación.
    
    Proporciona funcionalidades de autenticación y generación de tokens JWT.
    """
    
    def __init__(self, db: AsyncSession):
        """Inicializa el servicio con una sesión de base de datos."""
        self.db = db
    
    async def authenticate_user(
        self,
        username: str,
        password: str
    ) -> Optional["Usuario"]:
        """
        Autentica un usuario por nombre de usuario y contraseña.
        
        Args:
            username: Nombre de usuario
            password: Contraseña en texto plano
            
        Returns:
            Usuario autenticado o None si la autenticación falla
        """
        logger.info(f"Intentando autenticar usuario: {username}")
        
        try:
            # Buscar usuario por nombre de usuario
            from .models.usuario import Usuario  # Importación local para evitar dependencias circulares
            
            result = await self.db.execute(
                select(Usuario).where(Usuario.username == username)
            )
            user = result.scalars().first()
            
            if not user:
                logger.warning(f"Usuario no encontrado: {username}")
                return None
                
            if not user.activo:
                logger.warning(f"Usuario inactivo: {username}")
                return None
                
            # Verificar contraseña
            logger.debug(f"Verificando contraseña para usuario: {username}")
            if not verify_password(password, user.password_hash):
                logger.warning(f"Contraseña incorrecta para usuario: {username}")
                return None
                
            # Actualizar último inicio de sesión
            user.ultimo_login = datetime.utcnow()
            await self.db.commit()
            logger.info(f"Autenticación exitosa para usuario: {username}")
            return user
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error durante la autenticación para {username}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error durante la autenticación"
            )
    
    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Crea un token de acceso JWT.
        
        Args:
            data: Datos a incluir en el token
            expires_delta: Tiempo de expiración del token
            
        Returns:
            Token JWT codificado
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            
        to_encode.update({"exp": expire})
        
        try:
            encoded_jwt = jwt.encode(
                to_encode, 
                settings.SECRET_KEY, 
                algorithm=settings.ALGORITHM
            )
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error al crear token de acceso: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al generar el token de acceso"
            )
    
    async def get_current_user(self, token: str) -> "Usuario":
        """
        Obtiene el usuario actual a partir de un token JWT.
        
        Args:
            token: Token JWT
            
        Returns:
            Usuario autenticado
            
        Raises:
            HTTPException: Si el token es inválido o el usuario no existe
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudieron validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            # Decodificar el token
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            username: str = payload.get("sub")
            if username is None:
                logger.warning("Token JWT sin campo 'sub'")
                raise credentials_exception
                
        except JWTError as e:
            logger.warning(f"Error al decodificar token JWT: {str(e)}")
            raise credentials_exception
        
        # Buscar el usuario en la base de datos
        try:
            from .models.usuario import Usuario  # Importación local
            
            result = await self.db.execute(
                select(Usuario).where(Usuario.username == username)
            )
            user = result.scalars().first()
            
            if user is None:
                logger.warning(f"Usuario no encontrado en la base de datos: {username}")
                raise credentials_exception
                
            return user
            
        except Exception as e:
            logger.error(f"Error al obtener usuario {username}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al obtener información del usuario"
            )


class UserService(UserServiceContract):
    """
    Implementación del servicio de usuarios.
    
    Proporciona operaciones CRUD para la gestión de usuarios.
    """
    
    def __init__(self, db: AsyncSession):
        """Inicializa el servicio con una sesión de base de datos."""
        self.db = db
    
    async def get_user_by_id(self, user_id: int) -> Optional["Usuario"]:
        """Obtiene un usuario por su ID."""
        from .models.usuario import Usuario  # Importación local
        
        result = await self.db.execute(
            select(Usuario).where(Usuario.id == user_id)
        )
        return result.scalars().first()
    
    async def get_user_by_username(self, username: str) -> Optional["Usuario"]:
        """Obtiene un usuario por su nombre de usuario."""
        from .models.usuario import Usuario  # Importación local
        
        result = await self.db.execute(
            select(Usuario).where(Usuario.username == username)
        )
        return result.scalars().first()
    
    async def create_user(self, user_data: Dict[str, Any]) -> "Usuario":
        """Crea un nuevo usuario."""
        from .models.usuario import Usuario  # Importación local
        
        try:
            hashed_password = get_password_hash(user_data["password"])
            db_user = Usuario(
                username=user_data["username"],
                email=user_data["email"],
                password_hash=hashed_password,
                nombre=user_data.get("nombre"),
                apellido=user_data.get("apellido"),
                activo=user_data.get("activo", True)
            )
            
            self.db.add(db_user)
            await self.db.commit()
            await self.db.refresh(db_user)
            
            return db_user
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error al crear usuario: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al crear el usuario"
            )
    
    async def update_user(
        self, 
        user_id: int, 
        user_data: Dict[str, Any]
    ) -> Optional["Usuario"]:
        """Actualiza un usuario existente."""
        from .models.usuario import Usuario  # Importación local
        
        try:
            # Obtener el usuario existente
            result = await self.db.execute(
                select(Usuario).where(Usuario.id == user_id)
            )
            db_user = result.scalars().first()
            
            if not db_user:
                return None
            
            # Actualizar campos
            for field, value in user_data.items():
                if field == "password" and value is not None:
                    db_user.password_hash = get_password_hash(value)
                elif hasattr(db_user, field):
                    setattr(db_user, field, value)
            
            db_user.actualizado_en = datetime.utcnow()
            
            await self.db.commit()
            await self.db.refresh(db_user)
            
            return db_user
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error al actualizar usuario {user_id}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al actualizar el usuario"
            )
    
    async def delete_user(self, user_id: int) -> bool:
        """Elimina un usuario."""
        from .models.usuario import Usuario  # Importación local
        
        try:
            result = await self.db.execute(
                select(Usuario).where(Usuario.id == user_id)
            )
            db_user = result.scalars().first()
            
            if not db_user:
                return False
            
            # En lugar de eliminar físicamente, marcamos como inactivo
            db_user.activo = False
            db_user.actualizado_en = datetime.utcnow()
            
            await self.db.commit()
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error al eliminar usuario {user_id}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar el usuario"
            )


# Función de compatibilidad para dependencias existentes
async def get_current_user(
    db: AsyncSession = Depends(get_session),
    token: str = Depends(oauth2_scheme)
) -> "UsuarioRead":
    """
    Obtiene el usuario actual a partir del token JWT.
    
    Esta función se mantiene por compatibilidad con el código existente.
    Se recomienda usar AuthService.get_current_user en nuevo código.
    """
    auth_service = AuthService(db)
    return await auth_service.get_current_user(token)
