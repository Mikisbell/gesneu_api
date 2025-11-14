#!/bin/bash

# Script de diagnóstico para el error "Temporary failure in name resolution" en autenticación
# Ejecutar desde el directorio raíz del proyecto: ./scripts/diagnose_auth_dns.sh

echo "=== DIAGNÓSTICO DE ERROR DNS EN AUTENTICACIÓN ==="
echo "Fecha: $(date)"
echo ""

echo "1. VERIFICANDO VARIABLES DE ENTORNO DB_* DENTRO DEL CONTENEDOR API..."
echo "=================================================================="
docker-compose exec api env | grep -E '^DB_|^POSTGRES_' | sort
echo ""

echo "2. VERIFICANDO QUÉ LEE PYDANTIC SETTINGS Y LA URI RESULTANTE..."
echo "=============================================================="
docker-compose exec api python -c "
from ges_neu_api.core.config import settings
print('DB_HOST:', settings.db_host)
print('DB_PORT:', settings.db_port)
print('DB_NAME:', settings.db_name)
print('DB_USER:', settings.db_user)
print('URI completa:', settings.SQLALCHEMY_DATABASE_URI)
"
echo ""

echo "3. PROBANDO RESOLUCIÓN DNS DEL SERVICIO 'db' DESDE CONTENEDOR API..."
echo "=================================================================="
docker-compose exec api getent hosts db
if [ $? -eq 0 ]; then
    echo "✅ DNS resuelve correctamente"
else
    echo "❌ ERROR: DNS no puede resolver 'db'"
fi
echo ""

echo "4. PROBANDO CONECTIVIDAD AL PUERTO 5432 DE POSTGRESQL..."
echo "======================================================"
docker-compose exec api bash -c "
# Instalar herramientas si no están disponibles
apt-get update >/dev/null 2>&1 && apt-get install -y --no-install-recommends iputils-ping netcat-openbsd >/dev/null 2>&1

echo 'Ping a db:'
ping -c 1 db 2>/dev/null
if [ \$? -eq 0 ]; then
    echo '✅ Ping exitoso'
else
    echo '❌ Ping falló'
fi

echo ''
echo 'Conectividad al puerto 5432:'
nc -vz db 5432 2>&1
if [ \$? -eq 0 ]; then
    echo '✅ Puerto 5432 accesible'
else
    echo '❌ Puerto 5432 no accesible'
fi
"
echo ""

echo "5. VERIFICANDO ESTADO DE LOS SERVICIOS DOCKER..."
echo "=============================================="
docker-compose ps
echo ""

echo "6. PROBANDO CURL DESDE DENTRO DEL CONTENEDOR API..."
echo "================================================="
docker-compose exec api curl -s -X POST 'http://localhost:8000/api/v1/auth/token' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    -d 'grant_type=password&username=admin&password=Admin123'
echo ""
echo ""

echo "7. PROBANDO CURL DESDE EL HOST (COMO LO HACES TÚ)..."
echo "================================================="
curl -s -X POST 'http://localhost:8000/api/v1/auth/token' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    -d 'grant_type=password&username=admin&password=Admin123'
echo ""
echo ""

echo "=== DIAGNÓSTICO COMPLETADO ==="
echo ""
echo "INTERPRETACIÓN DE RESULTADOS:"
echo "- Si DB_HOST no es 'db': problema de configuración"
echo "- Si DNS no resuelve 'db': problema de red Docker"
echo "- Si puerto no es accesible: problema de PostgreSQL"
echo "- Si curl interno funciona pero externo no: problema de timing/DNS transitorio"
