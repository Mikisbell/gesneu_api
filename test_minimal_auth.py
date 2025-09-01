"""
Test mínimo para diagnosticar error de autenticación
"""
import asyncio
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

async def test_minimal():
    """Test mínimo de componentes de autenticación."""
    print("=== TEST MÍNIMO DE AUTENTICACIÓN ===")
    
    try:
        # 1. Test de configuración
        print("1. Verificando configuración...")
        from ges_neu_api.core.config import settings
        print(f"   DB_HOST: {settings.DB_HOST}")
        print(f"   DB_NAME: {settings.DB_NAME}")
        print(f"   JWT_SECRET_KEY configurado: {'Sí' if settings.JWT_SECRET_KEY else 'No'}")
        
        # 2. Test de conexión BD
        print("2. Probando conexión a BD...")
        from ges_neu_api.core.database import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1"))
            print("   ✅ Conexión BD exitosa")
        
        # 3. Test de modelo Usuario
        print("3. Verificando modelo Usuario...")
        from ges_neu_api.modules.auth.models_fixed import Usuario
        print("   ✅ Modelo Usuario importado correctamente")
        
        # 4. Test de servicio de autenticación
        print("4. Probando servicio de autenticación...")
        from ges_neu_api.modules.auth.service import AuthService
        async with AsyncSessionLocal() as session:
            auth_service = AuthService(session)
            print("   ✅ AuthService creado correctamente")
        
        # 5. Test de seguridad
        print("5. Probando funciones de seguridad...")
        from ges_neu_api.core.security import get_password_hash, verify_password
        hash_test = get_password_hash("test123")
        verify_test = verify_password("test123", hash_test)
        print(f"   ✅ Hash/verify funcionando: {verify_test}")
        
        print("\n✅ TODOS LOS COMPONENTES FUNCIONAN CORRECTAMENTE")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_minimal())
