# 📋 GesNeu API - Documentación de Endpoints

## 🏥 Health Check

### GET /api/health
Verifica el estado de la API y la conexión con la base de datos.

**Respuesta exitosa (200):**
```json
{
  "status": "ok",
  "message": "GesNeu API - Next.js + Supabase",
  "timestamp": "2025-11-14T05:00:00.000Z",
  "version": "1.0.0",
  "database": {
    "connected": true,
    "message": "PostgreSQL conectado exitosamente"
  }
}
```

---

## 📦 Catálogos - Proveedores

### GET /api/v1/catalogos/proveedores
Lista todos los proveedores con paginación.

**Query Parameters:**
- `page` (opcional): Número de página (default: 1)
- `pageSize` (opcional): Tamaño de página (default: 10)
- `activo` (opcional): Filtrar por estado (true/false)

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "tipo": "FABRICANTE",
      "nombre": "Proveedor Ejemplo",
      "ruc": "20123456789",
      "contacto_principal": "Juan Pérez",
      "telefono": "+51 999 999 999",
      "email": "contacto@proveedor.com",
      "direccion": "Av. Principal 123",
      "activo": true,
      "creado_en": "2025-11-14T05:00:00.000Z",
      "actualizado_en": null
    }
  ],
  "pagination": {
    "page": 1,
    "pageSize": 10,
    "total": 50,
    "totalPages": 5
  }
}
```

### POST /api/v1/catalogos/proveedores
Crea un nuevo proveedor.

**Body (JSON):**
```json
{
  "tipo": "FABRICANTE",
  "nombre": "Nuevo Proveedor",
  "ruc": "20987654321",
  "contacto_principal": "María García",
  "telefono": "+51 888 888 888",
  "email": "maria@proveedor.com",
  "direccion": "Calle Secundaria 456",
  "activo": true
}
```

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "data": { /* objeto proveedor creado */ },
  "message": "Proveedor creado exitosamente"
}
```

### GET /api/v1/catalogos/proveedores/[id]
Obtiene un proveedor específico por ID.

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "data": { /* objeto proveedor */ }
}
```

### PUT /api/v1/catalogos/proveedores/[id]
Actualiza un proveedor existente.

**Body (JSON):** Igual que POST

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "data": { /* objeto proveedor actualizado */ },
  "message": "Proveedor actualizado exitosamente"
}
```

### DELETE /api/v1/catalogos/proveedores/[id]
Desactiva un proveedor (soft delete).

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "data": { /* objeto proveedor desactivado */ },
  "message": "Proveedor desactivado exitosamente"
}
```

---

## 🏢 Catálogos - Almacenes

### GET /api/v1/catalogos/almacenes
Lista todos los almacenes con paginación.

**Query Parameters:**
- `page` (opcional): Número de página (default: 1)
- `pageSize` (opcional): Tamaño de página (default: 10)
- `activo` (opcional): Filtrar por estado (true/false)

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "nombre": "Almacén Central",
      "tipo": "PRINCIPAL",
      "ubicacion": "Lima, Perú",
      "responsable": "Carlos Rodríguez",
      "activo": true,
      "creado_en": "2025-11-14T05:00:00.000Z",
      "actualizado_en": null
    }
  ],
  "pagination": {
    "page": 1,
    "pageSize": 10,
    "total": 20,
    "totalPages": 2
  }
}
```

### POST /api/v1/catalogos/almacenes
Crea un nuevo almacén.

**Body (JSON):**
```json
{
  "nombre": "Nuevo Almacén",
  "tipo": "SECUNDARIO",
  "ubicacion": "Arequipa, Perú",
  "responsable": "Ana López",
  "activo": true
}
```

### GET /api/v1/catalogos/almacenes/[id]
Obtiene un almacén específico por ID.

### PUT /api/v1/catalogos/almacenes/[id]
Actualiza un almacén existente.

### DELETE /api/v1/catalogos/almacenes/[id]
Desactiva un almacén (soft delete).

---

## 🔧 Tipos de Datos

### TipoProveedor (Enum)
- `FABRICANTE`
- `DISTRIBUIDOR`
- `SERVICIO_REPARACION`
- `SERVICIO_REENCAUCHE`
- `OTRO`

---

## ⚠️ Códigos de Error

- **400 Bad Request**: Datos inválidos o faltantes
- **404 Not Found**: Recurso no encontrado
- **500 Internal Server Error**: Error del servidor

**Formato de respuesta de error:**
```json
{
  "success": false,
  "error": "Mensaje de error descriptivo"
}
```

---

## 🚀 URLs

### Desarrollo Local
- **Base URL**: http://localhost:3000
- **Health Check**: http://localhost:3000/api/health
- **Proveedores**: http://localhost:3000/api/v1/catalogos/proveedores
- **Almacenes**: http://localhost:3000/api/v1/catalogos/almacenes

### Producción (Vercel)
- **Base URL**: https://gesneu-api.vercel.app
- **Health Check**: https://gesneu-api.vercel.app/api/health
- **API v1**: https://gesneu-api.vercel.app/api/v1/

---

*Última actualización: 14 de Noviembre, 2025*
