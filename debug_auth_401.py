#!/usr/bin/env python3
"""
Diagnóstico del error 401 en endpoint /api/v1/auth/me
"""
import requests
import json
from jose import jwt, JWTError
from datetime import datetime

# Token del test
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1NjgyNDgxOX0.1fmAvKbMorKg1sLxskLSzlspBxakPO0Y87szZVqOo8o"
BASE_URL = "http://localhost:8000"

def decode_token():
    """Decodifica el token JWT para verificar su contenido"""
    print("=== ANÁLISIS DEL TOKEN JWT ===")
    
    try:
        # Decodificar sin verificar la firma primero
        unverified = jwt.get_unverified_claims(JWT_TOKEN)
        print(f"📋 Payload del token:")
        print(f"   - Usuario (sub): {unverified.get('sub')}")
        print(f"   - Expiración (exp): {unverified.get('exp')}")
        
        # Convertir timestamp a fecha legible
        if unverified.get('exp'):
            exp_date = datetime.fromtimestamp(unverified.get('exp'))
            print(f"   - Fecha expiración: {exp_date}")
            
            # Verificar si está expirado
            now = datetime.now()
            if exp_date > now:
                print(f"   ✅ Token válido hasta: {exp_date}")
            else:
                print(f"   ❌ Token EXPIRADO desde: {exp_date}")
                return False
                
    except JWTError as e:
        print(f"❌ Error decodificando token: {e}")
        return False
        
    return True

def test_auth_endpoint():
    """Prueba el endpoint /me con el token"""
    print("\n=== TEST ENDPOINT /api/v1/auth/me ===")
    
    headers = {'Authorization': f'Bearer {JWT_TOKEN}'}
    url = f"{BASE_URL}/api/v1/auth/me"
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 401:
            print("❌ ERROR 401 - Unauthorized")
            try:
                error_detail = response.json()
                print(f"Detalle del error: {json.dumps(error_detail, indent=2, ensure_ascii=False)}")
            except:
                print(f"Respuesta raw: {response.text}")
        elif response.status_code == 200:
            print("✅ ÉXITO - Usuario autenticado")
            user_data = response.json()
            print(f"Usuario: {json.dumps(user_data, indent=2, ensure_ascii=False)}")
        else:
            print(f"⚠ Status inesperado: {response.status_code}")
            print(f"Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error en petición: {e}")

def test_login_endpoint():
    """Prueba generar un nuevo token con login"""
    print("\n=== TEST LOGIN PARA GENERAR NUEVO TOKEN ===")
    
    login_url = f"{BASE_URL}/api/v1/auth/login"
    login_data = {
        "username": "admin",
        "password": "Admin123"
    }
    
    try:
        response = requests.post(login_url, data=login_data)
        print(f"Login Status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Login exitoso")
            print(f"Nuevo token: {token_data.get('access_token', 'N/A')[:50]}...")
            
            # Probar con el nuevo token
            new_token = token_data.get('access_token')
            if new_token:
                print("\n--- Probando con nuevo token ---")
                new_headers = {'Authorization': f'Bearer {new_token}'}
                me_response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=new_headers)
                print(f"Status con nuevo token: {me_response.status_code}")
                if me_response.status_code == 200:
                    print("✅ Nuevo token funciona correctamente")
                else:
                    print(f"❌ Nuevo token también falla: {me_response.text}")
        else:
            print(f"❌ Login falló: {response.text}")
            
    except Exception as e:
        print(f"❌ Error en login: {e}")

if __name__ == "__main__":
    print("🔍 DIAGNÓSTICO ERROR 401 AUTENTICACIÓN")
    
    # 1. Analizar el token actual
    token_valid = decode_token()
    
    # 2. Probar endpoint con token actual
    test_auth_endpoint()
    
    # 3. Intentar login para obtener nuevo token
    test_login_endpoint()
    
    print("\n=== DIAGNÓSTICO COMPLETADO ===")
