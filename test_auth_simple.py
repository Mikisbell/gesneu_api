"""
Test simple de autenticación sin base de datos
"""
import asyncio
from ges_neu_api.modules.auth.service import AuthService
from ges_neu_api.core.database import AsyncSessionLocal
from ges_neu_api.modules.auth.models_fixed import Usuario
from ges_neu_api.core.security import get_password_hash
from sqlalchemy import text

async def test_auth_flow():
    """Prueba el flujo completo de autenticación."""
    try:
        # Crear sesión de BD
        async with AsyncSessionLocal() as session:
            print("✅ Conexión a BD establecida")
            
            # Verificar si existe usuario admin
            result = await session.execute(
                text("SELECT COUNT(*) FROM usuarios WHERE username = 'admin'")
            )
            count = result.scalar()
            print(f"✅ Usuarios 'admin' encontrados: {count}")
            
            if count == 0:
                # Crear usuario admin de prueba
                admin_user = Usuario(
                    username="admin",
                    email="admin@gesneu.com",
                    password_hash=get_password_hash("Admin123"),
                    activo=True,
                    es_superusuario=True
                )
                session.add(admin_user)
                await session.commit()
                print("✅ Usuario admin creado")
            
            # Probar autenticación
            auth_service = AuthService(session)
            user = await auth_service.authenticate_user("admin", "Admin123")
            print(f"✅ Usuario autenticado: {user.username}")
            
            # Crear token
            token = auth_service.create_access_token({"sub": user.username})
            print(f"✅ Token creado: {token[:50]}...")
            
            return True
            
    except Exception as e:
        print(f"❌ Error en test de autenticación: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_auth_flow())
