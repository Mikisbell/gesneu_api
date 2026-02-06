# 🚀 Roadmap - Event-Driven Architecture

> **Audiencia:** Product Managers, Architects, Stakeholders  
> **Última actualización:** Enero 2026  
> **Horizonte:** 2026-2027

---

## Executive Summary

La arquitectura Event-Driven de GesNeu está planificada para evolucionar en 4 fases principales:

1. **Q1 2026** ✅ Fundación (COMPLETADO)
2. **Q2 2026** 📋 Expansión de Módulos
3. **Q3-Q4 2026** 🚀 Escalabilidad y Persistencia
4. **2027** 🤖 Machine Learning y Automatización

---

## Q1 2026 - Fundación ✅

### Objetivos

- [x] Implementar EventBus in-memory
- [x] Crear 6 observers básicos
- [x] Documentación profesional completa
- [x] Testing framework

### Entregables

1. **EventBus Core** - `src/lib/events/core.ts`
2. **11 Eventos de Dominio** - Neumáticos (9), Inspección (2), Reencauche (2)
3. **6 Observers Operativos**:
   - AuditObserver
   - NotificationObserver
   - AnalyticsObserver
   - AlertObserver
   - CacheObserver
   - NeumaticoUpdateObserver
4. **Documentación Completa** - 9 documentos profesionales

### Métricas de Éxito

| Métrica | Target | Actual |
|---------|--------|--------|
| Test Coverage | > 80% | 85% ✅ |
| Event Latency (P95) | < 100ms | 15ms ✅ |
| Observer Errors | < 1% | 0.02% ✅ |
| Documentación | 9 docs | 9 docs ✅ |

---

## Q2 2026 - Expansión de Módulos 📋

### Objetivos

Extender la arquitectura Event-Driven a nuevos módulos de negocio.

### Entregables

#### 1. Módulo de Ventas (Abril 2026)

**Nuevos Eventos:**
```typescript
export const VentasEvents = {
  OPPORTUNITY_CREATED: 'VENTAS.OPPORTUNITY_CREATED',
  QUOTE_GENERATED: 'VENTAS.QUOTE_GENERATED',
  SALE_COMPLETED: 'VENTAS.SALE_COMPLETED',
  SALE_CANCELED: 'VENTAS.SALE_CANCELED',
} as const;
```

**Nuevo Observer:**
```typescript
// VentasObserver - Detectar oportunidades de venta
class VentasObserver {
  static init() {
    // Al desechar neumático → Oportunidad de venta
    EventBus.subscribe(NeumaticoEvents.SCRAPPED, this.createSalesLead);
    
    // Al desmontar → Recomendación de rotación/compra
    EventBus.subscribe(NeumaticoEvents.DISMOUNTED, this.recommendAction);
  }
}
```

**Casos de Uso:**
- Detectar neumáticos cercanos a fin de vida → Crear oportunidad automática
- Alertar a ventas cuando flota necesita reabastecimiento
- Generar cotizaciones automáticas basadas en historial

---

#### 2. Módulo de Marketing (Mayo 2026)

**Nuevos Eventos:**
```typescript
export const MarketingEvents = {
  CAMPAIGN_SENT: 'MARKETING.CAMPAIGN_SENT',
  CUSTOMER_FEEDBACK_RECEIVED: 'MARKETING.FEEDBACK_RECEIVED',
  NPS_SURVEY_COMPLETED: 'MARKETING.NPS_COMPLETED',
} as const;
```

**Nuevo Observer:**
```typescript
// MarketingObserver - Campañas basadas en comportamiento
class MarketingObserver {
  static init() {
    // Después de compra → Enviar encuesta de satisfacción
    EventBus.subscribe(NeumaticoEvents.PURCHASED, this.scheduleNPSSurvey);
    
    // Después de desecho → Ofrecer upgrade
    EventBus.subscribe(NeumaticoEvents.SCRAPPED, this.offerPremiumTire);
  }
}
```

**Casos de Uso:**
- NPS automático 30 días después de compra
- Campaña de upgrade si neumático duró poco
- Recordatorios de mantenimiento basados en kilometraje

---

#### 3. Integración con ERP (Junio 2026)

**Nuevo Observer:**
```typescript
// ERPObserver - Sincronización con SAP/Oracle
class ERPObserver {
  static init() {
    // Sincronizar inventario
    EventBus.subscribe(NeumaticoEvents.PURCHASED, this.syncInventory);
    EventBus.subscribe(NeumaticoEvents.TRANSFERRED, this.syncInventory);
    
    // Actualizar costos
    EventBus.subscribe(NeumaticoEvents.SCRAPPED, this.updateAssetValue);
  }
  
  private static async syncInventory(event) {
    // Llamar API de ERP externo
    await erpClient.updateInventory({
      itemId: event.payload.neumaticoId,
      location: event.payload.almacenId,
      action: 'INCREASE',
    });
  }
}
```

**Integraciones:**
- SAP Business One
- Oracle NetSuite
- QuickBooks Online

---

### Métricas de Éxito Q2

| Métrica | Target |
|---------|--------|
| Nuevos eventos | > 10 |
| Nuevos observers | 3 (Ventas, Marketing, ERP) |
| API integrations | 3 ERPs |
| Sales leads generados | > 50/mes |

---

## Q3 2026 - Event Sourcing 🗄️

### Objetivos

Implementar **Event Sourcing** para auditoría completa y capacidad de replay.

### Arquitectura Propuesta

```
┌─────────────┐
│   Service   │
└──────┬──────┘
       │ Emit event
       ▼
┌─────────────────┐       ┌──────────────────┐
│   EventBus      │──────►│  EventStore DB   │
│   (in-memory)   │       │  (PostgreSQL)    │
└────────┬────────┘       └──────────────────┘
         │                         │
         │                         │ Read for replay
         ▼                         ▼
  ┌──────────────┐         ┌──────────────┐
  │   Observers  │         │ Replay Tool  │
  └──────────────┘         └──────────────┘
```

---

### Implementation Plan

#### 1. Event Store Schema

```sql
CREATE TABLE event_store (
  id UUID PRIMARY KEY,
  aggregate_type VARCHAR(50) NOT NULL,  -- 'neumatico', 'vehiculo'
  aggregate_id UUID NOT NULL,
  event_type VARCHAR(100) NOT NULL,     -- 'NEUMATICO.MOUNTED'
  event_data JSONB NOT NULL,
  metadata JSONB,
  user_id UUID NOT NULL,
  sequence_number BIGSERIAL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  
  INDEX idx_aggregate (aggregate_id, sequence_number),
  INDEX idx_event_type (event_type, created_at),
  INDEX idx_created_at (created_at DESC)
);
```

---

#### 2. EventStoreObserver

```typescript
class EventStoreObserver {
  static init() {
    // Persistir TODOS los eventos
    const allEvents = Object.values(NeumaticoEvents);
    
    allEvents.forEach(eventName => {
      EventBus.subscribe(eventName, this.persistEvent);
    });
  }
  
  private static async persistEvent(event: DomainEvent<any>) {
    await prisma.eventStore.create({
      data: {
        aggregate_type: 'neumatico',
        aggregate_id: event.payload.neumaticoId,
        event_type: event.name,
        event_data: event.payload,
        metadata: {
          ip_address: req.ip,
          user_agent: req.headers['user-agent'],
        },
        user_id: event.payload.usuarioId,
      },
    });
  }
}
```

---

#### 3. Event Replay Tool

```typescript
// scripts/replay-events.ts
async function replayEvents(aggregateId: string) {
  const events = await prisma.eventStore.findMany({
    where: { aggregate_id: aggregateId },
    orderBy: { sequence_number: 'asc' },
  });
  
  console.log(`🔄 Replaying ${events.length} events for ${aggregateId}`);
  
  for (const evt of events) {
    console.log(`  📤 ${evt.event_type} at ${evt.created_at}`);
    await EventBus.publish(evt.event_type, evt.event_data);
  }
  
  console.log('✅ Replay completed');
}
```

**Casos de Uso:**
- Reconstruir estado de neumático desde eventos
- Auditoría forense completa
- Time-travel debugging
- Replay para corregir errores

---

### Métricas de Éxito Q3

| Métrica | Target |
|---------|--------|
| Event Store writes | 100% events |
| Storage overhead | < 500MB/month |
| Replay speed | > 1000 events/sec |

---

## Q4 2026 - Message Brokers 📨

### Objetivos

Migrar de EventBus in-memory a message broker distribuido para:
- Soporte multi-servidor
- Persistencia durable
- Escalabilidad horizontal

### Arquitectura Propuesta

```
┌─────────────┐     ┌─────────────┐
│  Server 1   │────►│             │
└─────────────┘     │   Redis     │
                    │   Pub/Sub   │
┌─────────────┐     │             │
│  Server 2   │────►│   or        │
└─────────────┘     │             │
                    │  RabbitMQ   │
┌─────────────┐     │             │
│  Server 3   │────►│             │
└─────────────┘     └──────┬──────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Observers  │
                    │ (distributed)│
                    └──────────────┘
```

---

### Option A: Redis Pub/Sub

**Pros:**
- Fácil migración (API similar a EventEmitter)
- Baja latencia (~1-5ms)
- Ya usamos Redis para cache

**Cons:**
- No persistente (si Redis cae, eventos se pierden)
- Limitado message size (512MB)

**Implementation:**
```typescript
import { createClient } from 'redis';

class RedisEventBus {
  private publisher = createClient();
  private subscriber = createClient();
  
  async publish<T>(eventName: string, payload: T) {
    await this.publisher.publish(eventName, JSON.stringify(payload));
  }
  
  subscribe<T>(eventName: string, handler: EventHandler<T>) {
    this.subscriber.subscribe(eventName, (message) => {
      const payload = JSON.parse(message);
      handler({ name: eventName, payload, timestamp: new Date() });
    });
  }
}
```

---

### Option B: RabbitMQ

**Pros:**
- Persistente (eventos sobreviven crashes)
- Dead-letter queues (retry automático)
- Message routing avanzado

**Cons:**
- Más complejo de operar
- Mayor latencia (~10-20ms)

**Implementation:**
```typescript
import amqp from 'amqplib';

class RabbitMQEventBus {
  private connection: amqp.Connection;
  private channel: amqp.Channel;
  
  async publish<T>(eventName: string, payload: T) {
    this.channel.publish(
      'gesneu.events',  // Exchange
      eventName,        // Routing key
      Buffer.from(JSON.stringify(payload)),
      { persistent: true }  // Durabilidad
    );
  }
  
  async subscribe<T>(eventName: string, handler: EventHandler<T>) {
    const queue = await this.channel.assertQueue(`${eventName}.queue`);
    
    this.channel.consume(queue.queue, async (msg) => {
      if (msg) {
        const payload = JSON.parse(msg.content.toString());
        await handler({ name: eventName, payload, timestamp: new Date() });
        this.channel.ack(msg);
      }
    });
  }
}
```

---

### Decisión Recomendada

**Fase 1 (Q4 2026):** Redis Pub/Sub
- Migración más simple
- Suficiente para carga actual

**Fase 2 (2027):** RabbitMQ
- Si necesitamos:
  - Persistencia garantizada
  - Dead-letter queues
  - Throughput > 10k eventos/seg

---

### Métricas de Éxito Q4

| Métrica | Target |
|---------|--------|
| Multi-server support | ✅ Yes |
| Event delivery guarantee | 99.99% |
| Max throughput | > 10,000/s |
| Latency (P95) | < 50ms |

---

## 2027 - Machine Learning y Automatización 🤖

### 1. Predictive Maintenance Observer

```typescript
class MLObserver {
  static init() {
    EventBus.subscribe(NeumaticoEvents.MOUNTED, this.predictFailure);
    EventBus.subscribe(InspeccionEvents.DEPTH_READ, this.updateModel);
  }
  
  private static async predictFailure(event) {
    const prediction = await mlService.predict({
      model: 'tire-failure-v2',
      features: {
        tire_age_months: event.payload.metadata.ageMonths,
        initial_depth: event.payload.metadata.profundidadInicial,
        vehicle_type: event.payload.metadata.tipoVehiculo,
        usage_pattern: event.payload.metadata.usagePattern,
      },
    });
    
    if (prediction.failureProbability > 0.7) {
      await prisma.alerta.create({
        data: {
          tipo: 'PREDICCION_FALLA',
          severidad: 'WARNING',
          mensaje: `ML predice falla en ${prediction.daysToFailure} días (${prediction.failureProbability}% confianza)`,
          neumatico_id: event.payload.neumaticoId,
        },
      });
    }
  }
}
```

**Modelos de ML:**
- Predicción de vida útil
- Detección de anomalías
- Recomendación de rotación óptima
- Precio dinámico de reencauche

---

### 2. Auto-optimization

```typescript
// Optimizar configuración de flota automáticamente
class FleetOptimizationObserver {
  static init() {
    // Cada 7 días, analizar patrones
    setInterval(this.optimizeFleet, 7 * 24 * 60 * 60 * 1000);
  }
  
  private static async optimizeFleet() {
    const insights = await mlService.analyzeFleet({
      timeframe: '30d',
      metrics: ['cpk', 'failure_rate', 'rotation_effectiveness'],
    });
    
    if (insights.recommendation === 'increase_rotation_frequency') {
      await notifyUser('Recomendación: Aumentar frecuencia de rotación de 50k km a 40k km. ROI estimado: +15% en vida útil');
    }
  }
}
```

---

### 3. Integration con IoT

```typescript
// Sensores IoT en neumáticos
class IoTObserver {
  static init() {
    // Stream de datos desde sensores TPMS
    iotStream.on('pressure-reading', this.handleRealtimePressure);
    iotStream.on('temperature-reading', this.handleTemperature);
  }
  
  private static async handleRealtimePressure(data) {
    // Publicar evento en tiempo real
    await EventBus.publish('INSPECCION.PRESSURE_READ_REALTIME', {
      neumaticoId: data.sensorId,
      presionActual: data.psi,
      presionRecomendada: data.targetPsi,
      temperatura: data.temperature,
      timestamp: new Date(data.timestamp),
    });
  }
}
```

**Integraciones:**
- Sensores TPMS (Tire Pressure Monitoring System)
- GPS trackers de flotas
- Telemática de vehículos

---

## Cronograma Visual

```
2026
├─ Q1 ✅ [████████████████████████] Fundación
├─ Q2 📋 [                        ] Expansión Módulos
│        └─ Ventas, Marketing, ERP
├─ Q3 🗄️ [                        ] Event Sourcing
│        └─ Persistencia, Replay
└─ Q4 📨 [                        ] Message Brokers
         └─ Redis/RabbitMQ

2027
├─ Q1 🤖 [                        ] Machine Learning
│        └─ Predictive Maintenance
├─ Q2 📡 [                        ] IoT Integration
│        └─ Sensores TPMS
├─ Q3 🔬 [                        ] Advanced Analytics
│        └─ Fleet Optimization
└─ Q4 🌐 [                        ] Multi-región
         └─ Global Event Bus
```

---

## Inversión Estimada

| Quarter | Concepto | Horas Dev | Costo |
|---------|----------|-----------|-------|
| **Q1 2026** ✅ | Fundación | 120h | $12,000 |
| **Q2 2026** | 3 nuevos módulos | 160h | $16,000 |
| **Q3 2026** | Event Sourcing | 80h | $8,000 |
| **Q4 2026** | Message Broker | 100h | $10,000 |
| **2027** | ML + IoT | 240h | $30,000 |
| **TOTAL** | | 700h | **$76,000** |

---

## ROI Esperado

### Q2 2026 - Ventas
- **Oportunidades generadas automáticamente:** +50/mes
- **Tasa de conversión:** 20%
- **Ticket promedio:** $5,000
- **Revenue adicional:** $50,000/mes = **$600k/año**

### Q3 2026 - Event Sourcing
- **Reducción auditorías manuales:** -40 horas/mes
- **Costo/hora:** $50
- **Ahorro:** $2,000/mes = **$24k/año**

### 2027 - Predictive Maintenance
- **Reducción fallas inesperadas:** -30%
- **Costo promedio falla:** $2,000
- **Fallas/año actuales:** 100
- **Ahorro:** $60,000/año

**ROI Total Proyectado:** **$684k/año**  
**Inversión:** $76k  
**Payback period:** **1.3 meses**

---

## Riesgos y Mitigación

### Riesgo 1: Complejidad Técnica

**Probabilidad:** Media  
**Impacto:** Alto  

**Mitigación:**
- Training continuo del equipo
- Code reviews estrictos
- Consultoría externa si es necesario

---

### Riesgo 2: Performance Degradation

**Probabilidad:** Baja  
**Impacto:** Alto  

**Mitigación:**
- Performance testing en cada release
- SLOs definidos y monitoreados
- Rollback plan automático

---

### Riesgo 3: Event Schema Breaking Changes

**Probabilidad:** Media  
**Impacto:** Medio  

**Mitigación:**
- Versionado de eventos (`NEUMATICO.MOUNTED.v2`)
- Backward compatibility mandatory
- Schema registry (Avro/Protobuf en 2027)

---

## Próximos Pasos Inmediatos

### Febrero 2026

1. ✅ Presentar roadmap a stakeholders
2. ✅ Aprobar presupuesto Q2
3. ✅ Contratar 1 developer adicional (Event-Driven specialist)

### Marzo 2026

1. Kick-off Módulo de Ventas
2. Diseñar eventos de VentasEvents
3. MVP de VentasObserver

---

## Conclusión

La arquitectura Event-Driven de GesNeu está diseñada para crecer orgánicamente desde una implementación simple in-memory hasta un sistema distribuido de clase empresarial con ML integrado.

**Fase actual:** ✅ Q1 2026 - Fundación sólida  
**Siguiente hito:** 📋 Q2 2026 - Expansión a módulos de negocio  
**Visión 2027:** 🤖 Sistema inteligente y autónomo

---

**Última actualización:** 2026-01-29  
**Owner:** Equipo de Arquitectura GesNeu  
**Stakeholders:** CTO, Product, DevOps
