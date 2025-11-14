#!/bin/bash

# Configuración
BASE_URL="http://localhost:8000"
USERNAME="admin"
PASSWORD="Admin123"

echo "🧪 INICIANDO PRUEBAS COMPLETAS DE API GESNEU"
echo "============================================="
echo "Base URL: $BASE_URL"
echo "Usuario: $USERNAME"
echo ""

# Obtener token
echo "🔐 Obteniendo token JWT..."
TOKEN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password&username=$USERNAME&password=$PASSWORD")

# Extraer token usando diferentes métodos
if command -v jq >/dev/null 2>&1; then
  TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.access_token' 2>/dev/null)
else
  # Fallback sin jq - extraer token manualmente
  TOKEN=$(echo $TOKEN_RESPONSE | sed 's/.*"access_token":"\([^"]*\)".*/\1/')
fi

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ] || [ "$TOKEN" = "$TOKEN_RESPONSE" ]; then
  echo "❌ Error obteniendo token"
  echo "Respuesta: $TOKEN_RESPONSE"
  exit 1
fi

echo "✅ Token obtenido exitosamente"
echo "Token: ${TOKEN:0:50}..."
echo ""

# Contadores
TOTAL=0
SUCCESS=0
FAILED=0

# Función para probar endpoint
test_endpoint() {
  local method=$1
  local url=$2
  local description=$3
  local auth_required=$4
  
  TOTAL=$((TOTAL + 1))
  echo -n "[$TOTAL] Testing: $description ... "
  
  if [ "$auth_required" = "true" ]; then
    response=$(curl -s -w "%{http_code}" -o /tmp/response.json \
      -H "Authorization: Bearer $TOKEN" "$BASE_URL$url" 2>/dev/null)
  else
    response=$(curl -s -w "%{http_code}" -o /tmp/response.json \
      "$BASE_URL$url" 2>/dev/null)
  fi
  
  if [[ $response -eq 200 || $response -eq 201 ]]; then
    echo "✅ Status: $response"
    SUCCESS=$((SUCCESS + 1))
    
    # Mostrar cantidad de elementos si es un array
    if command -v jq >/dev/null 2>&1; then
      count=$(jq 'length' /tmp/response.json 2>/dev/null)
      if [[ $count =~ ^[0-9]+$ ]]; then
        echo "    └─ Elementos encontrados: $count"
      fi
    fi
  else
    echo "❌ Status: $response"
    FAILED=$((FAILED + 1))
    
    # Mostrar error si existe
    if [ -f /tmp/response.json ]; then
      error=$(cat /tmp/response.json 2>/dev/null | head -c 200)
      if [ ! -z "$error" ]; then
        echo "    └─ Error: $error"
      fi
    fi
  fi
  
  sleep 0.3
}

echo "🧪 EJECUTANDO PRUEBAS DE ENDPOINTS..."
echo "====================================="

# 1. SISTEMA (sin autenticación)
echo ""
echo "🏠 MÓDULO: SISTEMA"
test_endpoint "GET" "/" "Root - Información API" "false"
test_endpoint "GET" "/health" "Health Check" "false"
test_endpoint "GET" "/api/v1/health" "Health Check V1" "false"

# 2. CATÁLOGOS (con autenticación)
echo ""
echo "📋 MÓDULO: CATÁLOGOS"
test_endpoint "GET" "/api/v1/catalogos/proveedores/" "Proveedores - Lista" "true"
test_endpoint "GET" "/api/v1/catalogos/almacenes/" "Almacenes - Lista" "true"
test_endpoint "GET" "/api/v1/catalogos/motivos-desecho/" "Motivos Desecho - Lista" "true"
test_endpoint "GET" "/api/v1/catalogos/parametros-inventario/" "Parámetros Inventario - Lista" "true"

# 3. VEHÍCULOS
echo ""
echo "🚗 MÓDULO: VEHÍCULOS"
test_endpoint "GET" "/api/v1/vehiculos/" "Vehículos - Lista" "true"
test_endpoint "GET" "/api/v1/vehiculos/tipos" "Tipos Vehículo - Lista" "true"
test_endpoint "GET" "/api/v1/vehiculos/configuraciones-eje" "Configuraciones Eje - Lista" "true"
test_endpoint "GET" "/api/v1/vehiculos/posiciones-neumatico" "Posiciones Neumático - Lista" "true"
test_endpoint "GET" "/api/v1/vehiculos/registros-odometro" "Registros Odómetro - Lista" "true"

# 4. NEUMÁTICOS
echo ""
echo "🛞 MÓDULO: NEUMÁTICOS"
test_endpoint "GET" "/api/v1/neumaticos/" "Neumáticos - Lista" "true"
test_endpoint "GET" "/api/v1/neumaticos/fabricantes/" "Fabricantes - Lista" "true"
test_endpoint "GET" "/api/v1/neumaticos/modelos/" "Modelos - Lista" "true"

# 5. INVENTARIO
echo ""
echo "📦 MÓDULO: INVENTARIO"
test_endpoint "GET" "/api/v1/inventario/" "Inventario - Lista" "true"
test_endpoint "GET" "/api/v1/inventario/movimientos/" "Movimientos - Lista" "true"

# 6. EVENTOS
echo ""
echo "📅 MÓDULO: EVENTOS"
test_endpoint "GET" "/api/v1/eventos/" "Eventos - Lista" "true"
test_endpoint "GET" "/api/v1/eventos/historial-estados/" "Historial Estados - Lista" "true"
test_endpoint "GET" "/api/v1/eventos/mediciones-profundidad" "Mediciones Profundidad - Lista" "true"

# 7. GARANTÍAS
echo ""
echo "🛡️ MÓDULO: GARANTÍAS"
test_endpoint "GET" "/api/v1/garantias/" "Garantías - Lista" "true"

# 8. ALERTAS
echo ""
echo "🚨 MÓDULO: ALERTAS"
test_endpoint "GET" "/api/v1/alertas/" "Alertas - Lista" "true"

# 9. BITÁCORAS
echo ""
echo "📝 MÓDULO: BITÁCORAS"
test_endpoint "GET" "/api/v1/bitacoras/operaciones" "Bitácora Operaciones - Lista" "true"
test_endpoint "GET" "/api/v1/bitacoras/mantenimiento" "Bitácora Mantenimiento - Lista" "true"
test_endpoint "GET" "/api/v1/bitacoras/auditoria-roles" "Auditoría Roles - Lista" "true"

# 10. MACHINE LEARNING
echo ""
echo "🤖 MÓDULO: MACHINE LEARNING"
test_endpoint "GET" "/api/v1/ml/training-data" "Datos Entrenamiento - Lista" "true"

# RESUMEN FINAL
echo ""
echo "🏁 RESUMEN FINAL DE PRUEBAS"
echo "=========================="
echo "Total endpoints probados: $TOTAL"
echo "✅ Exitosos: $SUCCESS"
echo "❌ Fallidos: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
  echo "🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!"
  echo "🚀 API GesNeu está 100% funcional"
else
  echo "⚠️  Algunos endpoints fallaron. Revisar logs arriba."
  echo "📊 Tasa de éxito: $(( SUCCESS * 100 / TOTAL ))%"
fi

echo ""
echo "📋 Para más detalles, consulta: LISTA_ENDPOINTS_TESTING.md"
echo "🌐 Documentación interactiva: $BASE_URL/docs"

# Limpiar archivos temporales
rm -f /tmp/response.json

exit $FAILED
