import requests

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1Njc4MDM5MH0.mjWUaVDnmznHp_a4m2zfshDquv0XRuZFqR-FGReaDQE"
headers = {'Authorization': f'Bearer {token}'}

# Test proveedores
print("PROVEEDORES:")
r = requests.get('http://localhost:8000/api/v1/catalogos/proveedores', headers=headers)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    print(f"Count: {len(r.json())}")
else:
    print(f"Error: {r.text[:100]}")

# Test almacenes  
print("\nALMACENES:")
r = requests.get('http://localhost:8000/api/v1/catalogos/almacenes', headers=headers)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    print(f"Count: {len(r.json())}")
else:
    print(f"Error: {r.text[:100]}")

# Test motivos
print("\nMOTIVOS DESECHO:")
r = requests.get('http://localhost:8000/api/v1/catalogos/motivos-desecho', headers=headers)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    print(f"Count: {len(r.json())}")
else:
    print(f"Error: {r.text[:100]}")

print("\nDOCS:")
r = requests.get('http://localhost:8000/docs')
print(f"Status: {r.status_code}")
