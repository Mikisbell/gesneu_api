# 📋 Deuda Técnica - GesNeu API

> Documento generado: 2025-12-24  
> Basado en: Análisis comparativo entre Documento de Requerimientos v2.1 y código actual

---

## 🔴 Prioridad Alta (Seguridad/Compliance)

### 1. Audit Logging Incompleto
**Requerimiento DR**: "Se implementarán mecanismos robustos a nivel de base de datos, como pgaudit."

**Estado actual**:
- Solo `creado_por` en algunas tablas
- No hay `updated_by`, `deleted_by`
- No hay triggers de auditoría en PostgreSQL

**Impacto**: No cumple SOC 2, ISO 27001

**Solución propuesta**:
```prisma
// Agregar a todos los modelos principales
actualizado_por  String?  @db.Uuid
eliminado_por    String?  @db.Uuid
eliminado_en     DateTime?
```
+ Trigger en Supabase para registrar cambios

**Esfuerzo**: 1-2 días

---

### 2. Test de Regla de Seguridad
**Requerimiento DR**: RF16, RF39 - Validaciones operativas críticas

**Estado actual**:
- Validación implementada en `montaje/route.ts`
- No hay test explícito para "bloquear reencauchado en eje direccional"

**Impacto**: Regla de vida sin cobertura de regresión

**Solución propuesta**:
```typescript
// src/__tests__/security/retread-policy.test.ts
describe('Retread Safety Policy', () => {
  it('should BLOCK retread tire on steering axle', async () => {...});
  it('should ALLOW retread tire on traction axle', async () => {...});
  it('should BLOCK when position.permite_reencauchado = false', async () => {...});
});
```

**Esfuerzo**: 3-4 horas

---

## 🟡 Prioridad Media (UX/Funcionalidad)

### 3. RBAC Dinámico en UI
**Requerimiento DR**: "El botón 'Eliminar' debe estar oculto para usuarios con rol 'Gerente de Flota'."

**Estado actual**:
- Backend valida permisos (`requirePermission`)
- Frontend no oculta elementos

**Solución propuesta**:
```typescript
// Hook usePermissions
const { canDelete } = usePermissions();
{canDelete && <Button>Eliminar</Button>}
```

**Esfuerzo**: 1 día

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
