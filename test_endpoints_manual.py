import requests
import json

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1Njc4MDM5MH0.mjWUaVDnmznHp_a4m2zfshDquv0XRuZFqR-FGReaDQE"
headers = {'Authorization': f'Bearer {token}'}
base_url = 'http://localhost:8000'

endpoints = [
    '/api/v1/catalogos/proveedores',
    '/api/v1/catalogos/almacenes', 
    '/api/v1/catalogos/motivos-desecho',
    '/api/v1/catalogos/parametros-inventario',
    '/docs'
]

for endpoint in endpoints:
    try:
        if endpoint == '/docs':
            r = requests.get(f'{base_url}{endpoint}')
        else:
            r = requests.get(f'{base_url}{endpoint}', headers=headers)
        
        print(f"{endpoint}: {r.status_code}")
        
        if r.status_code == 200 and endpoint != '/docs':
            try:
                data = r.json()
                if isinstance(data, list):
                    print(f"  -> {len(data)} elementos")
                else:
                    print(f"  -> {type(data)}")
            except:
                print("  -> Respuesta no JSON")
        elif r.status_code != 200:
            print(f"  -> Error: {r.text[:100]}")
            
    except Exception as e:
        print(f"{endpoint}: ERROR - {e}")

print("\nPruebas completadas")
