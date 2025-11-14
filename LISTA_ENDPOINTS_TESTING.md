# 🧪 Lista Completa de Endpoints para Testing - API GesNeu

**Fecha:** 8 Septiembre 2025  
**Base URL:** http://localhost:8000  
**Autenticación:** Bearer Token JWT  

## 🔐 **1. AUTENTICACIÓN**

### Obtener Token JWT
```bash
curl -X POST "http://localhost:8000/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password&username=admin&password=Admin123"
```

**Respuesta esperada:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## 🏠 **2. SISTEMA**

### Root - Información de la API
```bash
curl "http://localhost:8000/"
```

### Health Check
```bash
curl "http://localhost:8000/health"
```

### Health Check V1
```bash
curl "http://localhost:8000/api/v1/health"
```

---

## 📋 **3. CATÁLOGOS**

**Token requerido para todos los endpoints de catálogos**

### 3.1 Proveedores

#### Listar Proveedores
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/catalogos/proveedores/"
```

#### Obtener Proveedor por ID
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/catalogos/proveedores/{proveedor_id}"
```

#### Crear Proveedor
```bash
curl -X POST "http://localhost:8000/api/v1/catalogos/proveedores/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Proveedor Test",
    "tipo": "FABRICANTE",
    "ruc": "12345678901",
    "contacto_principal": "Juan Pérez",
    "telefono": "+51987654321",
    "email": "contacto@proveedor.com"
  }'
```

#### Actualizar Proveedor
```bash
curl -X PUT "http://localhost:8000/api/v1/catalogos/proveedores/{proveedor_id}" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Proveedor Actualizado",
    "tipo": "DISTRIBUIDOR"
  }'
```

#### Eliminar Proveedor
```bash
curl -X DELETE "http://localhost:8000/api/v1/catalogos/proveedores/{proveedor_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3.2 Almacenes

#### Listar Almacenes
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/catalogos/almacenes/"
```

#### Crear Almacén
```bash
curl -X POST "http://localhost:8000/api/v1/catalogos/almacenes/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "codigo": "ALM001",
    "nombre": "Almacén Principal",
    "tipo": "PRINCIPAL",
    "direccion": "Av. Industrial 123"
  }'
```

### 3.3 Motivos de Desecho

#### Listar Motivos de Desecho
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/catalogos/motivos-desecho/"
```

#### Crear Motivo de Desecho
```bash
curl -X POST "http://localhost:8000/api/v1/catalogos/motivos-desecho/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Desgaste excesivo",
    "descripcion": "Neumático con desgaste más allá del límite permitido",
    "requiere_evidencia": true
  }'
```

### 3.4 Parámetros de Inventario

#### Listar Parámetros de Inventario
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/catalogos/parametros-inventario/"
```

---

## 🚗 **4. VEHÍCULOS**

### 4.1 Tipos de Vehículo

#### Listar Tipos de Vehículo
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/vehiculos/tipos/"
```

#### Crear Tipo de Vehículo
```bash
curl -X POST "http://localhost:8000/api/v1/vehiculos/tipos/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Camión 6x4",
    "descripcion": "Camión pesado de 6 ruedas",
    "categoria_principal": "PESADO",
    "ejes_standard": 3
  }'
```

### 4.2 Vehículos

#### Listar Vehículos
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/vehiculos/"
```

#### Obtener Vehículo por ID
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/vehiculos/{vehiculo_id}"
```

#### Crear Vehículo
```bash
curl -X POST "http://localhost:8000/api/v1/vehiculos/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "numero_economico": "VEH001",
    "placa": "ABC-123",
    "marca": "Volvo",
    "modelo": "FH16",
    "anio_fabricacion": 2023,
    "tipo_vehiculo_id": "uuid-del-tipo-vehiculo"
  }'
```

### 4.3 Configuraciones de Eje

#### Listar Configuraciones de Eje
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/vehiculos/configuraciones-eje/"
```

### 4.4 Posiciones de Neumático

#### Listar Posiciones de Neumático
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/vehiculos/posiciones-neumatico/"
```

### 4.5 Registros de Odómetro

#### Listar Registros de Odómetro
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/vehiculos/registros-odometro/"
```

---

## 🛞 **5. NEUMÁTICOS**

### 5.1 Fabricantes de Neumáticos

#### Listar Fabricantes
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/neumaticos/fabricantes/"
```

#### Crear Fabricante
```bash
curl -X POST "http://localhost:8000/api/v1/neumaticos/fabricantes/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Bridgestone",
    "codigo_abreviado": "BRS",
    "pais_origen": "Japón",
    "sitio_web": "https://www.bridgestone.com"
  }'
```

### 5.2 Modelos de Neumáticos

#### Listar Modelos
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/neumaticos/modelos/"
```

#### Crear Modelo
```bash
curl -X POST "http://localhost:8000/api/v1/neumaticos/modelos/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fabricante_id": "uuid-del-fabricante",
    "nombre_modelo": "R249 Ecopia",
    "medida": "295/80R22.5",
    "profundidad_original_mm": 16.5,
    "tasa_desgaste_esperada_mm_km": 0.00012
  }'
```

### 5.3 Neumáticos

#### Listar Neumáticos
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/neumaticos/"
```

#### Obtener Neumático por ID
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/neumaticos/{neumatico_id}"
```

#### Crear Neumático
```bash
curl -X POST "http://localhost:8000/api/v1/neumaticos/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "numero_serie": "NEU001",
    "dot": "1234",
    "modelo_id": "uuid-del-modelo",
    "fecha_compra": "2025-01-15",
    "costo_compra": 850.00,
    "profundidad_remanente_actual_mm": 16.5
  }'
```

---

## 📦 **6. INVENTARIO**

### 6.1 Inventario de Neumáticos

#### Listar Inventario
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/inventario/"
```

#### Obtener Inventario por ID
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/inventario/{inventario_id}"
```

### 6.2 Movimientos de Inventario

#### Listar Movimientos
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/inventario/movimientos/"
```

---

## 📅 **7. EVENTOS**

### 7.1 Eventos de Neumáticos

#### Listar Eventos
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/eventos/"
```

#### Crear Evento
```bash
curl -X POST "http://localhost:8000/api/v1/eventos/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "neumatico_id": "uuid-del-neumatico",
    "tipo_evento": "INSTALACION",
    "fecha_evento": "2025-09-08T15:00:00Z",
    "descripcion": "Instalación en vehículo VEH001"
  }'
```

### 7.2 Historial de Estados

#### Listar Historial de Estados
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/eventos/historial-estados/"
```

### 7.3 Mediciones de Profundidad

#### Listar Mediciones
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/eventos/mediciones-profundidad/"
```

---

## 🛡️ **8. GARANTÍAS**

### 8.1 Garantías de Neumáticos

#### Listar Garantías
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/garantias/"
```

#### Crear Garantía
```bash
curl -X POST "http://localhost:8000/api/v1/garantias/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "neumatico_id": "uuid-del-neumatico",
    "fecha_inicio": "2025-01-15",
    "fecha_fin": "2026-01-15",
    "tipo_garantia": "FABRICANTE",
    "cobertura_km": 100000
  }'
```

---

## 🚨 **9. ALERTAS**

### 9.1 Alertas del Sistema

#### Listar Alertas
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/alertas/"
```

#### Crear Alerta
```bash
curl -X POST "http://localhost:8000/api/v1/alertas/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_alerta": "PROFUNDIDAD_BAJA",
    "mensaje": "Neumático con profundidad crítica",
    "nivel_severidad": "CRITICAL",
    "neumatico_id": "uuid-del-neumatico"
  }'
```

---

## 📝 **10. BITÁCORAS**

### 10.1 Bitácora de Operaciones

#### Listar Operaciones
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/bitacoras/operaciones/"
```

### 10.2 Bitácora de Mantenimiento

#### Listar Mantenimientos
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/bitacoras/mantenimiento/"
```

### 10.3 Auditoría de Roles y Usuarios

#### Listar Auditoría
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/bitacoras/auditoria-roles-usuarios/"
```

---

## 🤖 **11. MACHINE LEARNING**

### 11.1 Datos de Entrenamiento

#### Obtener Datos de Entrenamiento
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/ml/training-data"
```

#### Con Filtros
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/ml/training-data?limit=100&fabricante_id=uuid-fabricante&estado=INSTALADO"
```

---

## 🧪 **SCRIPT DE TESTING AUTOMATIZADO**

### Crear archivo test_all_endpoints.sh:

```bash
#!/bin/bash

# Configuración
BASE_URL="http://localhost:8000"
USERNAME="admin"
PASSWORD="Admin123"

# Obtener token
echo "🔐 Obteniendo token JWT..."
TOKEN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password&username=$USERNAME&password=$PASSWORD")

TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.access_token')

if [ "$TOKEN" = "null" ]; then
  echo "❌ Error obteniendo token"
  exit 1
fi

echo "✅ Token obtenido exitosamente"

# Array de endpoints para probar
declare -a endpoints=(
  "GET:/:Sistema - Root"
  "GET:/health:Sistema - Health"
  "GET:/api/v1/health:Sistema - Health V1"
  "GET:/api/v1/catalogos/proveedores/:Catálogos - Proveedores"
  "GET:/api/v1/catalogos/almacenes/:Catálogos - Almacenes"
  "GET:/api/v1/catalogos/motivos-desecho/:Catálogos - Motivos Desecho"
  "GET:/api/v1/catalogos/parametros-inventario/:Catálogos - Parámetros"
  "GET:/api/v1/vehiculos/:Vehículos - Lista"
  "GET:/api/v1/vehiculos/tipos/:Vehículos - Tipos"
  "GET:/api/v1/vehiculos/configuraciones-eje/:Vehículos - Config Eje"
  "GET:/api/v1/vehiculos/posiciones-neumatico/:Vehículos - Posiciones"
  "GET:/api/v1/neumaticos/:Neumáticos - Lista"
  "GET:/api/v1/neumaticos/fabricantes/:Neumáticos - Fabricantes"
  "GET:/api/v1/neumaticos/modelos/:Neumáticos - Modelos"
  "GET:/api/v1/inventario/:Inventario - Lista"
  "GET:/api/v1/inventario/movimientos/:Inventario - Movimientos"
  "GET:/api/v1/eventos/:Eventos - Lista"
  "GET:/api/v1/garantias/:Garantías - Lista"
  "GET:/api/v1/alertas/:Alertas - Lista"
  "GET:/api/v1/bitacoras/operaciones/:Bitácoras - Operaciones"
  "GET:/api/v1/ml/training-data:ML - Datos Entrenamiento"
)

# Probar cada endpoint
echo "🧪 Iniciando pruebas de endpoints..."
echo "=================================="

for endpoint in "${endpoints[@]}"; do
  IFS=':' read -r method url description <<< "$endpoint"
  
  echo "Testing: $description"
  
  if [[ $url == "/" || $url == "/health" ]]; then
    # Endpoints sin autenticación
    response=$(curl -s -w "%{http_code}" -o /dev/null "$BASE_URL$url")
  else
    # Endpoints con autenticación
    response=$(curl -s -w "%{http_code}" -o /dev/null \
      -H "Authorization: Bearer $TOKEN" "$BASE_URL$url")
  fi
  
  if [[ $response -eq 200 ]]; then
    echo "✅ $description - Status: $response"
  else
    echo "❌ $description - Status: $response"
  fi
  
  sleep 0.5
done

echo "=================================="
echo "🏁 Pruebas completadas"
```

### Ejecutar el script:
```bash
chmod +x test_all_endpoints.sh
./test_all_endpoints.sh
```

---

## 📊 **NOTAS IMPORTANTES**

1. **Token JWT**: Reemplaza `YOUR_TOKEN` con el token obtenido del endpoint de autenticación
2. **UUIDs**: Reemplaza los `uuid-del-*` con IDs reales de tu base de datos
3. **Datos de prueba**: Los ejemplos incluyen datos válidos según el esquema PostgreSQL
4. **Estados HTTP**: Endpoints exitosos retornan 200 (GET) o 201 (POST)
5. **Documentación**: Accede a http://localhost:8000/docs para documentación interactiva

---

**Generado automáticamente - API GesNeu v1.0.0**
