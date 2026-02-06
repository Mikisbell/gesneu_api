# 📋 Catálogo de Eventos - Event-Driven Architecture

> **Audiencia:** Desarrolladores, Arquitectos  
> **Última actualización:** Enero 2026  
> **Nivel:** Referencia técnica

---

## Tabla de Contenidos

1. [Vista General](#vista-general)
2. [Eventos de Neumáticos](#eventos-de-neumáticos) (11 eventos)
3. [Eventos de Inspección](#eventos-de-inspección) (2 eventos)
4. [Eventos de Reencauche](#eventos-de-reencauche) (2 eventos)
5. [Matriz de Observers](#matriz-de-observers)

---

## Vista General

GesNeu implementa **11 tipos de eventos de dominio** para neumáticos, cada uno representando un cambio significativo en el ciclo de vida del neumático.

### Características Comunes

Todos los eventos heredan de `BaseNeumaticoPayload`:

```typescript
interface BaseNeumaticoPayload {
  neumaticoId: string;         // UUID del neumático
  empresaId: string;            // UUID de la empresa (actualmente DEFAULT_TENANT_ID)
  usuarioId: string;            // UUID del usuario que ejecutó la acción
  timestamp: Date;              // Cuándo ocurrió el evento
}
```

---

## Eventos de Neumáticos

### 1. NEUMATICO.PURCHASED 🛒

**Cuándo se dispara:** Al registrar la compra de un neumático nuevo.

**Payload:**
```typescript
interface TirePurchasedPayload extends BaseNeumaticoPayload {
  marcaId: string;
  modeloId: string;
  profundidadInicial: number;     // mm
  costoCompra: number;             // USD
  metadata: {
    proveedorId?: string;
    factura?: string;
    garantiaMeses?: number;
  };
}
```

**Observers que reaccionan:**
- ✅ `AuditObserver` - Registra la compra
- ✅ `AnalyticsObserver` - Actualiza inventario

**Ejemplo de uso:**
```typescript
await EventBus.publish(NeumaticoEvents.PURCHASED, {
  neumaticoId: 'abc-123',
  empresaId: DEFAULT_TENANT_ID,
  usuarioId: 'user-456',
  timestamp: new Date(),
  marcaId: 'bridgestone-789',
  modeloId: 'r19-commercial',
  profundidadInicial: 18.5,
  costoCompra: 450.00,
  metadata: {
    proveedorId: 'prov-987',
    factura: 'F-2026-001',
    garantiaMeses: 24,
  },
});
```

---

### 2. NEUMATICO.MOUNTED 🔧

**Cuándo se dispara:** Al instalar un neumático en un vehículo.

**Payload:**
```typescript
interface TireMountedPayload extends BaseNeumaticoPayload {
  vehiculoId: string;
  posicionId: string;              // FL, FR, RL, RR, etc.
  kilometrajeVehiculo: number;
  metadata: {
    almacenOrigenId?: string;
    profundidadActual?: number;
    presion?: number;
  };
}
```

**Observers que reaccionan:**
- ✅ `AuditObserver` - Registra montaje
- ✅ `AnalyticsObserver` - Invalida caché de flota

**Ejemplo:**
```typescript
await EventBus.publish(NeumaticoEvents.MOUNTED, {
  neumaticoId: 'tire-123',
  empresaId: DEFAULT_TENANT_ID,
  usuarioId: 'mech-001',
  timestamp: new Date(),
  vehiculoId: 'truck-456',
  posicionId: 'FL',  // Front Left
  kilometrajeVehiculo: 25000,
  metadata: {
    almacenOrigenId: 'wh-central',
    profundidadActual: 17.2,
    presion: 110,
  },
});
```

---

### 3. NEUMATICO.DISMOUNTED 🔓

**Cuándo se dispara:** Al desmontar un neumático de un vehículo.

**Payload:**
```typescript
interface TireDismountedPayload extends BaseNeumaticoPayload {
  vehiculoId: string;
  posicionId: string;
  kilometrajeVehiculo: number;
  motivoTexto: string;
  metadata: {
    almacenDestinoId?: string;
    profundidadFinal?: number;
    kmRecorridos?: number;
  };
}
```

**Observers que reaccionan:**
- ✅ `AuditObserver`
- ✅ `NotificationObserver` - Alertas si desmontaje prematuro
- ✅ `AnalyticsObserver`

**Ejemplo:**
```typescript
await EventBus.publish(NeumaticoEvents.DISMOUNTED, {
  neumaticoId: 'tire-123',
  empresaId: DEFAULT_TENANT_ID,
  usuarioId: 'mech-001',
  timestamp: new Date(),
  vehiculoId: 'truck-456',
  posicionId: 'FL',
  kilometrajeVehiculo: 75000,
  motivoTexto: 'Desgaste irregular detectado',
  metadata: {
    almacenDestinoId: 'wh-repair',
    profundidadFinal: 5.2,
    kmRecorridos: 50000,
  },
});
```

---

### 4. NEUMATICO.ROTATED 🔄

**Cuándo se dispara:** Al rotar un neumático entre posiciones dentro del mismo vehículo.

**Payload:**
```typescript
interface TireRotatedPayload extends BaseNeumaticoPayload {
  vehiculoId: string;
  posicionOrigenId: string;
  posicionDestinoId: string;
  kilometrajeVehiculo: number;
  metadata: {
    profundidadActual?: number;
    razonRotacion?: string;
  };
}
```

**Observers que reaccionan:**
- ✅ `AuditObserver`
- ✅ `AnalyticsObserver` - Métricas de rotación

**Ejemplo:**
```typescript
await EventBus.publish(NeumaticoEvents.ROTATED, {
  neumaticoId: 'tire-123',
  empresaId: DEFAULT_TENANT_ID,
  usuarioId: 'mech-002',
  timestamp: new Date(),
  vehiculoId: 'truck-456',
  posicionOrigenId: 'FL',
  posicionDestinoId: 'RL',
  kilometrajeVehiculo: 50000,
  metadata: {
    profundidadActual: 12.5,
    razonRotacion: 'Mantenimiento preventivo - 50k km',
  },
});
```

---

### 5. NEUMATICO.SCRAPPED 🗑️

**Cuándo se dispara:** Al desechar/dar de baja un neumático.

**Payload:**
```typescript
interface TireScrappedPayload extends BaseNeumaticoPayload {
  motivoTexto: string;
  profundidadFinal: number;
  metadata: {
    kmTotales: number;
    costoTotal: number;
    vidaAlcanzada: number;      // 1 = Primera vida, 2 = Reencauchado 1 vez
    numeroSerie?: string;
  };
}
```

**Observers que reaccionan:**
- ✅ `AuditObserver`
- ✅ `NotificationObserver` - Alertas de desecho prematuro/alto valor
- ✅ `AnalyticsObserver` - CPK calculation

**Ejemplo:**
```typescript
await EventBus.publish(NeumaticoEvents.SCRAPPED, {
  neumaticoId: 'tire-123',
  empresaId: DEFAULT_TENANT_ID,
  usuarioId: 'admin-001',
  timestamp: new Date(),
  motivoTexto: 'Desgaste completo - Fin de vida útil',
  profundidadFinal: 1.5,
  metadata: {
    kmTotales: 120000,
    costoTotal: 450,
    vidaAlcanzada: 2,  // Reencauchado 1 vez
    numeroSerie: 'BRS-2024-12345',
  },
});
```

**Alertas automáticas:**
- Si `kmTotales < 20,000` → Alerta de desgaste prematuro
- Si `costoTotal > 5,000` → Alerta de alto valor

---

### 6. NEUMATICO.REPAIR_STARTED 🔨

**Cuándo se dispara:** Al iniciar una reparación de neumático.

**Payload:**
```typescript
interface TireRepairStartedPayload extends BaseNeumaticoPayload {
  tipoReparacion: string;
  costoEstimado: number;
  metadata: {
    descripcionDaño?: string;
    ubicacionDaño?: string;
    tecnicoId?: string;
  };
}
```

**Observers que reaccionan:**
- ✅ `AuditObserver`
- ✅ `AnalyticsObserver`

**Ejemplo:**
```typescript
await EventBus.publish(NeumaticoEvents.REPAIR_STARTED, {
  neumaticoId: 'tire-456',
  empresaId: DEFAULT_TENANT_ID,
  usuarioId: 'tech-003',
  timestamp: new Date(),
  tipoReparacion: 'Parche lateral',
  costoEstimado: 75.00,
  metadata: {
    descripcionDaño: 'Pinchazo por clavo',
    ubicacionDaño: 'Flanco lateral derecho',
    tecnicoId: 'tech-003',
  },
});
```

---

### 7. NEUMATICO.REPAIR_COMPLETED ✅

**Cuándo se dispara:** Al completar una reparación de neumático.

**Payload:**
```typescript
interface TireRepairCompletedPayload extends BaseNeumaticoPayload {
  tipoReparacion: string;
  costoFinal: number;
  exitoso: boolean;
  metadata: {
    descripcionTrabajo?: string;
    duracionHoras?: number;
  };
}
```

**Observers que reaccionan:**
- ✅ `AuditObserver`
- ✅ `AnalyticsObserver` - Tracking de costos de reparación

**Ejemplo:**
```typescript
await EventBus.publish(NeumaticoEvents.REPAIR_COMPLETED, {
  neumaticoId: 'tire-456',
  empresaId: DEFAULT_TENANT_ID,
  usuarioId: 'tech-003',
  timestamp: new Date(),
  tipoReparacion: 'Parche lateral',
  costoFinal: 80.00,
  exitoso: true,
  metadata: {
    descripcionTrabajo: 'Parche vulcanizado aplicado exitosamente',
    duracionHoras: 2.5,
  },
});
```

---

### 8. NEUMATICO.TRANSFERRED 📦

**Cuándo se dispara:** Al transferir un neumático entre almacenes.

**Payload:**
```typescript
interface TireTransferredPayload extends BaseNeumaticoPayload {
  almacenOrigenId: string;
  almacenDestinoId: string;
  metadata: {
    ordenTransferenciaId?: string;
    responsableTransporte?: string;
  };
}
```

**Observers que reaccionan:**
- ✅ `AuditObserver`
- ✅ `AnalyticsObserver` - Actualiza inventario por almacén

**Ejemplo:**
```typescript
await EventBus.publish(NeumaticoEvents.TRANSFERRED, {
  neumaticoId: 'tire-789',
  empresaId: DEFAULT_TENANT_ID,
  usuarioId: 'log-001',
  timestamp: new Date(),
  almacenOrigenId: 'wh-central',
  almacenDestinoId: 'wh-norte',
  metadata: {
    ordenTransferenciaId: 'TRF-2026-045',
    responsableTransporte: 'driver-12',
  },
});
```

---

### 9. NEUMATICO.RECLASSIFIED 🏷️

**Cuándo se dispara:** Al cambiar la clasificación/calidad del neumático.

**Payload:**
```typescript
interface TireReclassifiedPayload extends BaseNeumaticoPayload {
  clasificacionAnterior: string;
  clasificacionNueva: string;
  motivo: string;
  metadata: {
    profundidadActual?: number;
    inspeccionId?: string;
  };
}
```

**Observers que reaccionan:**
- ✅ `AuditObserver`
- ✅ `AnalyticsObserver`

**Ejemplo:**
```typescript
await EventBus.publish(NeumaticoEvents.RECLASSIFIED, {
  neumaticoId: 'tire-111',
  empresaId: DEFAULT_TENANT_ID,
  usuarioId: 'insp-002',
  timestamp: new Date(),
  clasificacionAnterior: 'PREMIUM',
  clasificacionNueva: 'STANDARD',
  motivo: 'Desgaste detectado en inspección',
  metadata: {
    profundidadActual: 8.5,
    inspeccionId: 'insp-2026-789',
  },
});
```

---

## Eventos de Inspección

### 10. INSPECCION.PRESSURE_READ 🔍

**Cuándo se dispara:** Al registrar una lectura de presión.

**Payload:**
```typescript
interface PressureReadPayload {
  neumaticoId: string;
  empresaId: string;
  usuarioId: string;
  timestamp: Date;
  presionActual: number;          // PSI
  presionRecomendada: number;     // PSI
  vehiculoId: string;
  posicionId: string;
  kilometrajeVehiculo: number;
}
```

**Observers que reaccionan:**
- ✅ `AlertObserver` - Alerta si presión < 90% recomendado
- ✅ `NeumaticoUpdateObserver` - Actualiza snapshot de neumático

**Ejemplo:**
```typescript
await EventBus.publish(InspeccionEvents.PRESSURE_READ, {
  neumaticoId: 'tire-222',
  empresaId: DEFAULT_TENANT_ID,
  usuarioId: 'insp-001',
  timestamp: new Date(),
  presionActual: 95,
  presionRecomendada: 110,  // 95/110 = 86% < 90% → ⚠️ ALERTA
  vehiculoId: 'truck-333',
  posicionId: 'FR',
  kilometrajeVehiculo: 60000,
});
```

**Alertas automáticas:**
- Si `presionActual < presionRecomendada * 0.9` → Alerta CRITICAL

---

### 11. INSPECCION.DEPTH_READ 📏

**Cuándo se dispara:** Al registrar una medición de profundidad.

**Payload:**
```typescript
interface DepthReadPayload {
  neumaticoId: string;
  empresaId: string;
  usuarioId: string;
  timestamp: Date;
  profundidadActual: number;      // mm
  profundidadMinima: number;      // mm (legal limit)
  vehiculoId: string;
  posicionId: string;
  kilometrajeVehiculo: number;
}
```

**Observers que reaccionan:**
- ✅ `AlertObserver` - Alerta si profundidad crítica
- ✅ `NeumaticoUpdateObserver` - Actualiza datos de neumático

**Ejemplo:**
```typescript
await EventBus.publish(InspeccionEvents.DEPTH_READ, {
  neumaticoId: 'tire-222',
  empresaId: DEFAULT_TENANT_ID,
  usuarioId: 'insp-001',
  timestamp: new Date(),
  profundidadActual: 2.5,
  profundidadMinima: 1.6,  // 2.5 < 4mm → ⚠️ WARNING
  vehiculoId: 'truck-333',
  posicionId: 'FR',
  kilometrajeVehiculo: 60000,
});
```

**Alertas automáticas:**
- Si `profundidadActual < 4mm` → Alerta WARNING
- Si `profundidadActual < profundidadMinima` → Alerta CRITICAL

---

## Eventos de Reencauche

### 12. REENCAUCHE.SENT 🚚

**Cuándo se dispara:** Al enviar un neumático a reencauchar.

**Payload:**
```typescript
interface TireSentToRetreadPayload {
  neumaticoId: string;
  empresaId: string;
  usuarioId: string;
  timestamp: Date;
  proveedorId: string;
  costoEstimado: number;
  fechaEnvio: Date;
  metadata: {
    ordenReencaucheId?: string;
    profundidadActual?: number;
  };
}
```

**Observers que reaccionan:**
- ✅ `CacheObserver` - Invalida caché de reencauche

**Ejemplo:**
```typescript
await EventBus.publish(ReencaucheEvents.SENT, {
  neumaticoId: 'tire-444',
  empresaId: DEFAULT_TENANT_ID,
  usuarioId: 'log-002',
  timestamp: new Date(),
  proveedorId: 'retread-pro',
  costoEstimado: 200.00,
  fechaEnvio: new Date('2026-01-29'),
  metadata: {
    ordenReencaucheId: 'RE-2026-012',
    profundidadActual: 3.5,
  },
});
```

---

### 13. REENCAUCHE.RETURNED ✅

**Cuándo se dispara:** Al recibir un neumático reencauchado.

**Payload:**
```typescript
interface TireRetreadReturnedPayload {
  neumaticoId: string;
  empresaId: string;
  usuarioId: string;
  timestamp: Date;
  proveedorId: string;
  costoFinal: number;
  fechaRetorno: Date;
  profundidadNueva: number;
  metadata: {
    ordenReencaucheId?: string;
    calidadAceptada?: boolean;
  };
}
```

**Observers que reaccionan:**
- ✅ `CacheObserver` - Invalida caché de reencauche

**Ejemplo:**
```typescript
await EventBus.publish(ReencaucheEvents.RETURNED, {
  neumaticoId: 'tire-444',
  empresaId: DEFAULT_TENANT_ID,
  usuarioId: 'log-002',
  timestamp: new Date(),
  proveedorId: 'retread-pro',
  costoFinal: 185.00,
  fechaRetorno: new Date('2026-02-10'),
  profundidadNueva: 16.5,
  metadata: {
    ordenReencaucheId: 'RE-2026-012',
    calidadAceptada: true,
  },
});
```

---

## Matriz de Observers

Tabla que muestra qué observers reaccionan a qué eventos:

| Evento | Audit | Notification | Analytics | Alert | Cache | Update |
|--------|-------|--------------|-----------|-------|-------|--------|
| **PURCHASED** | ✅ | - | ✅ | - | - | - |
| **MOUNTED** | ✅ | - | ✅ | - | - | - |
| **DISMOUNTED** | ✅ | ✅ | ✅ | - | - | - |
| **ROTATED** | ✅ | - | ✅ | - | - | - |
| **SCRAPPED** | ✅ | ✅ | ✅ | - | - | - |
| **REPAIR_STARTED** | ✅ | - | ✅ | - | - | - |
| **REPAIR_COMPLETED** | ✅ | - | ✅ | - | - | - |
| **TRANSFERRED** | ✅ | - | ✅ | - | - | - |
| **RECLASSIFIED** | ✅ | - | ✅ | - | - | - |
| **PRESSURE_READ** | - | - | - | ✅ | - | ✅ |
| **DEPTH_READ** | - | - | - | ✅ | - | ✅ |
| **SENT (Retread)** | - | - | - | - | ✅ | - |
| **RETURNED (Retread)** | - | - | - | - | ✅ | - |

**Leyenda:**
- ✅ = Observer reacciona a este evento
- `-` = Observer ignora este evento

---

## Convenciones de Nombres

### Patrón General
```
NAMESPACE.PAST_TENSE_ACTION
```

**Ejemplos:**
- ✅ `NEUMATICO.MOUNTED`
- ✅ `INSPECCION.PRESSURE_READ`
- ✅ `REENCAUCHE.SENT`

**Anti-ejemplos:**
- ❌ `MOUNT_TIRE` (no namespace, tiempo presente)
- ❌ `neumatico.mounted` (lowercase)
- ❌ `TIRE_INSTALLATION` (no español, nombre demasiado largo)

---

## Próximos Pasos

- Ver [Catálogo de Observers](./04_OBSERVERS_CATALOGO.md) para entender qué hace cada observer
- Ver [Guía de Desarrollo](./02_GUIA_DESARROLLO.md) para aprender a crear nuevos eventos
- Ver [Testing de Eventos](./05_TESTING_EVENTOS.md) para testear eventos y observers

---

**Última actualización:** 2026-01-29  
**Total de eventos:** 13 (11 neumáticos + 2 inspección + 2 reencauche)  
**Mantenido por:** Equipo de Arquitectura GesNeu
