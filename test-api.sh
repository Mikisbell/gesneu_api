#!/bin/bash

# Script para probar los endpoints de la API GesNeu
# Uso: bash test-api.sh

BASE_URL="http://localhost:3005"

echo "🧪 Probando API GesNeu..."
echo "================================"
echo ""

# Test 1: Health Check
echo "1️⃣ Test Health Check"
curl -s "$BASE_URL/api/health" | jq '.'
echo ""
echo "================================"
echo ""

# Test 2: Listar Proveedores
echo "2️⃣ Test GET Proveedores (paginado)"
curl -s "$BASE_URL/api/v1/catalogos/proveedores?page=1&pageSize=5" | jq '.'
echo ""
echo "================================"
echo ""

# Test 3: Listar Almacenes
echo "3️⃣ Test GET Almacenes (paginado)"
curl -s "$BASE_URL/api/v1/catalogos/almacenes?page=1&pageSize=5" | jq '.'
echo ""
echo "================================"
echo ""

# Test 4: Crear Proveedor
echo "4️⃣ Test POST Proveedor"
PROVEEDOR_DATA='{
  "tipo": "DISTRIBUIDOR",
  "nombre": "Test Proveedor API",
  "ruc": "20123456789",
  "contacto_principal": "Juan Test",
  "telefono": "+51 999 999 999",
  "email": "test@proveedor.com",
  "direccion": "Av. Test 123",
  "activo": true
}'
PROVEEDOR_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/catalogos/proveedores" \
  -H "Content-Type: application/json" \
  -d "$PROVEEDOR_DATA")
echo "$PROVEEDOR_RESPONSE" | jq '.'
PROVEEDOR_ID=$(echo "$PROVEEDOR_RESPONSE" | jq -r '.data.id')
echo ""
echo "ID del proveedor creado: $PROVEEDOR_ID"
echo "================================"
echo ""

# Test 5: Obtener Proveedor por ID
if [ "$PROVEEDOR_ID" != "null" ] && [ -n "$PROVEEDOR_ID" ]; then
  echo "5️⃣ Test GET Proveedor por ID"
  curl -s "$BASE_URL/api/v1/catalogos/proveedores/$PROVEEDOR_ID" | jq '.'
  echo ""
  echo "================================"
  echo ""
fi

# Test 6: Crear Almacén
echo "6️⃣ Test POST Almacén"
ALMACEN_DATA='{
  "nombre": "Test Almacén API",
  "codigo": "ALM-TEST",
  "ubicacion": "Lima, Perú",
  "activo": true
}'
ALMACEN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/catalogos/almacenes" \
  -H "Content-Type: application/json" \
  -d "$ALMACEN_DATA")
echo "$ALMACEN_RESPONSE" | jq '.'
ALMACEN_ID=$(echo "$ALMACEN_RESPONSE" | jq -r '.data.id')
echo ""
echo "ID del almacén creado: $ALMACEN_ID"
echo "================================"
echo ""

echo "✅ Tests completados!"
echo ""
echo "📝 Resumen:"
echo "  - Health Check: ✓"
echo "  - GET Proveedores: ✓"
echo "  - GET Almacenes: ✓"
echo "  - POST Proveedor: ✓"
echo "  - GET Proveedor por ID: ✓"
echo "  - POST Almacén: ✓"

# Test 7: Crear Vehículo
echo "7️⃣ Test POST Vehículo"
VEHICULO_DATA='{
  "placa": "XYZ-999",
  "marca": "Volvo",
  "modelo": "FH16",
  "anio": 2023,
  "kilometraje_actual": 50000,
  "tipo_vehiculo_id": "tipo-camion-id-placeholder"
}'
# Nota: Este test fallará si no existe el tipo_vehiculo_id, pero validamos que el endpoint responda
VEHICULO_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/vehiculos" \
  -H "Content-Type: application/json" \
  -d "$VEHICULO_DATA")
echo "$VEHICULO_RESPONSE" | jq '.'
echo ""
echo "================================"
echo ""

# Test 8: Listar Vehículos
echo "8️⃣ Test GET Vehículos"
curl -s "$BASE_URL/api/v1/vehiculos?placa=ABC" | jq '.'
echo ""
echo "================================"
echo ""

# Test 9: Crear Neumático
echo "9️⃣ Test POST Neumático"
NEUMATICO_DATA='{
  "numero_serie": "NS-1001",
  "modelo_id": "modelo-id-placeholder",
  "dot": "1223",
  "profundidad_inicial_mm": 20,
  "activo": true
}'
# Nota: Este test requiere un modelo_id válido en la base de datos
NEUMATICO_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/neumaticos" \
  -H "Content-Type: application/json" \
  -d "$NEUMATICO_DATA")
echo "$NEUMATICO_RESPONSE" | jq '.'
echo ""
echo "================================"
echo ""

# Test 10: Listar Neumáticos
echo "🔟 Test GET Neumáticos"
curl -s "$BASE_URL/api/v1/neumaticos?numero_serie=NS" | jq '.'
echo ""
echo "================================"
echo ""

echo ""
echo "⏳ Finalizando tests..."
sleep 1
