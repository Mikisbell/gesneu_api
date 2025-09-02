#!/usr/bin/env python3
import urllib.request
import urllib.error

try:
    req = urllib.request.Request(
        'http://127.0.0.1:8001/api/v1/catalogos/proveedores',
        headers={'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcyNTIzNzYwMH0.4lQvzJhKOaUJVhqGCJBYQHxJNGJhZGE2ZGE2ZGE2ZGE2'}
    )
    response = urllib.request.urlopen(req, timeout=5)
    print('✅ EXITO:', response.getcode())
    content = response.read().decode()[:300]
    print('📊 CONTENIDO:', content)
except urllib.error.HTTPError as e:
    print('❌ ERROR_HTTP:', e.code)
    error_details = e.read().decode()[:300]
    print('🔥 DETALLES:', error_details)
except Exception as e:
    print('💥 ERROR_CONEXION:', str(e))
