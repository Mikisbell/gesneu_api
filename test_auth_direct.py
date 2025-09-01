#!/usr/bin/env python3
"""
Prueba directa de autenticación usando httpx
"""
import asyncio
import httpx
import json

async def test_authentication():
    """Prueba la autenticación de forma asíncrona"""
    print("🚀 INICIANDO PRUEBAS DE AUTENTICACIÓN")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Prueba 1: Usuario que NO existe
        print("\n🔍 Prueba 1: Usuario inexistente")
        try:
            response = await client.post(
                "http://localhost:8001/api/v1/auth/token",
                data={
                    "username": "usuario_inexistente",
                    "password": "password123"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            print(f"   Status: {response.status_code}")
            if response.status_code != 200:
                error_data = response.json()
                print(f"   ✅ Mensaje de error: {error_data.get('detail')}")
            else:
                print(f"   ❌ Inesperado: debería fallar")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Prueba 2: Usuario admin con contraseña incorrecta
        print("\n🔍 Prueba 2: Admin con contraseña incorrecta")
        try:
            response = await client.post(
                "http://localhost:8001/api/v1/auth/token",
                data={
                    "username": "admin",
                    "password": "password_incorrecta"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            print(f"   Status: {response.status_code}")
            if response.status_code != 200:
                error_data = response.json()
                print(f"   ✅ Mensaje de error: {error_data.get('detail')}")
            else:
                print(f"   ❌ Inesperado: debería fallar")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Prueba 3: Usuario admin con credenciales correctas
        print("\n🔍 Prueba 3: Admin con credenciales correctas")
        try:
            response = await client.post(
                "http://localhost:8001/api/v1/auth/token",
                data={
                    "username": "admin",
                    "password": "Admin123"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                token_data = response.json()
                print(f"   ✅ ÉXITO: Token generado")
                print(f"   Tipo: {token_data.get('token_type')}")
                token = token_data.get('access_token')
                print(f"   Token: {token[:50]}...")
                
                # Prueba 4: Endpoint protegido
                print("\n🔒 Prueba 4: Endpoint protegido /auth/users/me")
                try:
                    me_response = await client.get(
                        "http://localhost:8001/api/v1/auth/users/me",
                        headers={"Authorization": f"Bearer {token}"}
                    )
                    print(f"   Status: {me_response.status_code}")
                    if me_response.status_code == 200:
                        user_data = me_response.json()
                        print(f"   ✅ Usuario: {user_data.get('username')}")
                        print(f"   ✅ Email: {user_data.get('email')}")
                        print(f"   ✅ Activo: {user_data.get('activo')}")
                    else:
                        error_data = me_response.json()
                        print(f"   ❌ Error: {error_data.get('detail')}")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    
            else:
                error_data = response.json()
                print(f"   ❌ Error inesperado: {error_data.get('detail')}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 PRUEBAS COMPLETADAS")

if __name__ == "__main__":
    asyncio.run(test_authentication())
