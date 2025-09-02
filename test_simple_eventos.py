#!/usr/bin/env python3
"""Test simple para verificar el endpoint de eventos"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

def test_import():
    """Probar imports del módulo eventos"""
    try:
        from ges_neu_api.modules.eventos.models import EventosNeumaticos, TipoEventoNeumaticoEnum
        print("✅ Modelo EventosNeumaticos importado")
        
        from ges_neu_api.modules.eventos.schemas import EventoNeumaticoResponse
        print("✅ Schema EventoNeumaticoResponse importado")
        
        from ges_neu_api.modules.eventos.service import EventosService
        print("✅ EventosService importado")
        
        from ges_neu_api.modules.eventos.router import router
        print("✅ Router eventos importado")
        
        return True
    except Exception as e:
        print(f"❌ Error en imports: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_endpoint():
    """Probar endpoint HTTP"""
    try:
        import requests
        
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1Njg1NDQ2MX0.F0eZfWMG-BWpZ3aX7Whlnc1hbdXsSghorVSWjd4_SVA"
        
        response = requests.get(
            'http://localhost:8000/api/v1/eventos/',
            headers={'Authorization': f'Bearer {token}'},
            timeout=5
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Endpoint funcionando correctamente")
            return True
        else:
            print(f"❌ Endpoint falló con status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en test endpoint: {e}")
        return False

if __name__ == "__main__":
    print("🔍 === TEST MÓDULO EVENTOS ===")
    
    print("\n1. Probando imports...")
    imports_ok = test_import()
    
    if imports_ok:
        print("\n2. Probando endpoint...")
        endpoint_ok = test_endpoint()
        
        if endpoint_ok:
            print("\n✅ TODOS LOS TESTS PASARON")
        else:
            print("\n❌ ENDPOINT FALLÓ")
    else:
        print("\n❌ IMPORTS FALLARON")
