# 🏗️ Arquitectura - GesNeu API

> **Última actualización**: Enero 2026

## Stack Tecnológico

| Capa | Tecnología |
|------|------------|
| **Runtime** | Node.js 20+ |
| **Framework** | Next.js 16 (App Router) |
| **Lenguaje** | TypeScript 5 (strict) |
| **ORM** | Prisma 7 |
| **Base de Datos** | PostgreSQL 15 (Supabase) |
| **Autenticación** | NextAuth.js 5 (JWT) |
| **Validación** | Zod |
| **Emails** | Resend API |
| **Deploy** | Vercel |

---

## Diagrama de Arquitectura por Capas

```mermaid
graph TD
    A[Cliente Browser/PWA] -->|HTTPS| B[Next.js 16]
    
    subgraph "Presentation Layer"
        B --> C[API Routes /api/v1/*]
        B --> D[Middleware Auth]
    end
    
    subgraph "Business Logic Layer"
        C --> E[NeumaticoService]
        C --> F[DashboardService]
        C --> G[InspeccionService]
        C --> H[AlertasService]
        C --> R[ReencaucheService]
    end
    
    subgraph "Event-Driven Layer 🔔"
        E --> EB[EventBus Core]
        G --> EB
        R --> EB
        EB --> O1[AuditObserver]
        EB --> O2[NotificationObserver]
        EB --> O3[AnalyticsObserver]
        EB --> O4[AlertObserver]
        EB --> O5[CacheObserver]
        EB --> O6[NeumaticoUpdateObserver]
    end
    
    subgraph "Data Access Layer"
        E --> I[Prisma ORM]
        F --> I
        G --> I
        H --> I
        R --> I
        O1 --> I
        O2 --> I
        O4 --> I
        O6 --> I
    end
    
    subgraph "Database Layer"
        I --> J[(Supabase PostgreSQL)]
    end
    
    style A fill:#e1f5ff
    style B fill:#fff4e1
    style EB fill:#ffe1e1
    style I fill:#e1ffe1
    style J fill:#f5e1ff
```

---

## Complejidad del Dominio

### Entidades por Módulo (37 tablas)

```
CATÁLOGOS (4 tablas):
├── proveedores (TipoProveedorEnum: 5 valores)
├── almacenes (con códigos únicos)
├── motivos_desecho (con evidencia requerida)
└── parametros_inventario (6 tipos)

VEHÍCULOS (5 tablas):
├── vehiculos (con odómetro)
├── tipos_vehiculo (maestro)
├── configuraciones_eje (por tipo)
├── posiciones_neumatico (4 lados)
└── registros_odometro (histórico)

NEUMÁTICOS (6 tablas):
├── neumaticos (entidad principal)
├── modelos_neumatico (especificaciones)
├── fabricantes_neumatico (maestro)
├── especificaciones_desgaste (técnico)
├── parametros_rendimiento (IA/ML futuro)
└── modelos_posiciones_permitidas (restricciones)

OPERACIONES (8 tablas):
├── eventos_neumaticos (11 tipos de evento)
├── historial_estados (trazabilidad)
├── lecturas_presion (inspecciones)
├── inventario_neumaticos (stock)
├── movimientos_inventario (traslados)
├── garantias_neumaticos (gestión)
├── alertas (sistema proactivo)
└── bitacora_operaciones (auditoría)

SISTEMA (14 tablas):
├── usuarios + roles + permisos (RBAC)
├── auditoria_log (trazabilidad)
├── parametros_sistema (config)
└── [otras de soporte]
```

### Enums del Dominio (15)

| Enum | Valores | Uso |
|------|---------|-----|
| `EstadoNeumaticoEnum` | 6 | Ciclo de vida |
| `TipoEventoNeumaticoEnum` | 11 | Operaciones |
| `EstadoOperacionEnum` | 5 | Workflow |
| `TipoProveedorEnum` | 5 | Catálogo |
| `LadoVehiculoEnum` | 4 | Posiciones |
| `TipoEjeEnum` | 6 | Configuración |
| `NivelSeveridadEnum` | 3 | Alertas |
| `EstadoAlertaEnum` | 3 | Gestión alertas |

---

## Estructura del Proyecto

```
src/
├── app/
│   ├── api/v1/
│   │   ├── neumaticos/      # CRUD + eventos
│   │   ├── vehiculos/       # CRUD + montaje
│   │   ├── catalogos/       # Proveedores, almacenes
│   │   ├── operaciones/     # Montaje, desecho, rotación
│   │   ├── dashboard/       # KPIs, reportes
│   │   ├── alertas/         # Gestión alertas
│   │   ├── inspecciones/    # Lecturas presión/profundidad
│   │   ├── reencauche/      # Envío/retorno
│   │   └── webhooks/        # Integración ERP
│   ├── (pages)/             # UI Dashboard
│   └── layout.tsx
│
├── lib/
│   ├── auth/                # NextAuth config
│   │   ├── config.ts
│   │   └── authorization.ts
│   ├── events/              # 🔔 Event-Driven System
│   │   ├── core.ts          # EventBus singleton
│   │   ├── neumatico.events.ts  # 11 eventos de neumáticos
│   │   ├── inspeccion.events.ts # Eventos de inspección
│   │   ├── reencauche.events.ts # Eventos de reencauche
│   │   └── registry.ts      # Registro de observers
│   ├── observers/           # 🔔 6 Observers
│   │   ├── audit.observer.ts
│   │   ├── notification.observer.ts
│   │   ├── analytics.observer.ts
│   │   ├── alerta.observer.ts
│   │   ├── cache.observer.ts
│   │   └── neumatico-update.observer.ts
│   ├── services/            # Business Logic
│   │   ├── neumatico.service.ts
│   │   ├── evento-neumatico.service.ts  # Emite eventos
│   │   ├── dashboard.service.ts
│   │   ├── inspeccion.service.ts
│   │   ├── reencauche.service.ts
│   │   └── webhook.service.ts
│   ├── validators/          # Zod schemas
│   └── utils/
│       └── api-response.ts
│
├── components/              # React UI
└── types/                   # TypeScript types
```

---

## Patrones de Diseño

### API Routes
- Validación con Zod en entrada
- Auth con `requireAuth()` de authorization.ts
- Respuestas estandarizadas con `ApiResponseHelper`

### Servicios
- Un servicio por dominio (NeumaticoService, DashboardService)
- Transacciones Prisma para operaciones complejas
- Sin dependencia directa de HTTP Request/Response

### Eventos como Núcleo
- Todo cambio de estado pasa por `EventoNeumatico`
- Audit trail automático (`creado_por`, timestamps)
- Trazabilidad completa

### Event-Driven Architecture (Patrón Observer) 🔔

**Implementado en:** Enero 2026

GesNeu usa una arquitectura orientada a eventos para desacoplar la lógica de negocio de las side-effects (cache, notificaciones, analytics).

#### EventBus (Core)
Singleton basado en Node.js `EventEmitter` que proporciona:
- **Publicación de eventos**: `EventBus.publish<PayloadType>(eventName, payload)`
- **Suscripción**: `EventBus.subscribe<PayloadType>(eventName, handler)`
- **Type-safe**: Payloads fuertemente tipados con TypeScript

#### Eventos Definidos (11 tipos)

```typescript
// src/lib/events/neumatico.events.ts
NEUMATICO.PURCHASED        // Compra
NEUMATICO.MOUNTED          // Instalación
NEUMATICO.DISMOUNTED       // Desmontaje
NEUMATICO.ROTATED          // Rotación
NEUMATICO.SCRAPPED         // Desecho
NEUMATICO.REPAIR_STARTED   // Entrada a taller
NEUMATICO.REPAIR_COMPLETED // Salida de taller
NEUMATICO.RETREAD_SENT     // Envío a reencauche
NEUMATICO.RETREAD_RETURNED // Retorno reencauchado
```

#### Observers Activos (6 totales)

| Observer | Responsabilidad | Eventos |
|----------|----------------|---------|
| **AuditObserver** | Logging universal de eventos | Todos (9) |
| **NotificationObserver** | Alertas automáticas (alto costo, desgaste prematuro) | SCRAPPED, REPAIR_COMPLETED, DISMOUNTED |
| **AnalyticsObserver** | Invalidación de caché, KPIs en tiempo real | MOUNTED, DISMOUNTED, ROTATED, SCRAPPED |
| **AlertObserver** | Alertas de inspección (presión/profundidad) | PRESSURE_READ, DEPTH_READ |
| **CacheObserver** | Invalidación de caché (inspecciones/reencauche) | RETREAD_SENT, RETREAD_RETURNED |
| **NeumaticoUpdateObserver** | Sincronización de snapshots | PRESSURE_READ, DEPTH_READ |

#### Flujo de Eventos

```mermaid
sequenceDiagram
    participant API as API Route
    participant Svc as EventoNeumaticoService
    participant DB as PostgreSQL
    participant Bus as EventBus
    participant Obs as Observers

    API->>Svc: registrarEvento(DESECHO)
    Svc->>DB: $transaction { ... }
    DB-->>Svc: Success
    Svc->>Bus: publish(SCRAPPED, payload)
    Bus->>Obs: notify(event)
    Obs->>DB: create alerta (async)
    Obs->>Obs: invalidate cache
    Obs->>Obs: console.log(audit)
    Svc-->>API: Response
```

#### Ventajas del Patrón

- **Desacoplamiento**: Observers independientes, fácil agregar/eliminar
- **Extensibilidad**: Nuevas features sin tocar código existente
- **Auditoría**: Trazabilidad completa de ciclo de vida
- **Performance**: Invalidación selectiva de caché
- **Tolerancia a fallos**: Errores en observers no rompen transacciones

---

## Decisiones Arquitectónicas (ADR)

### ADR-001: Next.js sobre Express
**Decisión**: Usar Next.js App Router en lugar de Express tradicional.  
**Razón**: Unificar frontend y API en un solo deploy, aprovechar SSR para dashboard.

### ADR-002: Prisma sobre SQL crudo
**Decisión**: Usar Prisma ORM exclusivamente.  
**Razón**: Type safety, migraciones versionadas, compatibilidad con Supabase.

### ADR-003: Eventos como núcleo
**Decisión**: Todo cambio de estado de neumático genera un `EventoNeumatico`.  
**Razón**: Trazabilidad completa, auditoría, posibilidad de replay.

### ADR-004: Database-First
**Decisión**: El esquema PostgreSQL es la fuente de verdad.  
**Razón**: 37 tablas ya optimizadas, `prisma db pull` para sincronizar.

### ADR-005: Sistema Interno Single-Tenant
**Decisión**: Operar exclusivamente como **Single-Tenant** (sistema interno para una sola empresa).  
**Razón**: GesNeu es una aplicación **privada** para una empresa de transporte específica, **no es un SaaS** multi-cliente.  
**Implementación**: Todas las operaciones usan `DEFAULT_TENANT_ID` (`00000000-0000-0000-0000-000000000000`) automáticamente.  
**Nota Técnica**: Aunque el schema incluye `empresa_id` en las tablas por diseño histórico de la base de datos, el sistema **no opera ni operará** como multi-tenant.

### ADR-006: Event-Driven Architecture (Observer Pattern)
**Decisión**: Implementar patrón Observer para todas las operaciones de neumáticos, inspecciones y reencauche.
**Razón**: Desacoplar side-effects (cache, notificaciones, analytics) de la lógica transaccional core.
**Beneficios**: 
- Extensibilidad sin modificar código existente
- Auditoría completa de eventos
- Performance mejorado con invalidación selectiva de caché
- Tolerancia a fallos (observers nunca rompen transacciones)
**Fecha**: Enero 2026

---

## Métricas de Performance

| Métrica | Objetivo | Crítico |
|---------|----------|---------|
| API Response (p95) | <200ms | >500ms |
| DB Query (p95) | <50ms | >200ms |
| Memory | <512MB | >1GB |
| Throughput | 1000 req/min | <100 req/min |

---

*Ver también: `04_BASE_DATOS.md` para schema detallado.*
