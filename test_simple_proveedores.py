import urllib.request
import urllib.error

try:
    req = urllib.request.Request(
        'http://127.0.0.1:8001/api/v1/catalogos/proveedores',
        headers={'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcyNTIzNzYwMH0.4lQvzJhKOaUJVhqGCJBYQHxJNGJhZGE2ZGE2ZGE2ZGE2'}
    )
    response = urllib.request.urlopen(req, timeout=5)
    print('EXITO:', response.getcode())
    print('CONTENIDO:', response.read().decode()[:200])
except urllib.error.HTTPError as e:
    print('ERROR_HTTP:', e.code)
    print('DETALLES:', e.read().decode()[:500])
except Exception as e:
    print('ERROR_CONEXION:', str(e))
