import sys
import os
import asyncio
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_eventos_service():
    """Test the eventos service directly to identify the 500 error."""
    try:
        print("🔍 Testing EventosService directly...")
        
        # Import dependencies
        from ges_neu_api.core.database import get_session
        from ges_neu_api.modules.eventos.service import EventosService
        from ges_neu_api.modules.eventos.models import EventosNeumaticos
        
        print("✅ Imports successful")
        
        # Get database session
        async for db in get_session():
            print("✅ Database session obtained")
            
            # Create service instance
            service = EventosService(db)
            print("✅ EventosService created")
            
            # Test the problematic method
            eventos = await service.get_eventos(skip=0, limit=1)
            print(f"✅ get_eventos successful: {len(eventos)} events found")
            
            if eventos:
                evento = eventos[0]
                print(f"  - Event ID: {evento.id}")
                print(f"  - Event type: {evento.tipo_evento}")
                print(f"  - Timestamp: {evento.timestamp_evento}")
            
            break
            
    except Exception as e:
        print(f"❌ Error in service test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_eventos_service())
