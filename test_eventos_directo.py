#!/usr/bin/env python3
"""
Test directo del endpoint eventos para diagnosticar error 500.
"""
import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath('.'))

async def test_eventos_directo():
    """Test directo del servicio de eventos."""
    try:
        from ges_neu_api.core.database import get_session_sync
        from ges_neu_api.modules.eventos.service import EventosService
        
        print("🔍 Probando EventosService directamente...")
        
        # Obtener sesión de BD
        db = next(get_session_sync())
        service = EventosService(db)
        
        # Probar get_eventos
        eventos = await service.get_eventos(skip=0, limit=5)
        print(f"✅ get_eventos exitoso: {len(eventos)} eventos encontrados")
        
        for evento in eventos:
            print(f"  - ID: {evento.id}, Tipo: {evento.tipo_evento}")
            
    except Exception as e:
        print(f"❌ Error en test directo: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_eventos_directo())
