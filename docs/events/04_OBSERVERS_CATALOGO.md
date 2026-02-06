# 👁️ Catálogo de Observers - Event-Driven Architecture

> **Audiencia:** Desarrolladores, DevOps, Arquitectos  
> **Última actualización:** Enero 2026  
> **Nivel:** Referencia técnica

---

## Tabla de Contenidos

1. [Vista General](#vista-general)
2. [AuditObserver](#1-auditobserver-)
3. [NotificationObserver](#2-notificationobserver-)
4. [AnalyticsObserver](#3-analyticsobserver-)
5. [AlertObserver](#4-alertobserver-)
6. [CacheObserver](#5-cacheobserver-)
7. [NeumaticoUpdateObserver](#6-neumaticoupdateobserver-)
8. [Matriz de Responsabilidades](#matriz-de-responsabilidades)

---

## Vista General

GesNeu implementa **6 observers independientes**, cada uno con una responsabilidad específica en el sistema Event-Driven.

### Características Comunes

Todos los observers siguen el mismo patrón:

```typescript
export class MyObserver {
  // 1. Método de inicialización
  static init() {
    EventBus.subscribe(EVENT_NAME, this.handler);
  }

  // 2. Handlers privados con error handling
  private static async handler(event: DomainEvent<Payload>) {
    try {
      // Lógica del observer
    } catch (error) {
      console.error('[MyObserver] Error:', error);
      // NO hacer throw
    }
  }
}
```

**Ubicación:** `src/lib/observers/*.observer.ts`

---

## 1. AuditObserver 📋

**Archivo:** `src/lib/observers/audit.observer.ts`

### Propósito

Registrar **todos** los eventos de neumáticos para auditoría y trazabilidad completa.

### Eventos Suscritos (9)

1. `NEUMATICO.PURCHASED`
2. `NEUMATICO.MOUNTED`
3. `NEUMATICO.DISMOUNTED`
4. `NEUMATICO.ROTATED`
5. `NEUMATICO.SCRAPPED`
6. `NEUMATICO.REPAIR_STARTED`
7. `NEUMATICO.REPAIR_COMPLETED`
8. `NEUMATICO.TRANSFERRED`
9. `NEUMATICO.RECLASSIFIED`

### Funcionalidad

**Actualmente:** Logs en consola  
**Futuro (Q2 2026):** Persistir en tabla `audit_log`

```typescript
static async handleEvent(event: DomainEvent<any>) {
  console.log(`📋 [AUDIT] ${event.name}`, {
    eventType: event.name,
    ...event.payload,
    timestamp: event.payload.timestamp.toISOString(),
  });
}
```

### Output Example

```
📋 [AUDIT] NEUMATICO.MOUNTED {
  eventType: 'NEUMATICO.MOUNTED',
  neumaticoId: 'tire-123',
  empresaId: '00000000-0000-0000-0000-000000000000',
  usuarioId: 'user-456',
  timestamp: '2026-01-29T21:30:00.000Z',
  vehiculoId: 'truck-789',
  posicionId: 'FL',
  kilometrajeVehiculo: 50000
}
```

### Dependencies

- ❌ No dependencies (solo console.log)

### Performance

- **Latencia:** < 1ms (solo console.log)
- **Blocking:** No (async pero sin I/O)

### Error Handling

```typescript
try {
  console.log('[AUDIT]', event);
} catch (error) {
  // Prácticamente imposible que falle
  console.error('[AuditObserver] Critical error:', error);
}
```

### Future Enhancements (Q2 2026)

```typescript
// Persistir en DB
await prisma.auditLog.create({
  data: {
    event_type: event.name,
    event_payload: event.payload,
    user_id: event.payload.usuarioId,
    timestamp: event.payload.timestamp,
  },
});
```

---

## 2. NotificationObserver 📢

**Archivo:** `src/lib/observers/notification.observer.ts`

### Propósito

Crear alertas automáticas en la base de datos cuando se detectan condiciones críticas.

### Eventos Suscritos (4)

1. `NEUMATICO.SCRAPPED`
2. `NEUMATICO.DISMOUNTED`
3. `NEUMATICO.REPAIR_STARTED`
4. `NEUMATICO.REPAIR_COMPLETED`

### Funcionalidad

#### Alerta 1: Alto Valor Desechado

```typescript
// Si neumático de alto valor (> $5,000) se desecha
if (metadata.costoTotal > HIGH_VALUE_THRESHOLD) {
  await prisma.alerta.create({
    data: {
      tipo: TipoAlertaEnum.DESGASTE_IRREGULAR,
      severidad: 'WARNING',
      mensaje: `Neumático de alto valor desechado - $${metadata.costoTotal}`,
      neumatico_id: payload.neumaticoId,
      empresa_id: payload.empresaId,
    },
  });
}
```

**Threshold:** `$5,000`

#### Alerta 2: Desgaste Prematuro

```typescript
// Si neumático se desecha con < 20,000 km
if (metadata.kmTotales < LOW_MILEAGE_THRESHOLD) {
  await prisma.alerta.create({
    data: {
      tipo: TipoAlertaEnum.DESGASTE_IRREGULAR,
      severidad: 'CRITICAL',
      mensaje: `Desgaste prematuro - ${metadata.kmTotales}km`,
      neumatico_id: payload.neumaticoId,
      empresa_id: payload.empresaId,
    },
  });
}
```

**Threshold:** `20,000 km`

### Dependencies

- ✅ Prisma (base de datos)
- ✅ Enum `TipoAlertaEnum`

### Performance

- **Latencia:** ~50ms (DB write)
- **Blocking:** No (async)

### Error Handling

```typescript
try {
  await prisma.alerta.create({ ... });
} catch (error) {
  console.error('[NotificationObserver] Failed to create alert:', error);
  // No throw - continúa el flujo
}
```

### Future Enhancements

- Email/WhatsApp notifications
- Webhook para sistemas externos
- Configuración de thresholds por usuario

---

## 3. AnalyticsObserver 📊

**Archivo:** `src/lib/observers/analytics.observer.ts`

### Propósito

Invalidar caché y actualizar métricas cuando cambia el estado de neumáticos.

### Eventos Suscritos (4)

1. `NEUMATICO.MOUNTED`
2. `NEUMATICO.DISMOUNTED`
3. `NEUMATICO.ROTATED`
4. `NEUMATICO.SCRAPPED`

### Funcionalidad

#### Invalidación de Caché

```typescript
// Invalidar caché de flota cuando se monta/desmonta
revalidateTag(`fleet-status-${payload.empresaId}`);
```

**Tags usados:**
- `fleet-status-{empresaId}` - Estado general de flota
- `scrap-rate-{empresaId}` - Tasa de desecho

#### Cálculo de Métricas

```typescript
// Al desechar: calcular CPK (Costo por Kilómetro)
const costPerKm = metadata.costoTotal / metadata.kmTotales;
console.log(`💰 [Analytics] Cost efficiency: $${costPerKm.toFixed(4)}/km`);
```

### Dependencies

- ✅ Next.js `revalidateTag` API

### Performance

- **Latencia:** ~5ms (cache invalidation)
- **Blocking:** No

### Error Handling

```typescript
try {
  revalidateTag(tag);
} catch (error) {
  // Común en testing/desarrollo sin Next.js context
  console.error('[AnalyticsObserver] Cache invalidation failed:', error);
}
```

### Known Issues

⚠️ **Warning en tests:**
```
Invariant: static generation store missing in revalidateTag
```

**Causa:** `revalidateTag` solo funciona en runtime de Next.js  
**Impacto:** Ninguno - error silenciado en handler

---

## 4. AlertObserver 🚨

**Archivo:** `src/lib/observers/alerta.observer.ts`

### Propósito

Crear alertas basadas en lecturas de inspección (presión y profundidad).

### Eventos Suscritos (2)

1. `INSPECCION.PRESSURE_READ`
2. `INSPECCION.DEPTH_READ`

### Funcionalidad

#### Alerta por Presión Baja

```typescript
// Si presión < 90% de lo recomendado
const presionPorcentaje = (payload.presionActual / payload.presionRecomendada) * 100;

if (presionPorcentaje < 90) {
  await prisma.alerta.create({
    data: {
      tipo: TipoAlertaEnum.PRESION_BAJA,
      severidad: 'CRITICAL',
      mensaje: `Presión baja: ${payload.presionActual}/${payload.presionRecomendada} PSI (${presionPorcentaje.toFixed(1)}%)`,
      neumatico_id: payload.neumaticoId,
      vehiculo_id: payload.vehiculoId,
    },
  });
}
```

**Threshold:** 90% de presión recomendada

#### Alerta por Profundidad Crítica

```typescript
// Si profundidad < 4mm → WARNING
// Si profundidad < mínimo legal → CRITICAL
if (payload.profundidadActual < 4.0) {
  const severidad = payload.profundidadActual < payload.profundidadMinima 
    ? 'CRITICAL' 
    : 'WARNING';

  await prisma.alerta.create({
    data: {
      tipo: TipoAlertaEnum.PROFUNDIDAD_CRITICA,
      severidad,
      mensaje: `Profundidad crítica: ${payload.profundidadActual}mm`,
      neumatico_id: payload.neumaticoId,
      vehiculo_id: payload.vehiculoId,
    },
  });
}
```

**Thresholds:**
- **WARNING:** < 4mm
- **CRITICAL:** < profundidad mínima legal (1.6mm)

### Dependencies

- ✅ Prisma
- ✅ `TipoAlertaEnum`

### Performance

- **Latencia:** ~50ms (DB write)
- **Blocking:** No

---

## 5. CacheObserver 🔄

**Archivo:** `src/lib/observers/cache.observer.ts`

### Propósito

Invalidar caché específico de reencauche cuando cambia el estado.

### Eventos Suscritos (2)

1. `REENCAUCHE.SENT`
2. `REENCAUCHE.RETURNED`

### Funcionalidad

```typescript
// Invalidar lista de neumáticos en reencauche
revalidateTag(`pending-retreads-${payload.empresaId}`);
```

### Dependencies

- ✅ Next.js `revalidateTag` API

### Performance

- **Latencia:** ~5ms
- **Blocking:** No

---

## 6. NeumaticoUpdateObserver 💾

**Archivo:** `src/lib/observers/neumatico-update.observer.ts`

### Propósito

Actualizar el snapshot de datos del neumático cuando hay inspecciones.

### Eventos Suscritos (2)

1. `INSPECCION.PRESSURE_READ`
2. `INSPECCION.DEPTH_READ`

### Funcionalidad

#### Actualizar Presión

```typescript
await prisma.neumatico.update({
  where: { id: payload.neumaticoId },
  data: {
    presion_actual: payload.presionActual,
    fecha_ultima_inspeccion: payload.timestamp,
  },
});
```

#### Actualizar Profundidad

```typescript
await prisma.neumatico.update({
  where: { id: payload.neumaticoId },
  data: {
    profundidad_actual: payload.profundidadActual,
    fecha_ultima_inspeccion: payload.timestamp,
  },
});
```

### Dependencies

- ✅ Prisma

### Performance

- **Latencia:** ~30ms (DB update)
- **Blocking:** No

### Error Handling

```typescript
try {
  await prisma.neumatico.update({ ... });
} catch (error) {
  console.error('[NeumaticoUpdateObserver] Update failed:', error);
  // Común si neumático fue eliminado
}
```

---

## Matriz de Responsabilidades

| Observer | Eventos | Responsabilidad Principal | DB Writes | Performance Impact |
|----------|---------|---------------------------|-----------|-------------------|
| **AuditObserver** | 9 | Logging universal | ❌ | Ninguno |
| **NotificationObserver** | 4 | Crear alertas críticas | ✅ | Bajo (~50ms) |
| **AnalyticsObserver** | 4 | Cache invalidation | ❌ | Mínimo (~5ms) |
| **AlertObserver** | 2 | Alertas de inspección | ✅ | Bajo (~50ms) |
| **CacheObserver** | 2 | Cache de reencauche | ❌ | Mínimo (~5ms) |
| **NeumaticoUpdateObserver** | 2 | Snapshot de neumático | ✅ | Bajo (~30ms) |

---

## Performance Agregado

### Por Evento

**Ejemplo: NEUMATICO.MOUNTED**

| Observer | Latencia |
|----------|----------|
| AuditObserver | ~1ms |
| AnalyticsObserver | ~5ms |
| **Total** | **~6ms** |

**Ejemplo: NEUMATICO.SCRAPPED**

| Observer | Latencia |
|----------|----------|
| AuditObserver | ~1ms |
| NotificationObserver | ~50ms |
| AnalyticsObserver | ~5ms |
| **Total** | **~56ms** |

**Ejemplo: INSPECCION.PRESSURE_READ**

| Observer | Latencia |
|----------|----------|
| AlertObserver | ~50ms |
| NeumaticoUpdateObserver | ~30ms |
| **Total** | **~80ms** |

---

## Error Patterns

### Patrón Común

```typescript
private static async handler(event: DomainEvent<Payload>) {
  try {
    // Lógica del observer
    await someOperation();
  } catch (error) {
    // ✅ SIEMPRE logear
    console.error('[ObserverName] Error in handler:', error);
    
    // ❌ NUNCA hacer throw
    // throw error; // ← PROHIBIDO
  }
}
```

**Por qué:** Un observer fallando no debe impactar otros observers ni la transacción principal.

---

## Dependencies Graph

```
AuditObserver
  └─ (sin dependencias)

NotificationObserver
  └─ Prisma
     └─ TipoAlertaEnum

AnalyticsObserver
  └─ Next.js (revalidateTag)

AlertObserver
  └─ Prisma
     └─ TipoAlertaEnum

CacheObserver
  └─ Next.js (revalidateTag)

NeumaticoUpdateObserver
  └─ Prisma
```

---

## Próximos Observers (Roadmap)

### Q2 2026

**VentasObserver**
- Eventos: `SCRAPPED`, `DISMOUNTED`
- Propósito: Crear oportunidades de venta automáticas

**MarketingObserver**
- Eventos: `PURCHASED`, `SCRAPPED`
- Propósito: Encuestas y campañas basadas en comportamiento

### Q3 2026

**ERPObserver**
- Eventos: Todos
- Propósito: Sincronización con SAP/Oracle

**EventStoreObserver**
- Eventos: Todos
- Propósito: Persistir Event Sourcing

### Q4 2026

**MLObserver**
- Eventos: `SCRAPPED`, `MOUNTED`
- Propósito: Machine Learning predictions

---

## Monitoring

### Métricas Clave (Futuro)

```typescript
// Dashboard de observers
GET /api/v1/admin/events/monitor

{
  "observers": [
    {
      "name": "AuditObserver",
      "events_handled_24h": 1547,
      "avg_latency_ms": 0.8,
      "error_rate": 0,
      "last_error": null
    },
    {
      "name": "NotificationObserver",
      "events_handled_24h": 34,
      "avg_latency_ms": 52,
      "error_rate": 0.02,
      "last_error": "2026-01-29 15:30:00 - DB timeout"
    }
  ]
}
```

---

## Troubleshooting

### Observer no reacciona

**Verificar:**
1. `init()` llamado en `registry.ts`?
2. Nombre del evento correcto?
3. Handler definido como `private static async`?

### Performance degradado

**Verificar:**
1. DB queries optimizados?
2. Operaciones pesadas delegadas a job queue?
3. Timeout configurado en llamadas externas?

---

## Próximos Pasos

- Ver [Testing de Eventos](./05_TESTING_EVENTOS.md) para testear observers
- Ver [Monitoreo y Operaciones](./06_MONITOREO_OPERACIONES.md) para debugging
- Ver [Guía de Desarrollo](./02_GUIA_DESARROLLO.md) para crear nuevos observers

---

**Última actualización:** 2026-01-29  
**Total de observers:** 6 activos  
**Mantenido por:** Equipo de Arquitectura GesNeu
