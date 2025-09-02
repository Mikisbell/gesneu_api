"""
Prueba completa de API GesNeu con obtención dinámica de token JWT.
"""
import os
import time
import json
from typing import Optional

import requests

BASE_URL = os.getenv("GESNEU_BASE_URL", "http://localhost:8001")
API_PREFIX = os.getenv("GESNEU_API_PREFIX", "/api/v1")
USERNAME = os.getenv("GESNEU_USERNAME", "admin")
PASSWORD = os.getenv("GESNEU_PASSWORD", "Admin123")


def wait_for_health(timeout_sec: int = 20) -> bool:
    url = f"{BASE_URL}/health"
    start = time.time()
    while time.time() - start < timeout_sec:
        try:
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                print(f"✅ Health OK ({url})")
                return True
        except Exception:
            pass
        time.sleep(1)
    print(f"❌ Health check no responde en {timeout_sec}s: {url}")
    return False


def get_token() -> Optional[str]:
    url = f"{BASE_URL}{API_PREFIX}/auth/token"
    # OAuth2PasswordRequestForm expects application/x-www-form-urlencoded
    form = {
        "username": USERNAME,
        "password": PASSWORD,
        # Some implementations require grant_type=password; include if backend ignores it, it's harmless
        "grant_type": "password",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    try:
        r = requests.post(url, data=form, headers=headers, timeout=8)
        if r.status_code == 200:
            data = r.json()
            token = data.get("access_token") or data.get("token")
            if token:
                print("✅ Token obtenido correctamente")
                return token
            print("❌ Respuesta 200 pero sin access_token")
        else:
            print(f"❌ Auth {url} - {r.status_code} - {r.text}")
    except Exception as e:
        print(f"❌ Error autenticando: {e}")
    return None


def test_endpoint(method: str, endpoint: str, headers: dict, data=None, desc: str = ""):
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, timeout=12)
        elif method == "POST":
            resp = requests.post(url, headers=headers, json=data, timeout=12)
        elif method == "PUT":
            resp = requests.put(url, headers=headers, json=data, timeout=12)
        elif method == "DELETE":
            resp = requests.delete(url, headers=headers, timeout=12)
        else:
            raise ValueError("Método no soportado")
    except Exception as e:
        print(f"❌ {method} {endpoint} - ERROR: {e}")
        return None

    ok = "✅" if resp.status_code < 400 else "❌"
    print(f"{ok} {method} {endpoint} - {resp.status_code} - {desc}")
    if resp.status_code >= 400:
        print(f"   Error: {resp.text}")
    return resp


def main():
    print("🚀 Iniciando pruebas API GesNeu con token dinámico")

    # 1) Esperar salud
    wait_for_health()

    # 2) Obtener token
    token = get_token()
    if not token:
        print("⚠️ No se pudo obtener token. Intentando seguir si endpoints permiten acceso.")
        headers = {"Content-Type": "application/json"}
    else:
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # 3) Pruebas por módulos (lecturas básicas)
    test_endpoint("GET", f"{API_PREFIX}/auth/users/", headers, desc="Usuarios")
    test_endpoint("GET", f"{API_PREFIX}/auth/roles/", headers, desc="Roles")

    test_endpoint("GET", f"{API_PREFIX}/catalogos/proveedores/", headers, desc="Proveedores")
    test_endpoint("GET", f"{API_PREFIX}/catalogos/almacenes/", headers, desc="Almacenes")

    test_endpoint("GET", f"{API_PREFIX}/neumaticos/", headers, desc="Neumáticos")
    test_endpoint("GET", f"{API_PREFIX}/neumaticos/modelos", headers, desc="Modelos neumático")

    test_endpoint("GET", f"{API_PREFIX}/inventario/neumaticos", headers, desc="Inventario neumáticos")

    test_endpoint("GET", f"{API_PREFIX}/garantias/vigentes", headers, desc="Garantías vigentes")

    test_endpoint("GET", f"{API_PREFIX}/alertas/", headers, desc="Alertas")

    test_endpoint("GET", f"{API_PREFIX}/bitacoras/mantenimiento", headers, desc="Bitácora mantenimiento")

    test_endpoint("GET", f"{API_PREFIX}/sistema/rutas", headers, desc="Rutas")
    test_endpoint("GET", f"{API_PREFIX}/sistema/tipos-ruta", headers, desc="Tipos ruta")

    print("\n🎯 Pruebas finalizadas")


if __name__ == "__main__":
    main()
