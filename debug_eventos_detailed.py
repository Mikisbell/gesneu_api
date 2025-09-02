#!/usr/bin/env python3
"""
Debug detallado del módulo eventos para identificar causa exacta del error 500.
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

def test_imports():
    """Probar imports del módulo eventos."""
    try:
        print("🔍 Probando imports...")
        
        # Test import models
        from ges_neu_api.modules.eventos.models import EventosNeumaticos
        print("✅ EventosNeumaticos importado")
        
        # Test import enums
        from ges_neu_api.modules.eventos.models import TipoEventoNeumaticoEnum
        print("✅ TipoEventoNeumaticoEnum importado")
        
        # Test import service
        from ges_neu_api.modules.eventos.service import EventosService
        print("✅ EventosService importado")
        
        # Test database connection
        from ges_neu_api.core.database import engine
        print("✅ Database engine importado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en imports: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_model_creation():
    """Probar creación de instancia del modelo."""
    try:
        from ges_neu_api.modules.eventos.models import EventosNeumaticos
        from uuid import uuid4
        from datetime import datetime
        
        print("\n🔍 Probando creación de modelo...")
        
        # Crear instancia básica
        evento = EventosNeumaticos(
            neumatico_id=uuid4(),
            tipo_evento="COMPRA",
            usuario_id=uuid4()
        )
        print("✅ Modelo EventosNeumaticos creado exitosamente")
        print(f"  - ID: {evento.id}")
        print(f"  - Tipo: {evento.tipo_evento}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando modelo: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_database_table():
    """Probar si la tabla eventos_neumaticos existe."""
    try:
        from ges_neu_api.core.database import engine
        import asyncio
        
        print("\n🔍 Probando existencia de tabla...")
        
        async def check_table():
            async with engine.begin() as conn:
                result = await conn.execute(
                    "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'eventos_neumaticos'"
                )
                count = result.scalar()
                return count > 0
        
        exists = asyncio.run(check_table())
        if exists:
            print("✅ Tabla eventos_neumaticos existe en BD")
        else:
            print("❌ Tabla eventos_neumaticos NO existe en BD")
        
        return exists
        
    except Exception as e:
        print(f"❌ Error verificando tabla: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Iniciando diagnóstico detallado del módulo Eventos...\n")
    
    success = True
    success &= test_imports()
    success &= test_model_creation()
    success &= test_database_table()
    
    print(f"\n📊 Resultado final: {'✅ EXITOSO' if success else '❌ FALLÓ'}")
