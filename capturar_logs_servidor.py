#!/usr/bin/env python3
"""
Capturar logs detallados del servidor para diagnosticar error 500
"""
import subprocess
import time
import threading
import requests
import sys

def hacer_peticion_test():
    """Hacer petición de prueba después de un delay"""
    time.sleep(3)  # Esperar a que el servidor arranque
    
    try:
        print("\n🔥 HACIENDO PETICIÓN DE PRUEBA...")
        url = "http://127.0.0.1:8001/api/v1/catalogos/proveedores"
        headers = {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcyNTIzNzYwMH0.4lQvzJhKOaUJVhqGCJBYQHxJNGJhZGE2ZGE2ZGE2ZGE2"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f"✅ Respuesta: {response.status_code}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en petición: {e}")
    except Exception as e:
        print(f"💥 Error general: {e}")

def main():
    print("🚀 INICIANDO SERVIDOR CON LOGS DETALLADOS")
    print("=" * 50)
    
    # Iniciar thread para hacer petición de prueba
    test_thread = threading.Thread(target=hacer_peticion_test)
    test_thread.daemon = True
    test_thread.start()
    
    # Ejecutar servidor con logs detallados
    try:
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "ges_neu_api.main:app",
            "--host", "127.0.0.1",
            "--port", "8001", 
            "--log-level", "debug",
            "--access-log"
        ]
        
        print(f"📋 Comando: {' '.join(cmd)}")
        print("🔍 Observando logs del servidor...")
        print("=" * 50)
        
        # Ejecutar y capturar salida en tiempo real
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Leer logs línea por línea
        for line in process.stdout:
            print(line.rstrip())
            
            # Terminar después de capturar el error
            if "500" in line or "Internal Server Error" in line:
                print("\n🔥 ERROR 500 DETECTADO - TERMINANDO CAPTURA")
                process.terminate()
                break
                
    except KeyboardInterrupt:
        print("\n⏹️  Captura de logs interrumpida por usuario")
    except Exception as e:
        print(f"❌ Error ejecutando servidor: {e}")

if __name__ == "__main__":
    main()
