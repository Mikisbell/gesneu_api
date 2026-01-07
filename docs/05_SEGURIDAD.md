# 🔒 Seguridad - GesNeu API

> **Última actualización**: Diciembre 2025

---

## Autenticación

### NextAuth.js 5 (JWT)

```typescript
// Flujo de autenticación
1. Usuario envía credenciales a /api/auth/signin
2. NextAuth valida contra tabla `usuarios`
3. Se genera JWT con claims de roles/permisos
4. JWT se envía en header Authorization: Bearer <token>
5. Token expira en 8 horas (configurable)
```

### Configuración Crítica

```env
# REQUERIDO - Sin fallback
NEXTAUTH_SECRET=<generado con openssl rand -base64 32>
NEXTAUTH_URL=https://gesneu-api.vercel.app
```

**⚠️ NUNCA usar valores por defecto en producción.**

---

## Autorización (RBAC)

### Roles del Sistema

| Rol | Descripción | Acceso |
|-----|-------------|--------|
| `ADMINISTRADOR` | Acceso total | Todos los permisos |
| `GESTOR` | Gestión operativa | CRUD neumáticos, vehículos, reportes |
| `OPERADOR` | Operaciones diarias | Instalación, desmontaje, inspección |
| `CONSULTOR` | Solo lectura | Visualización de datos y dashboard |

### Permisos Granulares

```typescript
const PERMISSIONS = {
  // CATÁLOGOS
  CATALOGOS_PROVEEDORES_READ: 'catalogos:proveedores:read',
  CATALOGOS_PROVEEDORES_WRITE: 'catalogos:proveedores:write',
  CATALOGOS_ALMACENES_READ: 'catalogos:almacenes:read',
  CATALOGOS_ALMACENES_WRITE: 'catalogos:almacenes:write',

  // VEHÍCULOS
  VEHICULOS_READ: 'vehiculos:read',
  VEHICULOS_WRITE: 'vehiculos:write',
  VEHICULOS_CONFIGURAR: 'vehiculos:configurar',

  // NEUMÁTICOS
  NEUMATICOS_READ: 'neumaticos:read',
  NEUMATICOS_WRITE: 'neumaticos:write',
  NEUMATICOS_DELETE: 'neumaticos:delete',

  // EVENTOS (Granular por tipo)
  EVENTOS_INSTALACION: 'eventos:instalacion',
  EVENTOS_DESMONTAJE: 'eventos:desmontaje',
  EVENTOS_ROTACION: 'eventos:rotacion',
  EVENTOS_INSPECCION: 'eventos:inspeccion',
  EVENTOS_REENCAUCHE: 'eventos:reencauche',
  EVENTOS_DESECHO: 'eventos:desecho',

  // INVENTARIO
  INVENTARIO_READ: 'inventario:read',
  INVENTARIO_AJUSTES: 'inventario:ajustes',

  // REPORTES
  REPORTES_DASHBOARD: 'reportes:dashboard',
  REPORTES_AUDITORIA: 'reportes:auditoria',

  // SISTEMA
  SISTEMA_USUARIOS_MANAGE: 'sistema:usuarios:manage',
  SISTEMA_ROLES_MANAGE: 'sistema:roles:manage'
}
```

### Matriz Rol-Permisos

| Permiso | ADMIN | GESTOR | OPERADOR | CONSULTOR |
|---------|-------|--------|----------|-----------|
| catalogos:*:read | ✅ | ✅ | ✅ | ✅ |
| catalogos:*:write | ✅ | ✅ | ❌ | ❌ |
| vehiculos:read | ✅ | ✅ | ✅ | ✅ |
| vehiculos:write | ✅ | ✅ | ❌ | ❌ |
| neumaticos:read | ✅ | ✅ | ✅ | ✅ |
| neumaticos:write | ✅ | ✅ | ❌ | ❌ |
| eventos:instalacion | ✅ | ✅ | ✅ | ❌ |
| eventos:inspeccion | ✅ | ✅ | ✅ | ❌ |
| eventos:desecho | ✅ | ✅ | ❌ | ❌ |
| reportes:dashboard | ✅ | ✅ | ✅ | ✅ |
| reportes:auditoria | ✅ | ❌ | ❌ | ❌ |
| sistema:*:manage | ✅ | ❌ | ❌ | ❌ |

---

## Rate Limiting

```typescript
const RATE_LIMITS = {
  // Login - Más restrictivo (prevenir brute force)
  '/api/auth/signin': { 
    windowMs: 15 * 60 * 1000,  // 15 minutos
    maxRequests: 5              // 5 intentos
  },
  
  // API general
  '/api/v1/': { 
    windowMs: 60 * 1000,        // 1 minuto
    maxRequests: 100            // 100 requests
  },
  
  // Default
  'default': { 
    windowMs: 60 * 1000,
    maxRequests: 60
  }
}
```

---

## Middleware

```typescript
// src/middleware.ts
export const config = {
  matcher: ['/api/:path*', '/panel/:path*']
};
```

Protege:
- Todas las rutas `/api/*`
- Rutas de dashboard `/panel/*`

---

## Audit Trail

### Campos en Entidades

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `creado_por` | UUID | Usuario que creó |
| `creado_en` | DateTime | Timestamp creación |
| `actualizado_por` | UUID | Último editor |
| `actualizado_en` | DateTime | Timestamp actualización |
| `eliminado_por` | UUID | Quien eliminó (soft delete) |
| `eliminado_en` | DateTime | Timestamp eliminación |

### Algoritmo de Diff para Logs

```typescript
function calcularCambios(datosAntiguos, datosNuevos) {
  const cambios = {}
  
  for (const key in datosNuevos) {
    if (datosAntiguos[key] !== datosNuevos[key]) {
      cambios[key] = {
        anterior: datosAntiguos[key],
        nuevo: datosNuevos[key]
      }
    }
  }
  
  return Object.keys(cambios).length > 0 ? cambios : null
}
```

---

## Validación de Entrada

**Zod en todos los endpoints:**

```typescript
const body = CreateNeumaticoSchema.parse(await request.json());
```

Previene:
- Mass Assignment
- Inyección de datos maliciosos
- Tipos incorrectos

---

## Checklist de Seguridad

- [x] JWT sin fallback en secrets
- [x] Middleware en rutas API
- [x] Validación Zod en entrada
- [x] RBAC en endpoints sensibles
- [x] Audit trail completo
- [x] Soft delete (no eliminación física)
- [x] Rate limiting configurado
- [ ] 2FA (futuro)

---

*Ver `AGENT.md` para reglas de gobernanza de seguridad.*
