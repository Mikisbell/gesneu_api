# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select # Asegurar que select esté importado

# --- Importar verify_password y create_access_token ---
from core.security import create_access_token, verify_password
# --- Fin de importación ---

from core.dependencies import get_session # Usar la dependencia centralizada
from models.usuario import Usuario
from crud.crud_usuario import usuario as crud_usuario # Importar el objeto CRUD de usuario

router = APIRouter(tags=["Authentication"])

@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    # Buscar al usuario usando el CRUD
    user = await crud_usuario.get_by_username(session, username=form_data.username)

    # --- Usar la verificación segura ---
    password_ok = False
    #f user and user.password_hash: # Asegurarse que user existe y tiene hash
    if user and user.hashed_password:
        # ¡Llamar a la función de verificación!
        #password_ok = verify_password(form_data.password, user.password_hash)
        password_ok = verify_password(form_data.password, user.hashed_password)

    # --- Fin de la verificación segura ---

    # Verificar si el usuario existe Y la contraseña es correcta
    if not password_ok: # Simplificado: si no es OK (ya sea por user None o pass incorrecta)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Si la autenticación es exitosa, crear y devolver token
    access_token = create_access_token(data={"sub": user.username}) # user no puede ser None aquí
    return {"access_token": access_token, "token_type": "bearer"}