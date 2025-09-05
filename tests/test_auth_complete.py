"""Tests completos para el módulo de autenticación alineados con esquema PostgreSQL."""
import pytest
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from httpx import AsyncClient

from ges_neu_api.modules.auth.models import Usuario, Rol, Permiso, UsuariosRoles, RolesPermisos
from ges_neu_api.core.security import get_password_hash, verify_password
from tests.auth.factories import UsuarioFactory


class TestUsuarioModel:
    """Tests del modelo Usuario alineados con esquema PostgreSQL."""

    @pytest.mark.asyncio
    async def test_create_usuario_basic(self, db_session: AsyncSession):
        """Test creación básica de usuario con campos obligatorios."""
        # Crear usuario con campos obligatorios según esquema PostgreSQL
        password_hash = get_password_hash("testpassword123")
        
        usuario = Usuario(
            username="testuser001",
            password_hash=password_hash,
            activo=True
        )
        
        db_session.add(usuario)
        await db_session.commit()
        await db_session.refresh(usuario)

        # Verificar campos obligatorios
        assert usuario.id is not None
        assert usuario.username == "testuser001"
        assert usuario.password_hash is not None
        assert usuario.activo is True
        assert usuario.creado_en is not None

    @pytest.mark.asyncio
    async def test_usuario_campos_opcionales(self, db_session: AsyncSession):
        """Test campos opcionales del usuario según esquema."""
        password_hash = get_password_hash("password456")
        
        usuario = Usuario(
            username="fulluser001",
            nombre_completo="Juan Carlos Pérez López",
            email="juan.perez@empresa.com",
            password_hash=password_hash,
            activo=True
        )
        
        db_session.add(usuario)
        await db_session.commit()
        await db_session.refresh(usuario)

        # Verificar campos opcionales
        assert usuario.nombre_completo == "Juan Carlos Pérez López"
        assert usuario.email == "juan.perez@empresa.com"
        assert usuario.ultimo_login is None  # Inicialmente None
        assert usuario.creado_por is None  # Puede ser None
        assert usuario.actualizado_en is None  # Inicialmente None

    @pytest.mark.asyncio
    async def test_usuario_unique_constraints(self, db_session: AsyncSession):
        """Test constraints únicos según esquema PostgreSQL."""
        # Crear primer usuario
        usuario1 = Usuario(
            username="unique001",
            email="unique@test.com",
            password_hash=get_password_hash("pass123"),
            activo=True
        )
        db_session.add(usuario1)
        await db_session.commit()

        # Intentar crear usuario con username duplicado
        with pytest.raises(Exception):  # Should raise unique constraint violation
            usuario2 = Usuario(
                username="unique001",  # Username duplicado
                email="different@test.com",
                password_hash=get_password_hash("pass456"),
                activo=True
            )
            db_session.add(usuario2)
            await db_session.commit()

        # Intentar crear usuario con email duplicado
        with pytest.raises(Exception):  # Should raise unique constraint violation
            usuario3 = Usuario(
                username="different001",
                email="unique@test.com",  # Email duplicado
                password_hash=get_password_hash("pass789"),
                activo=True
            )
            db_session.add(usuario3)
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_password_hashing(self, db_session: AsyncSession):
        """Test hashing y verificación de contraseñas."""
        plain_password = "mi_password_seguro_123"
        password_hash = get_password_hash(plain_password)
        
        usuario = Usuario(
            username="hashtest001",
            password_hash=password_hash,
            activo=True
        )
        
        db_session.add(usuario)
        await db_session.commit()
        await db_session.refresh(usuario)

        # Verificar que el hash no es igual al password plano
        assert usuario.password_hash != plain_password
        
        # Verificar que la verificación funciona
        assert verify_password(plain_password, usuario.password_hash) is True
        assert verify_password("password_incorrecto", usuario.password_hash) is False


class TestRolModel:
    """Tests del modelo Rol alineados con esquema PostgreSQL."""

    @pytest.mark.asyncio
    async def test_create_rol_basic(self, db_session: AsyncSession):
        """Test creación básica de rol con campos obligatorios."""
        rol = Rol(
            nombre="ADMINISTRADOR",
            descripcion="Rol con acceso completo al sistema",
            es_rol_sistema=True
        )
        
        db_session.add(rol)
        await db_session.commit()
        await db_session.refresh(rol)

        # Verificar campos obligatorios
        assert rol.id is not None
        assert rol.nombre == "ADMINISTRADOR"
        assert rol.descripcion == "Rol con acceso completo al sistema"
        assert rol.es_rol_sistema is True
        assert rol.creado_en is not None

    @pytest.mark.asyncio
    async def test_rol_unique_nombre(self, db_session: AsyncSession):
        """Test constraint único en nombre de rol."""
        # Crear primer rol
        rol1 = Rol(
            nombre="OPERADOR",
            descripcion="Operador del sistema",
            es_rol_sistema=False
        )
        db_session.add(rol1)
        await db_session.commit()

        # Intentar crear rol con nombre duplicado
        with pytest.raises(Exception):  # Should raise unique constraint violation
            rol2 = Rol(
                nombre="OPERADOR",  # Nombre duplicado
                descripcion="Otro operador",
                es_rol_sistema=False
            )
            db_session.add(rol2)
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_rol_default_values(self, db_session: AsyncSession):
        """Test valores por defecto según esquema PostgreSQL."""
        rol = Rol(
            nombre="SUPERVISOR",
            descripcion="Rol de supervisión"
            # es_rol_sistema no especificado - default False
        )
        
        db_session.add(rol)
        await db_session.commit()
        await db_session.refresh(rol)

        # Verificar default aplicado
        assert rol.es_rol_sistema is False  # Default según esquema


class TestPermisoModel:
    """Tests del modelo Permiso alineados con esquema PostgreSQL."""

    @pytest.mark.asyncio
    async def test_create_permiso_basic(self, db_session: AsyncSession):
        """Test creación básica de permiso con campos obligatorios."""
        permiso = Permiso(
            nombre_recurso="usuarios",
            accion="create",
            descripcion="Crear nuevos usuarios en el sistema"
        )
        
        db_session.add(permiso)
        await db_session.commit()
        await db_session.refresh(permiso)

        # Verificar campos obligatorios
        assert permiso.id is not None
        assert permiso.nombre_recurso == "usuarios"
        assert permiso.accion == "create"
        assert permiso.descripcion == "Crear nuevos usuarios en el sistema"
        assert permiso.creado_en is not None

    @pytest.mark.asyncio
    async def test_permiso_unique_constraint(self, db_session: AsyncSession):
        """Test constraint único compuesto (nombre_recurso, accion)."""
        # Crear primer permiso
        permiso1 = Permiso(
            nombre_recurso="vehiculos",
            accion="read",
            descripcion="Leer información de vehículos"
        )
        db_session.add(permiso1)
        await db_session.commit()
    
        # Intentar crear permiso con combinación duplicada
        with pytest.raises(IntegrityError):  # Should raise unique constraint violation
            permiso2 = Permiso(
                nombre_recurso="vehiculos",  # Misma combinación
                accion="read",               # recurso + acción
                descripcion="Otra descripción"
            )
            db_session.add(permiso2)
            await db_session.commit()
        
        # Después de la excepción, hacer rollback para limpiar el estado de la sesión
        await db_session.rollback()
    
        # Crear permiso con diferente acción (debería funcionar)
        permiso3 = Permiso(
            nombre_recurso="vehiculos",
            accion="update",  # Diferente acción
            descripcion="Actualizar información de vehículos"
        )
        db_session.add(permiso3)
        await db_session.commit()
        await db_session.refresh(permiso3)
        
        assert permiso3.accion == "update"


class TestRelacionesRBAC:
    """Tests de relaciones RBAC alineadas con esquema PostgreSQL."""

    @pytest.mark.asyncio
    async def test_usuario_rol_relationship(self, db_session: AsyncSession):
        """Test relación Usuario-Rol a través de UsuariosRoles."""
        # Crear usuario
        usuario = Usuario(
            username="rbactest001",
            password_hash=get_password_hash("pass123"),
            activo=True
        )
        db_session.add(usuario)
        await db_session.commit()

        # Crear rol
        rol = Rol(
            nombre="ANALISTA",
            descripcion="Rol de análisis",
            es_rol_sistema=False
        )
        db_session.add(rol)
        await db_session.commit()

        # Crear relación usuario-rol
        usuario_rol = UsuariosRoles(
            usuario_id=usuario.id,
            rol_id=rol.id
        )
        db_session.add(usuario_rol)
        await db_session.commit()
        await db_session.refresh(usuario_rol)

        # Verificar relación
        assert usuario_rol.usuario_id == usuario.id
        assert usuario_rol.rol_id == rol.id
        assert usuario_rol.asignado_en is not None

    @pytest.mark.asyncio
    async def test_rol_permiso_relationship(self, db_session: AsyncSession):
        """Test relación Rol-Permiso a través de RolesPermisos."""
        # Crear rol
        rol = Rol(
            nombre="TECNICO",
            descripcion="Técnico especializado",
            es_rol_sistema=False
        )
        db_session.add(rol)
        await db_session.commit()

        # Crear permiso
        permiso = Permiso(
            nombre_recurso="neumaticos",
            accion="inspect",
            descripcion="Inspeccionar neumáticos"
        )
        db_session.add(permiso)
        await db_session.commit()

        # Crear relación rol-permiso
        rol_permiso = RolesPermisos(
            rol_id=rol.id,
            permiso_id=permiso.id
        )
        db_session.add(rol_permiso)
        await db_session.commit()
        await db_session.refresh(rol_permiso)

        # Verificar relación
        assert rol_permiso.rol_id == rol.id
        assert rol_permiso.permiso_id == permiso.id
        assert rol_permiso.asignado_en is not None

    @pytest.mark.asyncio
    async def test_rbac_complete_chain(self, db_session: AsyncSession):
        """Test cadena completa Usuario -> Rol -> Permiso."""
        # Crear usuario
        usuario = Usuario(
            username="chaintest001",
            password_hash=get_password_hash("chain123"),
            activo=True
        )
        db_session.add(usuario)
        await db_session.commit()

        # Crear rol
        rol = Rol(
            nombre="INSPECTOR",
            descripcion="Inspector de neumáticos",
            es_rol_sistema=False
        )
        db_session.add(rol)
        await db_session.commit()

        # Crear múltiples permisos
        permisos_data = [
            ("neumaticos", "read", "Leer información de neumáticos"),
            ("neumaticos", "inspect", "Inspeccionar neumáticos"),
            ("alertas", "create", "Crear alertas del sistema")
        ]

        permisos = []
        for recurso, accion, desc in permisos_data:
            permiso = Permiso(
                nombre_recurso=recurso,
                accion=accion,
                descripcion=desc
            )
            db_session.add(permiso)
            permisos.append(permiso)
        
        await db_session.commit()

        # Asignar rol a usuario
        usuario_rol = UsuariosRoles(
            usuario_id=usuario.id,
            rol_id=rol.id
        )
        db_session.add(usuario_rol)

        # Asignar permisos a rol
        for permiso in permisos:
            rol_permiso = RolesPermisos(
                rol_id=rol.id,
                permiso_id=permiso.id
            )
            db_session.add(rol_permiso)

        await db_session.commit()

        # Verificar cadena completa
        assert usuario_rol.usuario_id == usuario.id
        assert usuario_rol.rol_id == rol.id
        
        # Verificar que el rol tiene los 3 permisos
        from sqlalchemy import select
        result = await db_session.execute(
            select(RolesPermisos).where(RolesPermisos.rol_id == rol.id)
        )
        roles_permisos = result.scalars().all()
        assert len(roles_permisos) == 3


class TestAuthEndpoints:
    """Tests de endpoints de autenticación alineados con esquema PostgreSQL."""

    @pytest.mark.asyncio
    async def test_login_endpoint(self, client: AsyncClient, db_session: AsyncSession):
        """Test endpoint POST /api/v1/auth/login con usuario real."""
        # Crear usuario usando factory
        password = "logintest123"
        usuario = await UsuarioFactory.create(
            db=db_session,
            username="loginuser001",
            password=password,
            activo=True
        )

        # Test login
        login_data = {
            "username": usuario.username,
            "password": password
        }

        response = await client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        
        token_data = response.json()
        assert "access_token" in token_data
        assert "token_type" in token_data
        assert token_data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client: AsyncClient, db_session: AsyncSession):
        """Test login con credenciales inválidas."""
        # Crear usuario
        usuario = await UsuarioFactory.create(
            db=db_session,
            username="validuser001",
            password="correctpass",
            activo=True
        )

        # Test login con password incorrecto
        login_data = {
            "username": usuario.username,
            "password": "wrongpassword"
        }

        response = await client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 401

        # Test login con usuario inexistente
        login_data = {
            "username": "nonexistent",
            "password": "anypassword"
        }

        response = await client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_inactive_user(self, client: AsyncClient, db_session: AsyncSession):
        """Test login con usuario inactivo."""
        # Crear usuario inactivo
        usuario = await UsuarioFactory.create(
            db=db_session,
            username="inactiveuser001",
            password="testpass",
            activo=False  # Usuario inactivo
        )

        login_data = {
            "username": usuario.username,
            "password": "testpass"
        }

        response = await client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user(self, client: AsyncClient, db_session: AsyncSession):
        """Test endpoint GET /api/v1/auth/me con token válido."""
        # Crear usuario y obtener token
        password = "currentuser123"
        usuario = await UsuarioFactory.create(
            db=db_session,
            username="currentuser001",
            nombre_completo="Usuario Actual Test",
            email="current@test.com",
            password=password,
            activo=True
        )

        # Login para obtener token
        login_data = {
            "username": usuario.username,
            "password": password
        }

        login_response = await client.post("/api/v1/auth/login", data=login_data)
        assert login_response.status_code == 200
        
        token_data = login_response.json()
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}

        # Test endpoint me
        response = await client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        
        user_data = response.json()
        assert user_data["username"] == usuario.username
        assert user_data["nombre_completo"] == "Usuario Actual Test"
        assert user_data["email"] == "current@test.com"
        assert user_data["activo"] is True

    @pytest.mark.asyncio
    async def test_protected_endpoint_without_token(self, client: AsyncClient):
        """Test endpoint protegido sin token."""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_protected_endpoint_invalid_token(self, client: AsyncClient):
        """Test endpoint protegido con token inválido."""
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = await client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401


class TestAuthConstraints:
    """Tests de constraints y validaciones del esquema PostgreSQL."""

    @pytest.mark.asyncio
    async def test_usuario_required_fields(self, db_session: AsyncSession):
        """Test campos obligatorios según constraints NOT NULL."""
        # Test que username no puede ser None
        with pytest.raises(Exception):  # Should raise constraint violation
            usuario = Usuario(
                # username omitido - campo obligatorio
                password_hash=get_password_hash("test123"),
                activo=True
            )
            db_session.add(usuario)
            await db_session.commit()

        # Test que activo no puede ser None
        with pytest.raises(Exception):  # Should raise constraint violation
            usuario = Usuario(
                username="testuser",
                password_hash=get_password_hash("test123")
                # activo omitido - campo obligatorio
            )
            db_session.add(usuario)
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_usuario_field_lengths(self, db_session: AsyncSession):
        """Test longitudes de campos según esquema PostgreSQL."""
        # Test username máximo 50 caracteres
        long_username = "a" * 51  # 51 caracteres
        
        with pytest.raises(Exception):  # Should raise length constraint violation
            usuario = Usuario(
                username=long_username,
                password_hash=get_password_hash("test123"),
                activo=True
            )
            db_session.add(usuario)
            await db_session.commit()

        # Test nombre_completo máximo 200 caracteres
        long_name = "a" * 201  # 201 caracteres
        
        with pytest.raises(Exception):  # Should raise length constraint violation
            usuario = Usuario(
                username="testuser",
                nombre_completo=long_name,
                password_hash=get_password_hash("test123"),
                activo=True
            )
            db_session.add(usuario)
            await db_session.commit()

        # Test email máximo 100 caracteres
        long_email = "a" * 90 + "@test.com"  # Más de 100 caracteres
        
        with pytest.raises(Exception):  # Should raise length constraint violation
            usuario = Usuario(
                username="testuser",
                email=long_email,
                password_hash=get_password_hash("test123"),
                activo=True
            )
            db_session.add(usuario)
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_usuario_default_timestamps(self, db_session: AsyncSession):
        """Test timestamps automáticos según esquema PostgreSQL."""
        usuario = Usuario(
            username="timestamptest",
            password_hash=get_password_hash("test123"),
            activo=True
        )
        
        db_session.add(usuario)
        await db_session.commit()
        await db_session.refresh(usuario)

        # Verificar que creado_en se estableció automáticamente
        assert usuario.creado_en is not None
        assert isinstance(usuario.creado_en, datetime)
        
        # ultimo_login y actualizado_en deberían ser None inicialmente
        assert usuario.ultimo_login is None
        assert usuario.actualizado_en is None
