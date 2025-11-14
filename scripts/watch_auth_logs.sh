#!/bin/bash

# Script para monitorear logs de la API durante pruebas de autenticación
# Ejecutar en una terminal separada: ./scripts/watch_auth_logs.sh

echo "=== MONITOREANDO LOGS DE LA API DURANTE AUTENTICACIÓN ==="
echo "Presiona Ctrl+C para detener"
echo "En otra terminal, ejecuta tu curl de login para ver el stacktrace completo"
echo ""

docker-compose logs -f api
