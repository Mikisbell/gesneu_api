# 🔌 API Reference - GesNeu API

> **Última actualización**: Diciembre 2025  
> **Base URL**: `/api/v1`

---

## Autenticación

Todos los endpoints requieren autenticación JWT (NextAuth).

```
Authorization: Bearer <token>
```

---

## Recursos Principales

### Neumáticos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/neumaticos` | Listar neumáticos (paginado) |
| GET | `/neumaticos/:id` | Obtener neumático por ID |
| POST | `/neumaticos` | Crear neumático (evento COMPRA) |
| PUT | `/neumaticos/:id` | Actualizar neumático |
| DELETE | `/neumaticos/:id` | Soft delete |

### Vehículos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/vehiculos` | Listar vehículos |
| GET | `/vehiculos/:id` | Obtener vehículo |
| GET | `/vehiculos/:id/montaje` | Estado de montaje con mapa de ejes |
| POST | `/vehiculos` | Crear vehículo |

### Operaciones

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/operaciones/montaje` | Montar neumático |
| POST | `/operaciones/desmontaje` | Desmontar neumático |
| POST | `/operaciones/rotacion` | Rotar neumáticos |

### Inspecciones

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/inspecciones` | Registrar inspección manual de presión |

### Dashboard

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/dashboard/inventario` | Resumen de inventario |
| GET | `/dashboard/rendimiento` | KPIs de rendimiento |
| GET | `/dashboard/desechos` | Estadísticas de desechos |
| GET | `/dashboard/exportar` | Exportar datos (CSV) |

### Webhooks (Integración ERP)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/webhooks` | Listar configuraciones |
| POST | `/webhooks` | Crear configuración |
| POST | `/webhooks/:id/test` | Probar disparo de evento |

### Reportes y Documentos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/reports/certificate/:id` | **PDF** Certificado de Operatividad |
| GET | `/neumaticos/:id/historial-presion` | Datos históricos (JSON) para gráficos |
| GET | `/reportes/cpk` | Costo por Kilómetro |

### Alertas

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/alertas` | Listar alertas |
| POST | `/alertas/generar` | Generar alertas automáticas |
| PATCH | `/alertas/:id` | Marcar como leída/resuelta |

### Catálogos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/catalogos/almacenes` | Listar almacenes |
| POST | `/catalogos/almacenes` | Crear almacén |
| GET | `/catalogos/proveedores` | Listar proveedores |
| POST | `/catalogos/proveedores` | Crear proveedor |

### Admin Panel (Requiere Rol Admin)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/admin/users` | Directorio global usuarios |
| GET | `/admin/audit` | Audit trail del sistema |
| GET | `/admin/webhooks` | Consola de webhooks |

---

## Swagger/OpenAPI

Documentación interactiva disponible en:
```
GET /api/docs
```

---

*Para detalles de payloads, ver schemas Zod en `src/lib/validators/`.*
