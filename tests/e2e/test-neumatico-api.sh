#!/bin/bash
# Script de testing E2E para API de Neumáticos
# Tests: unique constraint tenant-scoped, validaciones, error handling

BASE_URL="http://localhost:3000"
API_ENDPOINT="$BASE_URL/api/neumaticos"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🧪 E2E Testing - Neumatico API"
echo "================================"
echo ""

# Wait for server to be ready
echo "⏳ Esperando que el servidor esté listo..."
for i in {1..30}; do
  if curl -s "$BASE_URL" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Servidor listo${NC}"
    break
  fi
  sleep 1
done

# Test data
EMPRESA_1_ID="11111111-1111-1111-1111-111111111111"
EMPRESA_2_ID="22222222-2222-2222-2222-222222222222"
MODELO_ID="33333333-3333-3333-3333-333333333333"

echo ""
echo "📋 Test 1: Crear neumático con datos válidos"
echo "-------------------------------------------"

PAYLOAD_1='{
  "numero_serie": "TEST-E2E-001",
  "modelo_id": "'"$MODELO_ID"'",
  "dot": "2423",
  "profundidad_inicial_mm": 12.5,
  "costo_compra": 250.00,
  "fecha_compra": "2026-01-30",
  "empresa_id": "'"$EMPRESA_1_ID"'"
}'

RESPONSE_1=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
  -X POST "$API_ENDPOINT" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD_1")

HTTP_STATUS_1=$(echo "$RESPONSE_1" | grep "HTTP_STATUS" | cut -d: -f2)
BODY_1=$(echo "$RESPONSE_1" | sed '/HTTP_STATUS/d')

if [ "$HTTP_STATUS_1" == "201" ] || [ "$HTTP_STATUS_1" == "200" ]; then
  echo -e "${GREEN}✅ Test 1 PASSED${NC}"
  echo "Status: $HTTP_STATUS_1"
  echo "Response: $BODY_1" | jq '.' 2>/dev/null || echo "$BODY_1"
else
  echo -e "${RED}❌ Test 1 FAILED${NC}"
  echo "Status: $HTTP_STATUS_1"
  echo "Response: $BODY_1"
fi

echo ""
echo "📋 Test 2: Intentar duplicar numero_serie en MISMA empresa (debe fallar)"
echo "------------------------------------------------------------------------"

PAYLOAD_2='{
  "numero_serie": "TEST-E2E-001",
  "modelo_id": "'"$MODELO_ID"'",
  "dot": "2423",
  "profundidad_inicial_mm": 10.0,
  "costo_compra": 200.00,
  "fecha_compra": "2026-01-30",
  "empresa_id": "'"$EMPRESA_1_ID"'"
}'

RESPONSE_2=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
  -X POST "$API_ENDPOINT" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD_2")

HTTP_STATUS_2=$(echo "$RESPONSE_2" | grep "HTTP_STATUS" | cut -d: -f2)
BODY_2=$(echo "$RESPONSE_2" | sed '/HTTP_STATUS/d')

if [ "$HTTP_STATUS_2" == "409" ] || [ "$HTTP_STATUS_2" == "400" ]; then
  echo -e "${GREEN}✅ Test 2 PASSED - Correctamente rechazó duplicado${NC}"
  echo "Status: $HTTP_STATUS_2"
  echo "Error Message: $BODY_2" | jq '.error // .message' 2>/dev/null || echo "$BODY_2"
else
  echo -e "${RED}❌ Test 2 FAILED - Debería haber rechazado (409 o 400)${NC}"
  echo "Status: $HTTP_STATUS_2"
  echo "Response: $BODY_2"
fi

echo ""
echo "📋 Test 3: Duplicar numero_serie en EMPRESA DIFERENTE (debe permitir)"
echo "---------------------------------------------------------------------"

PAYLOAD_3='{
  "numero_serie": "TEST-E2E-001",
  "modelo_id": "'"$MODELO_ID"'",
  "dot": "2423",
  "profundidad_inicial_mm": 11.0,
  "costo_compra": 220.00,
  "fecha_compra": "2026-01-30",
  "empresa_id": "'"$EMPRESA_2_ID"'"
}'

RESPONSE_3=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
  -X POST "$API_ENDPOINT" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD_3")

HTTP_STATUS_3=$(echo "$RESPONSE_3" | grep "HTTP_STATUS" | cut -d: -f2)
BODY_3=$(echo "$RESPONSE_3" | sed '/HTTP_STATUS/d')

if [ "$HTTP_STATUS_3" == "201" ] || [ "$HTTP_STATUS_3" == "200" ]; then
  echo -e "${GREEN}✅ Test 3 PASSED - Permitió duplicado en empresa diferente${NC}"
  echo "Status: $HTTP_STATUS_3"
  echo "Response: $BODY_3" | jq '.' 2>/dev/null || echo "$BODY_3"
else
  echo -e "${RED}❌ Test 3 FAILED - Debería haber permitido${NC}"
  echo "Status: $HTTP_STATUS_3"
  echo "Response: $BODY_3"
fi

echo ""
echo "📋 Test 4: Validación de business rule - costo = 0 (debe rechazar)"
echo "------------------------------------------------------------------"

PAYLOAD_4='{
  "numero_serie": "TEST-E2E-002",
  "modelo_id": "'"$MODELO_ID"'",
  "dot": "2423",
  "profundidad_inicial_mm": 12.0,
  "costo_compra": 0,
  "fecha_compra": "2026-01-30",
  "empresa_id": "'"$EMPRESA_1_ID"'"
}'

RESPONSE_4=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
  -X POST "$API_ENDPOINT" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD_4")

HTTP_STATUS_4=$(echo "$RESPONSE_4" | grep "HTTP_STATUS" | cut -d: -f2)
BODY_4=$(echo "$RESPONSE_4" | sed '/HTTP_STATUS/d')

if [ "$HTTP_STATUS_4" == "400" ]; then
  echo -e "${GREEN}✅ Test 4 PASSED - Rechazó costo = 0${NC}"
  echo "Status: $HTTP_STATUS_4"
  echo "Error Message: $BODY_4" | jq '.error // .message' 2>/dev/null || echo "$BODY_4"
else
  echo -e "${YELLOW}⚠️  Test 4 WARNING - Status: $HTTP_STATUS_4${NC}"
  echo "Response: $BODY_4"
fi

echo ""
echo "📋 Test 5: Validación DOT inválido (semana > 53)"
echo "------------------------------------------------"

PAYLOAD_5='{
  "numero_serie": "TEST-E2E-003",
  "modelo_id": "'"$MODELO_ID"'",
  "dot": "5499",
  "profundidad_inicial_mm": 12.0,
  "costo_compra": 250.00,
  "fecha_compra": "2026-01-30",
  "empresa_id": "'"$EMPRESA_1_ID"'"
}'

RESPONSE_5=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
  -X POST "$API_ENDPOINT" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD_5")

HTTP_STATUS_5=$(echo "$RESPONSE_5" | grep "HTTP_STATUS" | cut -d: -f2)
BODY_5=$(echo "$RESPONSE_5" | sed '/HTTP_STATUS/d')

if [ "$HTTP_STATUS_5" == "400" ]; then
  echo -e "${GREEN}✅ Test 5 PASSED - Rechazó DOT inválido${NC}"
  echo "Status: $HTTP_STATUS_5"
  echo "Error Message: $BODY_5" | jq '.error // .message' 2>/dev/null || echo "$BODY_5"
else
  echo -e "${YELLOW}⚠️  Test 5 WARNING - Status: $HTTP_STATUS_5${NC}"
  echo "Response: $BODY_5"
fi

echo ""
echo "================================"
echo "🎯 Resumen de Tests"
echo "================================"
echo "Total: 5 tests ejecutados"
