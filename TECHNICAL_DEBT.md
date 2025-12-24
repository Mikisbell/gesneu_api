# 📋 Deuda Técnica - GesNeu API

> Documento generado: 2025-12-24  
> Basado en: Análisis comparativo entre Documento de Requerimientos v2.1 y código actual

---

## 🔴 Prioridad Alta (Seguridad/Compliance)

### ~~1. Audit Logging Incompleto~~ ✅ RESUELTO
**Estado**: Completado en commit `82362815`

**Campos agregados a modelos principales**:
- `actualizado_por` (UUID)
- `eliminado_por` (UUID)
- `eliminado_en` (DateTime, soft delete)

**Modelos actualizados**: Neumatico, Vehiculo, Almacen, Proveedor

---

---

### ~~2. Test de Regla de Seguridad~~ ✅ RESUELTO
**Estado**: Completado en commit `5dfac84b`

**Tests creados**: `src/__tests__/security/retread-policy.test.ts`
- ✅ Bloquear reencauchado en eje direccional
- ✅ Permitir neumático nuevo en eje direccional
- ✅ Permitir reencauchado en eje tracción
- ✅ Bloquear cuando posicion.permite_reencauchado = false
- ✅ Verificar documentación en código

---

---

## 🟡 Prioridad Media (UX/Funcionalidad)

### ~~3. RBAC Dinámico en UI~~ ✅ RESUELTO
**Estado**: Completado en commit `64570202`

**Implementado**:
- Endpoint `GET /api/v1/auth/me` con permisos
- Hook `usePermissions()` para React
- Componentes `<PermissionGate>` y `<RoleGate>`

---

---

### 4. Mapa Visual de Ejes
**Requerimiento DR**: RF12 - "Visualizar un diagrama de los neumáticos de un vehículo."

**Estado actual**:
- Datos disponibles en `PosicionNeumatico`
- No hay componente visual de ejes

**Solución propuesta**:
- Componente `<VehicleAxleMap vehiculoId={...} />`
- SVG interactivo mostrando posiciones

**Esfuerzo**: 2-3 días

---

### 5. Notificaciones Externas
**Requerimiento DR**: "Webhook/Email para alertas críticas."

**Estado actual**:
- Alertas se generan y almacenan
- No hay envío de notificaciones

**Solución propuesta**:
- Integrar SendGrid o Resend para email
- Endpoint webhook configurable

**Esfuerzo**: 1-2 días

---

## 🟢 Prioridad Baja (Mejoras)

### 6. Diagrama ER en Documentación
**Estado actual**: No existe representación visual del modelo de datos.

**Solución**: Generar con `prisma-erd-generator` o Mermaid

---

### 7. Multi-Tenant (Futuro)
**Estado actual**: No hay `empresa_id` en tablas.

**Impacto**: No se puede vender como SaaS a múltiples clientes.

**Solución**: Agregar campo + Row Level Security en Supabase

---

### 8. Soporte para Neumáticos Gemelos (Duales)
**Estado actual**: Cada neumático se trata individualmente.

**Realidad operativa**: En ejes de tracción, las llantas van en pares y se rotan juntas.

**Solución**: Campo `gemelo_id` o relación `NeumaticoGemelo`

---

## 📊 Resumen

| Categoría | Items | Esfuerzo Total |
|-----------|-------|----------------|
| 🔴 Alta | 2 | 2-3 días |
| 🟡 Media | 3 | 4-6 días |
| 🟢 Baja | 3 | 3-5 días |

**Total estimado**: 2-3 semanas para cerrar toda la deuda técnica.

---

## ✅ Cómo usar este documento

1. **Antes de cada sprint**: Revisar y priorizar items
2. **Al agregar features**: Verificar que no se agregue más deuda
3. **Antes de vender/escalar**: Resolver items 🔴 obligatoriamente
