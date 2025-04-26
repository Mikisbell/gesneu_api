from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from core.security import create_access_token
from database import get_session
from models.usuario import Usuario
# En tus routers
from database import get_session

async def my_endpoint(
    session: AsyncSession = Depends(get_session)
):
    # Usar la sesión
    result = await session.execute(...)
    
router = APIRouter(tags=["Authentication"])

@router.post("/token")
async def login(
    username: str,
    password: str,
    session: AsyncSession = Depends(get_session)
):
    user = await Usuario.get_by_username(session, username)
    
    if not user or not user.verify_password(password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    return {
        "access_token": create_access_token({"sub": user.username}),
        "token_type": "bearer"
    }