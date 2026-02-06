# 🔍 Monitoreo y Operaciones - Event-Driven Architecture

> **Audiencia:** DevOps, SREs, Developers  
> **Última actualización:** Enero 2026  
> **Nivel:** Operaciones

---

## Tabla de Contenidos

1. [Logging Estructurado](#logging-estructurado)
2. [Dashboards (Futuro)](#dashboards-futuro)
3. [Alertas y SLOs](#alertas-y-slos)
4. [Debugging de Flujos](#debugging-de-flujos)
5. [Troubleshooting](#troubleshooting)
6. [Performance Monitoring](#performance-monitoring)

---

## Logging Estructurado

### Estado Actual (Enero 2026)

Los observers emiten logs a `console.log` con formato consistente:

```typescript
console.log(`[ObserverName] Message`, { context });
```

**Prefijos estandarizados:**
- `📋 [AUDIT]` - AuditObserver
- `📢 [ALERT]` - NotificationObserver
- `🔄 [Analytics]` - AnalyticsObserver
- `🚨 [ALERT]` - AlertObserver
- `💾 [Observer]` - NeumaticoUpdateObserver

---

### Formato de Logs

#### Evento Publicado

```
📋 [AUDIT] NEUMATICO.MOUNTED {
  eventType: 'NEUMATICO.MOUNTED',
  neumaticoId: 'tire-abc-123',
  empresaId: '00000000-0000-0000-0000-000000000000',
  usuarioId: 'user-456',
  timestamp: '2026-01-29T21:30:00.000Z',
  vehiculoId: 'truck-789',
  posicionId: 'FL',
  kilometrajeVehiculo: 50000
}
```

#### Error en Observer

```
❌ [NotificationObserver] alertHighValueScrap failed: 
Invalid `prisma.alerta.create()` invocation
Can't reach database server at 127.0.0.1:5432
```

---

### Logs Estructurados (Plan Q2 2026)

Migrar a logs JSON para indexación en Elasticsearch:

```typescript
import { logger } from '@/lib/logging';

// En lugar de console.log
logger.info({
  message: 'Event processed',
  observer: 'AuditObserver',
  event_type: 'NEUMATICO.MOUNTED',
  neumatico_id: payload.neumaticoId,
  user_id: payload.usuarioId,
  duration_ms: 15,
  success: true,
});
```

**Stack propuesto:**
- **Winston** - Structured logging
- **Elasticsearch** - Log storage
- **Kibana** - Visualization

---

## Dashboards (Futuro)

### Dashboard 1: Event Overview

**Ubicación futura:** `/dashboard/admin/events`

**Métricas:**
```
┌─────────────────────────────────────────┐
│  Event-Driven Architecture Overview     │
├─────────────────────────────────────────┤
│ Events Published (24h):      1,547      │
│ Avg Latency:                 15ms       │
│ Error Rate:                  0.02%      │
│ Active Observers:            6          │
└─────────────────────────────────────────┘

Recent Events:
┌──────────────────┬───────────────────┬────────┬──────────┐
│ Timestamp        │ Event             │ Tire   │ User     │
├──────────────────┼───────────────────┼────────┼──────────┤
│ 21:45:32         │ MOUNTED           │ T-123  │ mech-001 │
│ 21:43:15         │ SCRAPPED          │ T-456  │ admin-01 │
│ 21:40:05         │ PRESSURE_READ     │ T-789  │ insp-002 │
└──────────────────┴───────────────────┴────────┴──────────┘
```

---

### Dashboard 2: Observer Health

```
┌──────────────────────────────────────────────────────────┐
│  Observer Health Status                                  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ AuditObserver              ✅ Healthy                    │
│   └─ Events: 1,547  Latency: 0.8ms  Errors: 0           │
│                                                          │
│ NotificationObserver       ⚠️  Degraded                  │
│   └─ Events: 34     Latency: 52ms   Errors: 1 (2%)      │
│   └─ Last Error: DB timeout (21:30:15)                   │
│                                                          │
│ AnalyticsObserver          ✅ Healthy                    │
│   └─ Events: 1,200  Latency: 5ms    Errors: 0           │
│                                                          │
│ AlertObserver              ✅ Healthy                    │
│   └─ Events: 450    Latency: 45ms   Errors: 0           │
│                                                          │
│ CacheObserver              ✅ Healthy                    │
│   └─ Events: 12     Latency: 3ms    Errors: 0           │
│                                                          │
│ NeumaticoUpdateObserver    ✅ Healthy                    │
│   └─ Events: 450    Latency: 30ms   Errors: 0           │
└──────────────────────────────────────────────────────────┘
```

---

### Dashboard 3: Event Throughput

**Gráfica de líneas:**
```
Events/hour ┤
 2000       ┤                                    ╭─╮
 1500       ┤              ╭╮       ╭──╮    ╭──╯ │
 1000       ┤          ╭───╯╰───────╯  ╰────╯    │
  500       ┤  ╭───────╯                         │
    0       ┴──┴────────────────────────────────┴──
            0  4  8  12 16 20 24 (hours)
```

**Tipos de eventos (pie chart):**
- MOUNTED: 35%
- PRESSURE_READ: 25%
- DEPTH_READ: 20%
- SCRAPPED: 10%
- Others: 10%

---

## Alertas y SLOs

### SLIs (Service Level Indicators)

| SLI | Definición | Target |
|-----|-----------|---------|
| **Event Latency** | P95 de tiempo de publicación | < 100ms |
| **Observer Success Rate** | % de observers sin errores | > 99.5% |
| **Event Throughput** | Eventos/seg procesados | > 10/s |
| **Error Rate** | % de eventos con errors | < 0.1% |

---

### SLOs (Service Level Objectives)

**SLO 1: Event Latency**
- **Target:** P95 < 100ms en ventana 24h
- **Alerta:** Si P95 > 150ms por > 5 minutos

**SLO 2: Observer Availability**
- **Target:** 99.9% uptime
- **Alerta:** Si observer falla > 3 veces en 1 hora

**SLO 3: No Data Loss**
- **Target:** 100% de eventos persistidos en audit log
- **Alerta:** Si audit log falla > 1 vez en 24h

---

### Configuración de Alertas (Futuro)

```yaml
# alerts/event-driven.yml
alerts:
  - name: HighEventLatency
    condition: p95(event_publish_duration_ms) > 150 for 5m
    severity: WARNING
    notify:
      - slack: #ops-alerts
      - email: ops@gesneu.com

  - name: ObserverFailureSpike
    condition: rate(observer_errors) > 0.05 for 5m
    severity: CRITICAL
    notify:
      - pagerduty: oncall
      - slack: #ops-critical

  - name: EventBusDown
    condition: up{service="event-bus"} == 0
    severity: CRITICAL
    notify:
      - pagerduty: oncall
```

---

## Debugging de Flujos

### Herramienta 1: Event Tracer Script

**Archivo:** `scripts/trace-event.ts`

```typescript
#!/usr/bin/env tsx

import { prisma } from '@/lib/db';
import { EventBus } from '@/lib/events/core';

async function traceEvent(neumaticoId: string) {
  console.log(`🔍 Tracing events for tire: ${neumaticoId}\n`);

  // 1. Buscar en DB
  const eventos = await prisma.eventoNeumatico.findMany({
    where: { neumatico_id: neumaticoId },
    orderBy: { fecha_evento: 'asc' },
    include: { usuario: true },
  });

  console.log('📋 Database Events:');
  eventos.forEach(evt => {
    console.log(`  ${evt.fecha_evento.toISOString()} - ${evt.tipo} by ${evt.usuario.username}`);
  });

  // 2. Buscar alertas relacionadas
  const alertas = await prisma.alerta.findMany({
    where: { neumatico_id: neumaticoId },
    orderBy: { fecha_creacion: 'asc' },
  });

  console.log(`\n🚨 Alerts Triggered: ${alertas.length}`);
  alertas.forEach(alerta => {
    console.log(`  [${alerta.severidad}] ${alerta.mensaje}`);
  });
}

// Run
const neumaticoId = process.argv[2];
if (!neumaticoId) {
  console.error('Usage: tsx scripts/trace-event.ts <neumatico_id>');
  process.exit(1);
}

traceEvent(neumaticoId);
```

**Uso:**
```bash
tsx scripts/trace-event.ts tire-abc-123
```

**Output:**
```
🔍 Tracing events for tire: tire-abc-123

📋 Database Events:
  2026-01-15T10:30:00.000Z - COMPRA by admin-001
  2026-01-20T14:45:00.000Z - MONTAJE by mech-002
  2026-01-29T21:30:00.000Z - DESECHO by admin-001

🚨 Alerts Triggered: 1
  [CRITICAL] Desgaste prematuro - 15000km
```

---

### Herramienta 2: Live Event Monitor

```typescript
// scripts/monitor-events.ts
import { EventBus } from '@/lib/events/core';
import { registerObservers } from '@/lib/events/registry';

console.log('🔴 Live Event Monitor - Press Ctrl+C to exit\n');

registerObservers();

// Suscribirse a TODOS los eventos
const allEvents = [
  'NEUMATICO.PURCHASED',
  'NEUMATICO.MOUNTED',
  'NEUMATICO.DISMOUNTED',
  'NEUMATICO.ROTATED',
  'NEUMATICO.SCRAPPED',
  'NEUMATICO.REPAIR_STARTED',
  'NEUMATICO.REPAIR_COMPLETED',
  'NEUMATICO.TRANSFERRED',
  'NEUMATICO.RECLASSIFIED',
  'INSPECCION.PRESSURE_READ',
  'INSPECCION.DEPTH_READ',
];

allEvents.forEach(eventName => {
  EventBus.subscribe(eventName, (event) => {
    console.log(`📤 [${new Date().toISOString()}] ${eventName}`);
    console.log(JSON.stringify(event.payload, null, 2));
    console.log('─'.repeat(80));
  });
});
```

**Uso:**
```bash
tsx scripts/monitor-events.ts
```

---

## Troubleshooting

### Problema 1: Observer no reacciona

**Síntomas:**
- Evento se publica (se ve en logs de AuditObserver)
- Observer específico no ejecuta

**Debugging:**
```typescript
// Verificar listeners registrados
import { EventBus } from '@/lib/events/core';

const count = (EventBus as any).listenerCount('NEUMATICO.MOUNTED');
console.log(`Listeners for MOUNTED: ${count}`);
// Esperado: 2 (AuditObserver + AnalyticsObserver)
```

**Soluciones:**
1. Verificar que `Observer.init()` está en `registry.ts`
2. Verificar nombre del evento (case-sensitive)
3. Revisar logs de errores en el handler

---

### Problema 2: Performance Degradado

**Síntomas:**
- API responses lentos después de eventos
- CPU spike al publicar eventos

**Debugging:**
```typescript
// Medir latencia de cada observer
import { performance } from 'perf_hooks';

EventBus.subscribe('NEUMATICO.MOUNTED', async (event) => {
  const start = performance.now();
  
  await yourHandler(event);
  
  const duration = performance.now() - start;
  console.log(`⏱️  Handler duration: ${duration.toFixed(2)}ms`);
  
  if (duration > 100) {
    console.warn(`⚠️  Slow handler detected!`);
  }
});
```

**Soluciones:**
1. Optimizar queries de DB (agregar índices)
2. Delegar operaciones pesadas a job queue
3. Cachear datos frecuentes

---

### Problema 3: Memory Leak

**Síntomas:**
- Uso de RAM creciente
- Warning: `MaxListenersExceededWarning`

**Debugging:**
```typescript
// Verificar listeners activos
const emitter = EventBus as any;
console.log('Event listeners:');
emitter.eventNames().forEach(eventName => {
  const count = emitter.listenerCount(eventName);
  console.log(`  ${eventName}: ${count} listeners`);
});
```

**Soluciones:**
1. Verificar que observers no se registran múltiples veces
2. Aumentar max listeners si es legítimo:
   ```typescript
   this.setMaxListeners(50);
   ```

---

## Performance Monitoring

### Métricas Clave

#### 1. Event Publish Latency

```typescript
// Instrumentación (futuro)
import { performance } from 'perf_hooks';

async publish<T>(eventName: string, payload: T) {
  const start = performance.now();
  
  await this.executeListeners(eventName, payload);
  
  const duration = performance.now() - start;
  
  metrics.histogram('event_publish_duration_ms', duration, {
    event_type: eventName,
  });
}
```

**Queries útiles:**
```promql
# P95 latency
histogram_quantile(0.95, event_publish_duration_ms)

# Latency por tipo de evento
histogram_quantile(0.95, event_publish_duration_ms{event_type="NEUMATICO.MOUNTED"})
```

---

#### 2. Observer Success Rate

```typescript
// Instrumentación
try {
  await handler(event);
  metrics.increment('observer_success', { observer: 'AuditObserver' });
} catch (error) {
  metrics.increment('observer_error', { observer: 'AuditObserver' });
}
```

**Queries:**
```promql
# Error rate por observer
rate(observer_error[5m]) / (rate(observer_success[5m]) + rate(observer_error[5m]))
```

---

#### 3. Event Throughput

```typescript
metrics.increment('event_published', { event_type: eventName });
```

**Queries:**
```promql
# Events per second
rate(event_published[1m])

# Por tipo
rate(event_published{event_type="NEUMATICO.MOUNTED"}[1m])
```

---

### Profiling en Desarrollo

```typescript
// Para identificar bottlenecks
import { registerObservers } from '@/lib/events/registry';

console.profile('EventBus Performance');

registerObservers();

// Publicar 1000 eventos
for (let i = 0; i < 1000; i++) {
  await EventBus.publish('NEUMATICO.MOUNTED', { /* payload */ });
}

console.profileEnd('EventBus Performance');
```

---

## Runbooks

### Runbook 1: Observer Down

**Condición:** Observer falla consistentemente

**Pasos:**
1. Identificar el observer fallando (revisar logs)
2. Verificar dependencias (DB, APIs externas)
3. Deshabilitar temporalmente el observer:
   ```typescript
   // En registry.ts
   // MyBrokenObserver.init();  // ← Comentar
   ```
4. Desplegar hotfix
5. Investigar causa raíz
6. Re-habilitar con fix

---

### Runbook 2: Event Storm

**Condición:** > 1000 eventos/seg (anormal)

**Pasos:**
1. Identificar fuente del storm (revisar event types)
2. Rate limiting temporal:
   ```typescript
   const lastPublish = new Map();
   const RATE_LIMIT_MS = 100;
   
   async publish(eventName, payload) {
     const now = Date.now();
     const last = lastPublish.get(eventName) || 0;
     
     if (now - last < RATE_LIMIT_MS) {
       console.warn('Rate limit hit');
       return;
     }
     
     lastPublish.set(eventName, now);
     await this.doPublish(eventName, payload);
   }
   ```
3. Investigar código que genera eventos
4. Fix y deploy

---

## Próximos Pasos

- Ver [Roadmap de Eventos](./07_ROADMAP_EVENTOS.md) para mejoras futuras
- Ver [Testing de Eventos](./05_TESTING_EVENTOS.md) para prevenir problemas
- Ver [Arquitectura](./01_ARQUITECTURA_EVENTOS.md) para entender el sistema

---

**Última actualización:** 2026-01-29  
**Stack de monitoreo (futuro):** Prometheus + Grafana + Elasticsearch  
**Mantenido por:** Equipo de DevOps GesNeu
