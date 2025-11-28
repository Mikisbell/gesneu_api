#!/bin/bash

# Script de testing para producción - GesNeu API
BASE_URL="https://gesneu.vercel.app"

echo "=================================="
echo "🧪 Testing GesNeu API - Producción"
echo "URL: $BASE_URL"
echo "=================================="
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Contador de tests
PASSED=0
FAILED=0

# Función para test
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    
    echo -e "${YELLOW}Testing:${NC} $description"
    echo "  → $method $endpoint"
    
    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$endpoint" \
            -H "Content-Type: application/json")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "  ${GREEN}✓ PASSED${NC} (HTTP $http_code)"
        PASSED=$((PASSED + 1))
    else
        echo -e "  ${RED}✗ FAILED${NC} (HTTP $http_code)"
        echo "  Response: $body" | head -c 200
        FAILED=$((FAILED + 1))
    fi
    echo ""
}

# 1. Health Check
echo "📊 Health & Status"
echo "-------------------"
test_endpoint "GET" "/api/health" "" "Health check endpoint"

# 2. Proveedores (Suppliers)
echo "📦 Proveedores (Suppliers)"
echo "--------------------------"
test_endpoint "GET" "/api/v1/catalogos/proveedores" "" "List all suppliers"
test_endpoint "GET" "/api/v1/catalogos/proveedores?limit=5" "" "List suppliers with limit"

# 3. Almacenes (Warehouses)
echo "🏭 Almacenes (Warehouses)"
echo "-------------------------"
test_endpoint "GET" "/api/v1/catalogos/almacenes" "" "List all warehouses"
test_endpoint "GET" "/api/v1/catalogos/almacenes?limit=3" "" "List warehouses with limit"

# 4. Vehículos (Vehicles)
echo "🚗 Vehículos (Vehicles)"
echo "-----------------------"
test_endpoint "GET" "/api/v1/vehiculos" "" "List all vehicles"
test_endpoint "GET" "/api/v1/vehiculos?limit=5" "" "List vehicles with limit"

# 5. Neumáticos (Tires)
echo "🛞 Neumáticos (Tires)"
echo "----------------------"
test_endpoint "GET" "/api/v1/neumaticos" "" "List all tires"
test_endpoint "GET" "/api/v1/neumaticos?limit=5" "" "List tires with limit"

# Resumen
echo "=================================="
echo "📊 TEST SUMMARY"
echo "=================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo "Total:  $((PASSED + FAILED))"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed${NC}"
    exit 1
fi
