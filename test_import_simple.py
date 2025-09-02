import sys
sys.path.insert(0, '.')

print("Testing imports step by step...")

try:
    from ges_neu_api.modules.eventos.models import TipoEventoNeumaticoEnum
    print("✅ TipoEventoNeumaticoEnum imported")
except Exception as e:
    print(f"❌ TipoEventoNeumaticoEnum error: {e}")

try:
    from ges_neu_api.modules.eventos.models import EstadoNeumaticoEnumDestino
    print("✅ EstadoNeumaticoEnumDestino imported")
except Exception as e:
    print(f"❌ EstadoNeumaticoEnumDestino error: {e}")

try:
    from ges_neu_api.modules.eventos.models import EventosNeumaticos
    print("✅ EventosNeumaticos imported")
except Exception as e:
    print(f"❌ EventosNeumaticos error: {e}")
    import traceback
    traceback.print_exc()
