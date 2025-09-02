import sys
sys.path.insert(0, '.')

try:
    from ges_neu_api.modules.eventos.models import EventosNeumaticos
    print("Modelo OK")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
