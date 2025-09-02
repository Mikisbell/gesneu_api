import sys
sys.path.insert(0, '.')

try:
    from ges_neu_api.modules.eventos.models import EventosNeumaticos
    print("✅ EventosNeumaticos model imported")
    
    # Check if the model has all required fields
    fields = EventosNeumaticos.__fields__
    print(f"Model has {len(fields)} fields")
    
    # Check specific problematic fields
    required_fields = ['id', 'neumatico_id', 'tipo_evento', 'timestamp_evento', 'usuario_id']
    for field in required_fields:
        if field in fields:
            print(f"✅ {field}: OK")
        else:
            print(f"❌ {field}: MISSING")
            
except Exception as e:
    print(f"❌ Model import error: {e}")
    import traceback
    traceback.print_exc()

# Test direct database query
try:
    import asyncio
    from ges_neu_api.core.database import engine
    
    async def test_db():
        async with engine.begin() as conn:
            result = await conn.execute("SELECT COUNT(*) FROM eventos_neumaticos")
            count = result.scalar()
            print(f"✅ eventos_neumaticos table has {count} records")
    
    asyncio.run(test_db())
    
except Exception as e:
    print(f"❌ Database test error: {e}")
    import traceback
    traceback.print_exc()
