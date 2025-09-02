#!/usr/bin/env python3
"""
Script para diagnosticar el error 500 en el módulo de Eventos.
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ges_neu_api.core.database import get_session
from ges_neu_api.modules.eventos.service import EventosService
from ges_neu_api.modules.eventos.models import EventosNeumaticos

async def test_eventos_service():
    """Probar el servicio de eventos directamente."""
    print("🔍 Diagnosticando servicio de Eventos...")
    
    try:
        # Obtener sesión de BD
        async for session in get_session():
            print("✅ Conexión a BD establecida")
            
            # Crear servicio
            service = EventosService(session)
            print("✅ Servicio EventosService creado")
            
            # Probar método get_eventos
            eventos = await service.get_eventos(skip=0, limit=10)
            print(f"✅ Método get_eventos ejecutado: {len(eventos)} eventos encontrados")
            
            # Verificar modelo
            print("✅ Modelo EventosNeumaticos importado correctamente")
            
            break
            
    except Exception as e:
        print(f"❌ Error en servicio: {str(e)}")
        import traceback
        print(traceback.format_exc())

async def test_eventos_model():
    """Probar el modelo de eventos."""
    print("\n🔍 Diagnosticando modelo de Eventos...")
    
    try:
        from ges_neu_api.modules.eventos.models import EventosNeumaticos, TipoEventoNeumaticoEnum
        print("✅ Imports del modelo exitosos")
        
        # Verificar tabla
        print(f"✅ Tabla: {EventosNeumaticos.__tablename__}")
        
        # Verificar campos principales
        campos = ['id', 'neumatico_id', 'tipo_evento', 'timestamp_evento', 'usuario_id']
        for campo in campos:
            if hasattr(EventosNeumaticos, campo):
                print(f"✅ Campo {campo}: OK")
            else:
                print(f"❌ Campo {campo}: FALTA")
                
    except Exception as e:
        print(f"❌ Error en modelo: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(test_eventos_model())
    asyncio.run(test_eventos_service())
