# 🧪 Testing de Eventos - Event-Driven Architecture

> **Audiencia:** Developers, QA Engineers  
> **Última actualización:** Enero 2026  
> **Nivel:** Guía práctica

---

## Tabla de Contenidos

1. [Estrategias de Testing](#estrategias-de-testing)
2. [Unit Tests de Observers](#unit-tests-de-observers)
3. [Integration Tests de Flujos](#integration-tests-de-flujos)
4. [Mocking del EventBus](#mocking-del-eventbus)
5. [Testing en CI/CD](#testing-en-cicd)
6. [Coverage Goals](#coverage-goals)

---

## Estrategias de Testing

### Pirámide de Testing para Eventos

```
         /\
        /  \     E2E Tests (5%)
       /----\    - Flujos completos con DB real
      /      \   
     /--------\  Integration Tests (25%)
    /          \ - Service + EventBus + Observers
   /------------\ 
  /______________\ Unit Tests (70%)
                   - Observers aislados
                   - Event payloads
                   - Mappers
```

---

## Unit Tests de Observers

### Setup Básico

**Archivo:** `src/lib/observers/__tests__/audit.observer.test.ts`

```typescript
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { AuditObserver } from '../audit.observer';
import { EventBus } from '@/lib/events/core';
import { NeumaticoEvents, TireMountedPayload } from '@/lib/events/neumatico.events';

// Mock de console.log para verificar output
const consoleLogSpy = vi.spyOn(console, 'log');

describe('AuditObserver', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Registrar observer
    AuditObserver.init();
  });

  afterEach(() => {
    // Limpiar suscripciones
    EventBus.removeAllListeners();
  });

  it('should log MOUNTED events', async () => {
    // Arrange
    const payload: TireMountedPayload = {
      neumaticoId: 'test-123',
      empresaId: 'empresa-456',
      usuarioId: 'user-789',
      timestamp: new Date('2026-01-29'),
      vehiculoId: 'vehicle-001',
      posicionId: 'FL',
      kilometrajeVehiculo: 50000,
      metadata: {},
    };

    // Act
    await EventBus.publish(NeumaticoEvents.MOUNTED, payload);

    // Assert
    expect(consoleLogSpy).toHaveBeenCalledWith(
      expect.stringContaining('[AUDIT] NEUMATICO.MOUNTED'),
      expect.objectContaining({
        neumaticoId: 'test-123',
        vehiculoId: 'vehicle-001',
      })
    );
  });

  it('should handle all 9 tire events', async () => {
    // Arrange
    const events = [
      NeumaticoEvents.PURCHASED,
      NeumaticoEvents.MOUNTED,
      NeumaticoEvents.DISMOUNTED,
      NeumaticoEvents.ROTATED,
      NeumaticoEvents.SCRAPPED,
      NeumaticoEvents.REPAIR_STARTED,
      NeumaticoEvents.REPAIR_COMPLETED,
      NeumaticoEvents.TRANSFERRED,
      NeumaticoEvents.RECLASSIFIED,
    ];

    // Act & Assert
    for (const eventName of events) {
      await EventBus.publish(eventName, { neumaticoId: 'test' });
      expect(consoleLogSpy).toHaveBeenLastCalledWith(
        expect.stringContaining(eventName),
        expect.any(Object)
      );
    }
  });
});
```

---

### Testing Observer con DB (NotificationObserver)

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { NotificationObserver } from '../notification.observer';
import { EventBus } from '@/lib/events/core';
import { NeumaticoEvents, TireScrappedPayload } from '@/lib/events/neumatico.events';
import { prisma } from '@/lib/db';

// Mock de Prisma
vi.mock('@/lib/db', () => ({
  prisma: {
    alerta: {
      create: vi.fn(),
    },
  },
}));

describe('NotificationObserver', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    NotificationObserver.init();
  });

  it('should create alert for high-value scrap', async () => {
    // Arrange
    const payload: TireScrappedPayload = {
      neumaticoId: 'expensive-tire',
      empresaId: 'empresa-123',
      usuarioId: 'user-456',
      timestamp: new Date(),
      motivoTexto: 'Daño irreparable',
      profundidadFinal: 5.0,
      metadata: {
        kmTotales: 80000,
        costoTotal: 6000,  // > $5,000 → Alerta!
        vidaAlcanzada: 1,
      },
    };

    // Act
    await EventBus.publish(NeumaticoEvents.SCRAPPED, payload);

    // Assert
    expect(prisma.alerta.create).toHaveBeenCalledWith({
      data: expect.objectContaining({
        tipo: 'DESGASTE_IRREGULAR',
        severidad: 'WARNING',
        mensaje: expect.stringContaining('$6000'),
        neumatico_id: 'expensive-tire',
      }),
    });
  });

  it('should create alert for premature wear', async () => {
    // Arrange
    const payload: TireScrappedPayload = {
      neumaticoId: 'early-failure',
      empresaId: 'empresa-123',
      usuarioId: 'user-456',
      timestamp: new Date(),
      motivoTexto: 'Desgaste prematuro',
      profundidadFinal: 3.0,
      metadata: {
        kmTotales: 15000,  // < 20,000 km → Alerta!
        costoTotal: 450,
        vidaAlcanzada: 1,
      },
    };

    // Act
    await EventBus.publish(NeumaticoEvents.SCRAPPED, payload);

    // Assert
    expect(prisma.alerta.create).toHaveBeenCalledWith({
      data: expect.objectContaining({
        tipo: 'DESGASTE_IRREGULAR',
        severidad: 'CRITICAL',
        mensaje: expect.stringContaining('15000km'),
        neumatico_id: 'early-failure',
      }),
    });
  });

  it('should not throw if DB fails', async () => {
    // Arrange
    prisma.alerta.create.mockRejectedValueOnce(new Error('DB Connection failed'));

    const payload: TireScrappedPayload = {
      neumaticoId: 'test',
      empresaId: 'empresa-123',
      usuarioId: 'user-456',
      timestamp: new Date(),
      motivoTexto: 'Test',
      profundidadFinal: 5.0,
      metadata: { kmTotales: 10000, costoTotal: 6000, vidaAlcanzada: 1 },
    };

    // Act & Assert - No debe hacer throw
    await expect(async () => {
      await EventBus.publish(NeumaticoEvents.SCRAPPED, payload);
    }).resolves.not.toThrow();
  });
});
```

---

## Integration Tests de Flujos

### Setup

**Archivo:** `src/lib/services/__tests__/evento-neumatico-integration.test.ts`

```typescript
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { EventoNeumaticoService } from '../evento-neumatico.service';
import { EventBus } from '@/lib/events/core';
import { NeumaticoEvents } from '@/lib/events/neumatico.events';
import { prisma } from '@/lib/db';
import { registerObservers } from '@/lib/events/registry';
import { TipoEventoEnum } from '@prisma/client';

describe('EventoNeumaticoService Integration', () => {
  let testNeumatico: any;
  let testUsuario: any;

  beforeAll(async () => {
    // Registrar todos los observers
    registerObservers();

    // Crear datos de prueba
    testNeumatico = await prisma.neumatico.create({
      data: {
        numero_serie: 'TEST-INT-001',
        estado: 'DISPONIBLE',
        empresa_id: '00000000-0000-0000-0000-000000000000',
        // ... otros campos
      },
    });

    testUsuario = await prisma.usuario.create({
      data: {
        username: 'test-user',
        // ... otros campos
      },
    });
  });

  afterAll(async () => {
    // Limpiar datos de prueba
    await prisma.neumatico.delete({ where: { id: testNeumatico.id } });
    await prisma.usuario.delete({ where: { id: testUsuario.id } });
    await prisma.$disconnect();
  });

  it('should emit MOUNTED event after registering montaje', async () => {
    // Arrange
    const service = new EventoNeumaticoService();
    const publishSpy = vi.spyOn(EventBus, 'publish');

    // Act
    await service.registrarEvento({
      tipo: TipoEventoEnum.MONTAJE,
      neumatico_id: testNeumatico.id,
      vehiculo_id: 'test-vehicle',
      posicion_id: 'FL',
      kilometraje_vehiculo: 50000,
    }, testUsuario.id);

    // Assert
    expect(publishSpy).toHaveBeenCalledWith(
      NeumaticoEvents.MOUNTED,
      expect.objectContaining({
        neumaticoId: testNeumatico.id,
        vehiculoId: 'test-vehicle',
        posicionId: 'FL',
      })
    );

    publishSpy.mockRestore();
  });

  it('should create alert when tire is scrapped prematurely', async () => {
    // Arrange
    const service = new EventoNeumaticoService();

    // Act - Desechar neumático con bajo kilometraje
    await service.registrarEvento({
      tipo: TipoEventoEnum.DESECHO,
      neumatico_id: testNeumatico.id,
      motivo_texto: 'Test premature scrap',
      profundidad_final: 5.0,
      metadata: {
        kmTotales: 10000,  // < 20,000 km
        costoTotal: 450,
        vidaAlcanzada: 1,
      },
    }, testUsuario.id);

    // Assert - Verificar que se creó la alerta
    const alertas = await prisma.alerta.findMany({
      where: {
        neumatico_id: testNeumatico.id,
        tipo: 'DESGASTE_IRREGULAR',
      },
    });

    expect(alertas.length).toBeGreaterThan(0);
    expect(alertas[0].severidad).toBe('CRITICAL');
    expect(alertas[0].mensaje).toContain('10000km');

    // Cleanup
    await prisma.alerta.deleteMany({ where: { neumatico_id: testNeumatico.id } });
  });
});
```

---

## Mocking del EventBus

### Mock para Unit Tests

```typescript
// __mocks__/@/lib/events/core.ts
import { vi } from 'vitest';

export const EventBus = {
  publish: vi.fn(),
  subscribe: vi.fn(),
  removeAllListeners: vi.fn(),
};
```

**Uso:**
```typescript
import { EventBus } from '@/lib/events/core';

vi.mock('@/lib/events/core');

describe('MyService', () => {
  it('should publish event', async () => {
    await myService.doSomething();
    
    expect(EventBus.publish).toHaveBeenCalledWith(
      'NEUMATICO.MOUNTED',
      expect.objectContaining({ neumaticoId: 'test' })
    );
  });
});
```

---

### Spy Pattern (sin mock completo)

```typescript
import { EventBus } from '@/lib/events/core';

describe('Integration Test', () => {
  it('should emit event', async () => {
    // Spy en método real (no mock)
    const publishSpy = vi.spyOn(EventBus, 'publish');

    await service.action();

    expect(publishSpy).toHaveBeenCalled();

    // Restaurar
    publishSpy.mockRestore();
  });
});
```

---

## Testing en CI/CD

### Vitest Config

**Archivo:** `vitest.config.ts`

```typescript
import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    setupFiles: ['./tests/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: [
        'src/lib/observers/**/*.ts',
        'src/lib/events/**/*.ts',
        'src/lib/services/evento-neumatico.service.ts',
      ],
      exclude: [
        '**/*.test.ts',
        '**/*.spec.ts',
        '**/node_modules/**',
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 75,
        statements: 80,
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

---

### GitHub Actions Workflow

**Archivo:** `.github/workflows/test.yml`

```yaml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: gesneu_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run Prisma migrations
        run: npx prisma migrate deploy
        env:
          DATABASE_URL: postgresql://postgres:test_password@localhost:5432/gesneu_test
      
      - name: Run unit tests
        run: npm test -- --coverage
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/coverage-final.json
```

---

## Coverage Goals

### Current Coverage (Enero 2026)

| Módulo | Lines | Functions | Branches | Statements |
|--------|-------|-----------|----------|------------|
| **Events Core** | 95% | 100% | 90% | 95% |
| **Observers** | 70% | 75% | 65% | 70% |
| **Services** | 65% | 70% | 60% | 65% |

### Target Coverage (Q2 2026)

| Módulo | Lines | Functions | Branches | Statements |
|--------|-------|-----------|----------|------------|
| **Events Core** | 100% | 100% | 95% | 100% |
| **Observers** | 85% | 90% | 80% | 85% |
| **Services** | 80% | 85% | 75% | 80% |

---

## Best Practices

### ✅ DO

```typescript
// Usar factories para payloads
function createMountedPayload(overrides = {}): TireMountedPayload {
  return {
    neumaticoId: 'test-123',
    empresaId: 'empresa-456',
    usuarioId: 'user-789',
    timestamp: new Date(),
    vehiculoId: 'vehicle-001',
    posicionId: 'FL',
    kilometrajeVehiculo: 50000,
    metadata: {},
    ...overrides,
  };
}

// Uso
const payload = createMountedPayload({ vehiculoId: 'custom-vehicle' });
```

### ✅ DO

```typescript
// Testear edge cases
it('should handle missing metadata gracefully', async () => {
  const payload = createPayload({ metadata: undefined });
  await expect(EventBus.publish(EVENT, payload)).resolves.not.toThrow();
});
```

### ❌ DON'T

```typescript
// No hardcodear payloads en cada test
it('test 1', async () => {
  await EventBus.publish(EVENT, {
    neumaticoId: 'test',
    empresaId: 'test',
    usuarioId: 'test',
    timestamp: new Date(),
    // ... 10 líneas más
  });
});

it('test 2', async () => {
  // Copiar-pegar el mismo payload ❌
  await EventBus.publish(EVENT, { /* ... */ });
});
```

---

## Próximos Pasos

- Ver [Monitoreo y Operaciones](./06_MONITOREO_OPERACIONES.md) para debugging en producción
- Ver [Catálogo de Observers](./04_OBSERVERS_CATALOGO.md) para entender qué testear
- Ver [Guía de Desarrollo](./02_GUIA_DESARROLLO.md) para crear nuevos tests

---

**Última actualización:** 2026-01-29  
**Framework:** Vitest 1.x  
**Mantenido por:** Equipo de Arquitectura GesNeu
