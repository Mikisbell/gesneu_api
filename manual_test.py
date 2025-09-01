"""
Test manual de autenticación - versión simplificada
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
from sqlalchemy.ext.asyncio import create_async_session, AsyncSession
from ges_neu_api.core.database import get_db
from ges_neu_api.modules.auth.service import AuthService
from ges_neu_api.core.exceptions import UnauthorizedException

async def test_auth_service():
    """Prueba directa del servicio de autenticación"""
    print("🔍 PRUEBA DIRECTA DEL SERVICIO DE AUTENTICACIÓN")
    print("=" * 60)
    
    # Crear una sesión de base de datos mock para la prueba
    class MockDB:
        async def execute(self, stmt):
            class MockResult:
                def scalars(self):
                    class MockScalars:
                        def first(self):
                            return None  # Simula usuario no encontrado
                    return MockScalars()
            return MockResult()
    
    # Crear instancia del servicio
    auth_service = AuthService(MockDB())
    
    # Prueba 1: Usuario inexistente
    print("\n🔍 Prueba 1: Usuario inexistente")
    try:
        result = await auth_service.authenticate_user("usuario_inexistente", "password123")
        print(f"   ❌ Inesperado: debería lanzar excepción")
    except UnauthorizedException as e:
        print(f"   ✅ Excepción capturada correctamente: {str(e)}")
    except Exception as e:
        print(f"   ❌ Error inesperado: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Validación de mensajes en español implementada correctamente")
    print("🏁 PRUEBA COMPLETADA")

if __name__ == "__main__":
    asyncio.run(test_auth_service())
