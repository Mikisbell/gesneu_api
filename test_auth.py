#!/usr/bin/env python3
"""
Script para probar la autenticación de la API GesNeu
"""
import requests
import json

BASE_URL = "http://localhost:8001/api/v1"

def test_auth(username, password, description):
    """Prueba la autenticación con las credenciales dadas"""
    print(f"\n🔍 Probando: {description}")
    print(f"   Usuario: {username}")
    print(f"   Contraseña: {'*' * len(password)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/token",
            data={
                "username": username,
                "password": password
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            },
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print(f"   ✅ ÉXITO: Token generado")
            print(f"   Tipo: {token_data.get('token_type', 'N/A')}")
            print(f"   Token: {token_data.get('access_token', 'N/A')[:50]}...")
            return token_data.get('access_token')
        else:
            try:
                error_data = response.json()
                print(f"   ❌ ERROR: {error_data.get('detail', 'Error desconocido')}")
            except:
                print(f"   ❌ ERROR: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("   ❌ ERROR: No se puede conectar al servidor")
        print("   💡 Asegúrate de que el servidor esté ejecutándose en localhost:8001")
        return None
    except Exception as e:
        print(f"   ❌ ERROR INESPERADO: {e}")
        return None

def test_protected_endpoint(token):
    """Prueba un endpoint protegido con el token"""
    if not token:
        print("\n❌ No hay token para probar endpoint protegido")
        return
        
    print(f"\n🔒 Probando endpoint protegido /auth/users/me")
    
    try:
        response = requests.get(
            f"{BASE_URL}/auth/users/me",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"   ✅ ÉXITO: Información del usuario obtenida")
            print(f"   Usuario: {user_data.get('username', 'N/A')}")
            print(f"   Email: {user_data.get('email', 'N/A')}")
            print(f"   Activo: {user_data.get('activo', 'N/A')}")
        else:
            try:
                error_data = response.json()
                print(f"   ❌ ERROR: {error_data.get('detail', 'Error desconocido')}")
            except:
                print(f"   ❌ ERROR: {response.text}")
                
    except Exception as e:
        print(f"   ❌ ERROR: {e}")

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DE AUTENTICACIÓN API GESNEU")
    print("=" * 60)
    
    # Prueba 1: Usuario que NO existe
    test_auth("usuario_inexistente", "password123", "Usuario que NO existe")
    
    # Prueba 2: Usuario admin con contraseña incorrecta
    test_auth("admin", "password_incorrecta", "Usuario admin con contraseña incorrecta")
    
    # Prueba 3: Usuario admin con credenciales correctas
    token = test_auth("admin", "Admin123", "Usuario admin con credenciales correctas")
    
    # Prueba 4: Endpoint protegido con token válido
    if token:
        test_protected_endpoint(token)
    
    print("\n" + "=" * 60)
    print("🏁 PRUEBAS COMPLETADAS")
