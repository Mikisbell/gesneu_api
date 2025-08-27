#!/bin/bash

# Configuración
API_URL="http://localhost:8001"
ADMIN_USERNAME="admin@example.com"
ADMIN_PASSWORD="admin123"

# Función para hacer peticiones a la API
api_request() {
    local method=$1
    local endpoint=$2
    local data=$3
    
    curl -s -X $method \
        -H "Content-Type: application/json" \
        -d "$data" \
        "$API_URL$endpoint"
}

# 1. Iniciar sesión como administrador
echo "🔑 Iniciando sesión como administrador..."
TOKEN=$(curl -s -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$ADMIN_USERNAME&password=$ADMIN_PASSWORD" \
  "$API_URL/auth/token" | jq -r '.access_token')

if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
    echo "❌ Error al iniciar sesión. Asegúrate de que el usuario administrador existe y las credenciales son correctas."
    exit 1
fi

echo "✅ Sesión iniciada correctamente"
echo "🔑 Token: ${TOKEN:0:20}..."

# 2. Crear un rol de prueba
ROLE_DATA='{"nombre": "rol_prueba", "descripcion": "Rol para pruebas de RBAC"}'
echo "\n🔄 Creando rol de prueba..."
ROLE_RESPONSE=$(api_request "POST" "/auth/roles/" "$ROLE_DATA")
echo "Respuesta: $ROLE_RESPONSE"

# 3. Crear un permiso de prueba
PERMISSION_DATA='{"nombre_recurso": "recurso_prueba", "accion": "leer", "descripcion": "Permiso para leer recurso de prueba"}'
echo "\n🔄 Creando permiso de prueba..."
PERM_RESPONSE=$(api_request "POST" "/auth/permisos/" "$PERMISSION_DATA")
echo "Respuesta: $PERM_RESPONSE"

# 4. Asignar permiso al rol
# Primero necesitamos los IDs del rol y permiso recién creados
# En un entorno real, deberías extraer estos IDs de las respuestas anteriores
# Por simplicidad, asumiremos que los IDs son 1
ROLE_ID=1
PERM_ID=1

ASSIGN_DATA="{\"permiso_id\": $PERM_ID}"
echo "\n🔗 Asignando permiso al rol..."
ASSIGN_RESPONSE=$(curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$ASSIGN_DATA" \
  "$API_URL/auth/roles/$ROLE_ID/permisos/")
echo "Respuesta: $ASSIGN_RESPONSE"

# 5. Crear un usuario de prueba
USER_DATA='{"email": "usuario_prueba@example.com", "password": "password123", "nombre_completo": "Usuario de Prueba"}'
echo "\n👤 Creando usuario de prueba..."
USER_RESPONSE=$(api_request "POST" "/auth/register" "$USER_DATA")
echo "Respuesta: $USER_RESPONSE"

# 6. Asignar rol al usuario
USER_ID=1  # Asumimos que el ID del usuario es 1
ASSIGN_ROLE_DATA="{\"rol_id\": $ROLE_ID}"
echo "\n🔗 Asignando rol al usuario..."
ASSIGN_ROLE_RESPONSE=$(curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$ASSIGN_ROLE_DATA" \
  "$API_URL/auth/usuarios/$USER_ID/roles/")
echo "Respuesta: $ASSIGN_ROLE_RESPONSE"

echo "\n✅ Prueba de RBAC completada. Verifica los resultados en la base de datos o en la aplicación."
