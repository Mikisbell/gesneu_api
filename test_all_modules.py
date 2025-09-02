import requests

# Token actualizado
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1Njc4MDM5MH0.mjWUaVDnmznHp_a4m2zfshDquv0XRuZFqR-FGReaDQE"
headers = {'Authorization': f'Bearer {token}'}
base_url = 'http://localhost:8000'

# Endpoints por módulo
endpoints_to_test = [
    # Neumáticos
    ('/api/v1/neumaticos/', 'Neumáticos Info'),
    ('/api/v1/neumaticos/health', 'Neumáticos Health'),
    ('/api/v1/neumaticos/fabricantes', 'Fabricantes'),
    ('/api/v1/neumaticos/modelos', 'Modelos Neumático'),
    
    # Vehículos  
    ('/api/v1/vehiculos/', 'Vehículos Lista'),
    ('/api/v1/vehiculos/tipos', 'Tipos Vehículo'),
    
    # Auth
    ('/api/v1/auth/me', 'Auth Me'),
    
    # Sistema
    ('/api/v1/sistema/parametros', 'Parámetros Sistema'),
    
    # Bitácoras
    ('/api/v1/bitacoras/mantenimiento', 'Bitácora Mantenimiento'),
]

print("=== PRUEBAS MÓDULOS API GESNEU ===")
print("Verificando otros módulos después de corrección\n")

for endpoint, name in endpoints_to_test:
    try:
        if 'auth/me' in endpoint:
            # Auth endpoints necesitan token
            r = requests.get(f'{base_url}{endpoint}', headers=headers)
        elif 'health' in endpoint or endpoint.endswith('/'):
            # Health y info pueden no necesitar auth
            r = requests.get(f'{base_url}{endpoint}')
        else:
            # Otros endpoints con auth
            r = requests.get(f'{base_url}{endpoint}', headers=headers)
            
        if r.status_code == 200:
            try:
                data = r.json()
                if isinstance(data, list):
                    print(f"✅ {name}: {r.status_code} ({len(data)} elementos)")
                else:
                    print(f"✅ {name}: {r.status_code} (objeto)")
            except:
                print(f"✅ {name}: {r.status_code} (no JSON)")
        elif r.status_code == 404:
            print(f"⚠️ {name}: {r.status_code} (endpoint no implementado)")
        elif r.status_code == 401:
            print(f"🔐 {name}: {r.status_code} (requiere auth)")
        else:
            print(f"❌ {name}: {r.status_code}")
            if r.status_code == 500:
                print(f"   Error 500: {r.text[:100]}")
                
    except Exception as e:
        print(f"💥 {name}: Error conexión - {e}")

print("\n=== RESUMEN ===")
print("Verificación completa de módulos API GesNeu")
print("Identificando posibles problemas similares al corregido")
