# tests/helpers.py
import uuid
import pytest # Necesario si usas pytest.fail
from httpx import AsyncClient
from fastapi import status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.usuario import Usuario
from core.security import get_password_hash, verify_password # Asegúrate que verify_password esté si la usas aquí

async def create_user_and_get_token(
    client: AsyncClient,
    session: AsyncSession, # Puede ser SQLite o PostgreSQL
    user_suffix: str,
    rol: str = "OPERADOR", # Rol por defecto
    activo: bool = True
) -> tuple[str, dict]:
    """
    Crea un usuario único para pruebas y devuelve su ID y headers con token.
    Funciona con cualquier sesión asíncrona (SQLite o PostgreSQL).
    """
    user_password = f"password_{user_suffix}"
    hashed_password = get_password_hash(user_password)
    username = f"testuser_{user_suffix}_{uuid.uuid4().hex[:4]}" # Añadir UUID para evitar colisiones entre ejecuciones
    email = f"{username}@example.com"

    # Verificar si ya existe un usuario con ese username (menos probable con UUID, pero buena práctica)
    stmt_user = select(Usuario).where(Usuario.username == username)
    existing_user = (await session.exec(stmt_user)).first()

    user: Usuario
    if not existing_user:
        user = Usuario(
            username=username,
            email=email,
            password_hash=hashed_password,
            activo=activo,
            rol=rol
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        user_id = str(user.id)
    else:
        # Si existiera (raro), actualizar hash/estado y obtener ID
        # Opcional: Podrías lanzar un error si no esperas que exista
        existing_user.password_hash = hashed_password
        existing_user.activo = activo
        existing_user.rol = rol
        session.add(existing_user)
        await session.commit()
        await session.refresh(existing_user)
        user_id = str(existing_user.id)
        user = existing_user # Usar para login

    # Obtener token
    login_data = {"username": user.username, "password": user_password}
    response_token = await client.post("/auth/token", data=login_data)

    if response_token.status_code != status.HTTP_200_OK:
         # Usar pytest.fail para detener la prueba si falla el helper crítico
         pytest.fail(
             f"Fallo al obtener token en helper genérico para user {user.username}: "
             f"{response_token.status_code} {response_token.text}"
        )

    access_token = response_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    return user_id, headers

# Puedes añadir aquí otros helpers comunes, como los de crear proveedores, modelos, etc.
# adaptándolos para que acepten la `session` como argumento. Por ejemplo:
# async def create_test_modelo(session: AsyncSession, fabricante_id: uuid.UUID, sufijo: str) -> ModeloNeumatico: ...
# async def create_test_vehiculo_posicion(session: AsyncSession, sufijo: str) -> tuple[uuid.UUID, uuid.UUID]: ...