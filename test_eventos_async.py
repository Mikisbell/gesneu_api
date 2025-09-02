#!/usr/bin/env python3
"""
Test async del servicio eventos para diagnosticar error 500.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath('.'))

async def test_eventos_service():
    """Test directo del servicio eventos."""
    try:
        from ges_neu_api.core.database import get_session
        from ges_neu_api.modules.eventos.service import EventosService
        
        print("🔍 Probando EventosService...")
        
        # Obtener sesión async
        async for db in get_session():
            service = EventosService(db)
            
            # Test get_eventos
            eventos = await service.get_eventos(skip=0, limit=1)
            print(f"✅ get_eventos exitoso: {len(eventos)} eventos")
            
            break  # Solo una iteración
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_eventos_service())
