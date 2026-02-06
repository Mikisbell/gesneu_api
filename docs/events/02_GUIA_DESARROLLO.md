# 🛠️ Guía de Desarrollo - Event-Driven Architecture

> **Audiencia:** Desarrolladores que trabajarán con el sistema de eventos  
> **Última actualización:** Enero 2026  
> **Nivel:** Práctico - Step by step

---

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Cómo Crear un Nuevo Evento](#cómo-crear-un-nuevo-evento)
3. [Cómo Crear un Nuevo Observer](#cómo-crear-un-nuevo-observer)
4. [Convenciones y Mejores Prácticas](#convenciones-y-mejores-prácticas)
5. [Testing](#testing)
6. [Code Review Checklist](#code-review-checklist)

---

## Introducción

Esta guía te enseñará a trabajar con el sistema Event-Driven de GesNeu. Asumimos que ya leíste:
- [Arquitectura de Eventos](./01_ARQUITECTURA_EVENTOS.md) (para entender el "por qué")
- Esta guía te enseña el "cómo"

**Flujo básico:**
```
1. Algo pasa en el sistema (ej: se desecha un neumático)
2. EventoNeumaticoService emite un evento
3. Observers reaccionan automáticamente
```

---

## Cómo Crear un Nuevo Evento

### Paso 1: Definir el Tipo de Evento y Payload

**Archivo:** `src/lib/events/neumatico.events.ts` (o crear nuevo archivo si es otro módulo)

```typescript
// 1. Agregar constante del evento
export const NeumaticoEvents = {
  // ... eventos existentes
  MY_NEW_EVENT: 'NEUMATICO.MY_NEW_EVENT',  // ⬅️ NUEVO
} as const;

// 2. Definir el payload (heredar de BaseNeumaticoPayload)
export interface MyNewEventPayload extends BaseNeumaticoPayload {
  // Campos específicos de tu evento
  customField: string;
  anotherField: number;
  metadata: {
    optionalData?: string;
  };
}
```

**Convenciones de nombres:**
- **Constante:** `SCREAMING_SNAKE_CASE`
- **Namespace:** `NEUMATICO.`, `INSPECCION.`, `REENCAUCHE.`
- **Acción:** En **pasado** (CREATED, MOUNTED, DELETED)
- **Payload interface:** `PascalCase` terminando en `Payload`

---

### Paso 2: Emitir el Evento desde el Service

**Archivo:** `src/lib/services/evento-neumatico.service.ts`

```typescript
// Dentro del método _emitDomainEvent()
private async _emitDomainEvent(evento: EventoResponse) {
  const eventName = this._mapTipoEventoToEventName(evento.tipo);
  
  // ... código existente ...
  
  // Agregar tu nuevo evento al switch
  switch (evento.tipo) {
    // ... casos existentes ...
    
    case TipoEventoEnum.MY_NEW_TYPE: {  // ⬅️ Mapear desde DB enum
      const payload: MyNewEventPayload = {
        neumaticoId: evento.neumatico_id,
        empresaId: evento.empresa_id,
        usuarioId: evento.usuario_id,
        timestamp: evento.fecha_evento,
        customField: evento.metadata?.customField || '',
        anotherField: evento.metadata?.anotherField || 0,
        metadata: evento.metadata || {},
      };
      
      await EventBus.publish(NeumaticoEvents.MY_NEW_EVENT, payload);
      break;
    }
  }
}
```

**Importante:**
- ✅ Emitir eventos **DESPUÉS** del `COMMIT` de la transacción
- ✅ Payload debe ser **inmutable** (solo lectura)
- ✅ Nunca hacer `throw` si falla el evento (tolerancia a fallos)

---

### Paso 3: Actualizar el Enum de la Base de Datos (Opcional)

Si el evento representa un nuevo tipo de operación, agregar al enum:

**Archivo:** `prisma/schema.prisma`

```prisma
enum TipoEventoEnum {
  // ... tipos existentes
  MY_NEW_TYPE  // ⬅️ NUEVO
}
```

Luego migrar:
```bash
npx prisma migrate dev --name add_my_new_event_type
```

---

## Cómo Crear un Nuevo Observer

### Paso 1: Crear el Archivo del Observer

**Archivo:** `src/lib/observers/my-feature.observer.ts`

```typescript
import { EventBus, DomainEvent } from '../events/core';
import { NeumaticoEvents, MyNewEventPayload } from '../events/neumatico.events';
import { prisma } from '@/lib/db';

export class MyFeatureObserver {
  /**
   * Inicializar suscripciones
   */
  static init() {
    console.log('🚀 [Observer] Initializing MyFeature System...');
    
    // Suscribirse a los eventos que te interesan
    EventBus.subscribe<MyNewEventPayload>(
      NeumaticoEvents.MY_NEW_EVENT,
      this.handleMyNewEvent
    );
    
    EventBus.subscribe<TireScrappedPayload>(
      NeumaticoEvents.SCRAPPED,
      this.handleScrapped
    );
    
    console.log('✅ [MyFeatureObserver] Subscribed to 2 event types');
  }

  /**
   * Handler para MY_NEW_EVENT
   */
  private static async handleMyNewEvent(event: DomainEvent<MyNewEventPayload>) {
    try {
      const { payload } = event;
      
      console.log(`[MyFeature] Processing: ${payload.customField}`);
      
      // Tu lógica aquí
      // Ejemplo: Guardar en DB, llamar API externa, etc.
      await prisma.myTable.create({
        data: {
          neumatico_id: payload.neumaticoId,
          custom_data: payload.customField,
        },
      });
      
    } catch (error) {
      // ⚠️ NUNCA hacer throw - solo logear
      console.error('[MyFeatureObserver] Error in handleMyNewEvent:', error);
    }
  }

  /**
   * Handler para SCRAPPED
   */
  private static async handleScrapped(event: DomainEvent<TireScrappedPayload>) {
    try {
      // Tu lógica para cuando se desecha un neumático
      console.log(`[MyFeature] Tire scrapped: ${event.payload.neumaticoId}`);
    } catch (error) {
      console.error('[MyFeatureObserver] Error in handleScrapped:', error);
    }
  }
}
```

**Estructura obligatoria:**
- ✅ Método estático `init()` que registra suscripciones
- ✅ Handlers privados estáticos (no instanciar la clase)
- ✅ Try-catch en TODOS los handlers
- ✅ NO hacer `throw` en los handlers
- ✅ Logs descriptivos con prefijo `[NombreObserver]`

---

### Paso 2: Registrar el Observer

**Archivo:** `src/lib/events/registry.ts`

```typescript
import { MyFeatureObserver } from '../observers/my-feature.observer';  // ⬅️ Importar

let initialized = false;

export const registerObservers = () => {
  if (initialized) return;

  // Observers existentes
  CacheObserver.init();
  AlertObserver.init();
  NeumaticoUpdateObserver.init();
  AuditObserver.init();
  NotificationObserver.init();
  AnalyticsObserver.init();
  
  // Tu nuevo observer
  MyFeatureObserver.init();  // ⬅️ Registrar

  initialized = true;
  console.log("✅ [System] All 7 Observers Registered");  // ⬅️ Actualizar count
};
```

---

### Paso 3: Verificar el Registro

Ejecutar el build y verificar logs:

```bash
npm run build | grep "Observer"
```

Deberías ver:
```
🚀 [Observer] Initializing MyFeature System...
✅ [MyFeatureObserver] Subscribed to 2 event types
✅ [System] All 7 Observers Registered
```

---

## Convenciones y Mejores Prácticas

### Nombres de Eventos

| ✅ Correcto | ❌ Incorrecto |
|------------|--------------|
| `NEUMATICO.MOUNTED` | `NEUMATICO.MOUNT` (presente) |
| `NEUMATICO.SCRAPPED` | `neumatico_scrapped` (snake_case) |
| `INSPECCION.PRESSURE_READ` | `PRESSURE_CHECKED` (sin namespace) |

**Regla:** `NAMESPACE.PAST_TENSE_ACTION`

---

### Payloads

#### ✅ DO:
```typescript
export interface GoodPayload extends BaseNeumaticoPayload {
  // Campos inmutables, solo lectura implícita
  status: EstadoNeumaticoEnum;
  timestamp: Date;
  metadata: {
    optional?: string;
  };
}
```

#### ❌ DON'T:
```typescript
export interface BadPayload {
  // ❌ No heredar de Base
  id: string;  // ❌ Usar 'neumaticoId' por convención
  mutableField: any;  // ❌ No usar 'any'
}
```

---

### Observers

#### ✅ DO:
```typescript
static async handleEvent(event: DomainEvent<Payload>) {
  try {
    // Lógica del observer
    await someAsyncOperation();
  } catch (error) {
    // ✅ Logear y continuar
    console.error('[Observer] Error:', error);
  }
}
```

#### ❌ DON'T:
```typescript
static async handleEvent(event: DomainEvent<Payload>) {
  // ❌ Sin try-catch
  await someAsyncOperation();
  
  // ❌ Hacer throw
  if (error) throw new Error('Something failed');
}
```

**Por qué:** Observers deben ser tolerantes a fallos. Un observer fallando no debe romper otros observers ni la transacción principal.

---

### Performance

#### Evita Operaciones Pesadas en Observers
```typescript
// ❌ MAL: Operación síncrona pesada
static handleEvent(event) {
  const result = calculateComplexMetrics();  // 5 segundos!
  await saveResult(result);
}

// ✅ BIEN: Delegar a job async
static handleEvent(event) {
  // Solo encolar el job, no ejecutarlo
  await jobQueue.add('calculate-metrics', { eventId: event.payload.id });
}
```

**Regla:** Si una operación toma > 100ms, considerar usar un job queue (futuro: BullMQ).

---

## Testing

### Unit Test de un Observer

**Archivo:** `src/lib/observers/__tests__/my-feature.observer.test.ts`

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MyFeatureObserver } from '../my-feature.observer';
import { NeumaticoEvents } from '@/lib/events/neumatico.events';
import { EventBus } from '@/lib/events/core';

// Mock de Prisma
vi.mock('@/lib/db', () => ({
  prisma: {
    myTable: {
      create: vi.fn(),
    },
  },
}));

describe('MyFeatureObserver', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should handle MY_NEW_EVENT correctly', async () => {
    // Arrange
    const payload = {
      neumaticoId: 'test-123',
      empresaId: 'empresa-123',
      usuarioId: 'user-123',
      timestamp: new Date(),
      customField: 'test-value',
      anotherField: 42,
      metadata: {},
    };

    // Act
    await EventBus.publish(NeumaticoEvents.MY_NEW_EVENT, payload);

    // Assert
    expect(prisma.myTable.create).toHaveBeenCalledWith({
      data: expect.objectContaining({
        neumatico_id: 'test-123',
        custom_data: 'test-value',
      }),
    });
  });

  it('should not throw if database fails', async () => {
    // Arrange
    prisma.myTable.create.mockRejectedValueOnce(new Error('DB Error'));

    // Act & Assert
    await expect(async () => {
      await EventBus.publish(NeumaticoEvents.MY_NEW_EVENT, {
        /* payload */
      });
    }).not.toThrow();
  });
});
```

---

### Integration Test de Flujo Completo

**Archivo:** `src/lib/services/__tests__/evento-neumatico-integration.test.ts`

```typescript
import { describe, it, expect } from 'vitest';
import { EventoNeumaticoService } from '../evento-neumatico.service';
import { EventBus } from '@/lib/events/core';
import { NeumaticoEvents } from '@/lib/events/neumatico.events';

describe('EventoNeumaticoService Integration', () => {
  it('should emit event after registering evento', async () => {
    // Arrange
    const service = new EventoNeumaticoService();
    const publishSpy = vi.spyOn(EventBus, 'publish');

    // Act
    await service.registrarEvento({
      tipo: TipoEventoEnum.MONTAJE,
      neumatico_id: 'test-123',
      // ... otros campos
    }, 'user-123');

    // Assert
    expect(publishSpy).toHaveBeenCalledWith(
      NeumaticoEvents.MOUNTED,
      expect.objectContaining({
        neumaticoId: 'test-123',
      })
    );
  });
});
```

---

## Code Review Checklist

Cuando crees un PR con cambios en el sistema de eventos, verifica:

### Eventos
- [ ] Evento nombrado en pasado (`CREATED`, no `CREATE`)
- [ ] Namespace correcto (`NEUMATICO.`, `INSPECCION.`, etc.)
- [ ] Payload hereda de `BaseNeumaticoPayload`
- [ ] Payload fuertemente tipado (sin `any`)
- [ ] Validado con Zod (si viene de API)

### Observers
- [ ] Archivo nombrado `*.observer.ts`
- [ ] Método `init()` estático presente
- [ ] Handlers privados y estáticos
- [ ] Try-catch en TODOS los handlers
- [ ] NO hace `throw` en handlers
- [ ] Logs con prefijo `[NombreObserver]`
- [ ] Registrado en `registry.ts`

### Performance
- [ ] Operaciones pesadas (> 100ms) delegadas a jobs
- [ ] No bloquea el hilo principal
- [ ] Async/await usado correctamente

### Testing
- [ ] Unit tests del observer creados
- [ ] Integration test del flujo completo
- [ ] Coverage > 80% en nuevos archivos

### Documentación
- [ ] Comentarios JSDoc en métodos públicos
- [ ] README actualizado (si aplica)
- [ ] Catálogo de eventos actualizado

---

## Ejemplos Completos

### Ejemplo 1: Observer Simple (Solo Logs)

```typescript
// src/lib/observers/simple-logger.observer.ts
import { EventBus, DomainEvent } from '../events/core';
import { NeumaticoEvents, TireScrappedPayload } from '../events/neumatico.events';

export class SimpleLoggerObserver {
  static init() {
    EventBus.subscribe<TireScrappedPayload>(
      NeumaticoEvents.SCRAPPED,
      this.logScrap
    );
  }

  private static async logScrap(event: DomainEvent<TireScrappedPayload>) {
    console.log(`[SimpleLogger] Tire ${event.payload.neumaticoId} scrapped`);
  }
}
```

---

### Ejemplo 2: Observer con Lógica de Negocio

```typescript
// src/lib/observers/warranty.observer.ts
import { EventBus, DomainEvent } from '../events/core';
import { NeumaticoEvents, TireScrappedPayload } from '../events/neumatico.events';
import { prisma } from '@/lib/db';

export class WarrantyObserver {
  private static readonly EARLY_SCRAP_KM = 20000;

  static init() {
    EventBus.subscribe<TireScrappedPayload>(
      NeumaticoEvents.SCRAPPED,
      this.checkWarranty
    );
  }

  private static async checkWarranty(event: DomainEvent<TireScrappedPayload>) {
    try {
      const { neumaticoId, metadata } = event.payload;

      // Si se desechó antes de 20,000 km, verificar garantía
      if (metadata.kmTotales < this.EARLY_SCRAP_KM) {
        console.log(`[Warranty] Checking warranty for ${neumaticoId}`);

        // Buscar información del neumático
        const neumatico = await prisma.neumatico.findUnique({
          where: { id: neumaticoId },
          include: { modeloNeumatico: { include: { fabricante: true } } },
        });

        if (!neumatico) return;

        // Calcular edad del neumático
        const ageMonths = this.calculateAgeInMonths(
          neumatico.fecha_compra,
          new Date()
        );

        // Si tiene < 12 meses Y < 20k km, crear caso de garantía
        if (ageMonths < 12) {
          await prisma.warrantyClaim.create({
            data: {
              tire_id: neumaticoId,
              manufacturer_id: neumatico.modeloNeumatico.fabricante.id,
              reason: metadata.motivoTexto,
              km_at_failure: metadata.kmTotales,
              age_months: ageMonths,
              status: 'PENDING',
            },
          });

          console.log(`✅ [Warranty] Claim created for ${neumaticoId}`);
        }
      }
    } catch (error) {
      console.error('[WarrantyObserver] Error checking warranty:', error);
    }
  }

  private static calculateAgeInMonths(start: Date, end: Date): number {
    const months = (end.getFullYear() - start.getFullYear()) * 12;
    return months + (end.getMonth() - start.getMonth());
  }
}
```

---

### Ejemplo 3: Observer que Llama API Externa

```typescript
// src/lib/observers/external-api.observer.ts
import { EventBus, DomainEvent } from '../events/core';
import { NeumaticoEvents, TireScrappedPayload } from '../events/neumatico.events';

export class ExternalAPIObserver {
  static init() {
    EventBus.subscribe<TireScrappedPayload>(
      NeumaticoEvents.SCRAPPED,
      this.notifyExternalSystem
    );
  }

  private static async notifyExternalSystem(event: DomainEvent<TireScrappedPayload>) {
    try {
      const { neumaticoId, metadata } = event.payload;

      // Llamar a API externa (con timeout)
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000); // 5s timeout

      const response = await fetch('https://external-api.com/tires/scrapped', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tireId: neumaticoId,
          reason: metadata.motivoTexto,
          mileage: metadata.kmTotales,
        }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        console.error(`[ExternalAPI] HTTP ${response.status}`);
        return;
      }

      console.log(`✅ [ExternalAPI] Notified external system about ${neumaticoId}`);
    } catch (error) {
      if (error.name === 'AbortError') {
        console.error('[ExternalAPI] Request timeout');
      } else {
        console.error('[ExternalAPI] Error calling external API:', error);
      }
    }
  }
}
```

---

## Debugging

### Cómo Ver Qué Observers Están Suscritos

```typescript
// En cualquier archivo
import { EventBus } from '@/lib/events/core';

const listenerCount = (EventBus as any).listenerCount('NEUMATICO.MOUNTED');
console.log(`Listeners for MOUNTED: ${listenerCount}`);
```

---

### Cómo Testear un Observer Manualmente

```typescript
// En un script de test o REPL
import { EventBus } from '@/lib/events/core';
import { NeumaticoEvents } from '@/lib/events/neumatico.events';
import { registerObservers } from '@/lib/events/registry';

// 1. Registrar observers
registerObservers();

// 2. Emitir evento de prueba
await EventBus.publish(NeumaticoEvents.MOUNTED, {
  neumaticoId: 'test-123',
  empresaId: '00000000-0000-0000-0000-000000000000',
  usuarioId: 'test-user',
  timestamp: new Date(),
  vehiculoId: 'vehicle-123',
  posicionId: 'FL',
  kilometrajeVehiculo: 50000,
  metadata: {},
});

// 3. Revisar logs en consola
```

---

## Troubleshooting

### Error: "Observer no se registra"
**Síntoma:** El observer no reacciona a eventos.

**Solución:**
1. Verificar que `init()` esté en `registry.ts`
2. Verificar que el nombre del evento coincida exactamente
3. Revisar consola para ver si hubo error en `init()`

---

### Error: "EventBus is not defined"
**Síntoma:** `ReferenceError: EventBus is not defined`

**Solución:**
```typescript
// ✅ Correcto
import { EventBus } from '@/lib/events/core';

// ❌ Incorrecto
import EventBus from '@/lib/events/core';  // Default export no existe
```

---

### Warning: "Possible EventEmitter memory leak"
**Síntoma:** `MaxListenersExceededWarning: Possible EventEmitter memory leak detected`

**Solución:**
- Actualmente el límite es 20 observers por evento
- Si necesitas más, actualizar en `core.ts`:
  ```typescript
  this.setMaxListeners(50);  // Aumentar límite
  ```

---

## Próximos Pasos

Ahora que sabes crear eventos y observers, consulta:
- [Catálogo de Eventos](./03_EVENTOS_CATALOGO.md) - Referencia de los 11 eventos
- [Catálogo de Observers](./04_OBSERVERS_CATALOGO.md) - Referencia de los 6 observers
- [Testing de Eventos](./05_TESTING_EVENTOS.md) - Estrategias avanzadas de testing

---

**Última actualización:** 2026-01-29  
**Mantenido por:** Equipo de Arquitectura GesNeu
