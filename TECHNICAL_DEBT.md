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

### ~~4. Mapa Visual de Ejes~~ ✅ RESUELTO
**Estado**: Completado en commit `ab42c1b8`

**Implementado**:
- Endpoint `GET /api/v1/vehiculos/:id/montaje`
- Componente `<VehicleAxleMap>` con glassmorphism
- Componente `<TireSlot>` con estados visuales
- Página demo `/mapa-ejes`

**Diseño Premium 2025**:
- Glassmorphism + backdrop blur
- Micro-animaciones (pulse, shake)
- Color coding (OK/Warning/Critical)
- Tooltips interactivos
- Responsive + Dark mode

---

### ~~5. Notificaciones Email~~ ✅ RESUELTO
**Estado**: Completado en commit `dd2f9e5b`

**Implementado**:
- Servicio `EmailService` usando Resend API
- Templates HTML responsivos y profesionales
- Integración en `AlertasService.generarAlertasProfundidad()`
- Envío automático a usuarios ADMIN/GESTOR
- Manejo errores robusto (Lazy init, fallback)

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
