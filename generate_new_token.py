#!/usr/bin/env python3
"""
Script para generar un nuevo token JWT válido
"""
import requests
import json

# Configuración
BASE_URL = "http://localhost:8000"

def get_new_token():
    """Obtener nuevo token JWT"""
    try:
        # Intentar login con credenciales admin
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"Login Status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            print(f"✅ Nuevo token generado:")
            print(f"Token: {token}")
            return token
        else:
            print(f"❌ Error en login: {response.text}")
            return None
            
    except Exception as e:
        print(f"💥 Error de conexión: {e}")
        return None

if __name__ == "__main__":
    print("🔑 Generando nuevo token JWT...")
    token = get_new_token()
    
    if token:
        print("\n📝 Actualiza test_all_modules_complete.py con este token:")
        print(f'JWT_TOKEN = "{token}"')
    else:
        print("\n❌ No se pudo generar token. Verifica que el servidor esté ejecutándose.")
