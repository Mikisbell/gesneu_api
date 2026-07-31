# 🚀 ROADMAP — GesNeu API

> **Stack**: Next.js 16 + TypeScript + Prisma 7 + PostgreSQL (Supabase)
> **Última actualización**: 2026-04-10
> **Documento complementario**: [`docs/00_PRD.md`](./docs/00_PRD.md) (qué hace el sistema y por qué)
> **Naturaleza de este documento**: planning temporal — el QUÉ está en el PRD, el CÓMO está en la arquitectura, el **CUÁNDO** está acá.

---

## 📊 Estado Actual

| Fase | Estado | Descripción |
|------|--------|-------------|
| **Fase 1** | ✅ 100% | CRUD core, Auth, Eventos, Audit, RBAC |
| **Fase 2** | ✅ 100% | KPIs: CPK, Desgaste, Comparativo |
| **Fase 3** | ✅ 100% | Alertas, Dashboard, Email Notifications |
| **Fase 4** | ✅ 100% | Políticas de reencauchado |
| **Fase 5** | ✅ 100% | Reportes, CSV, Dashboard visual, Mapa Ejes |
| **Fase 6** | ✅ 100% | PWA + Inspecciones Manuales |
| **Fase 6A** | ✅ 100% | Historial de posiciones, Matriz semáforo |
| **Fase 6B** | ✅ 100% | Inspecciones digitalizadas, Alertas post-inspección, Predicción de vida útil, Frecuencia adaptativa |
| **Fase 6C** | ✅ 100% | TCO, Benchmarking, Scoring, Forecast |
| **Event-Driven Architecture** | ✅ 100% | EventBus + 6 Observers + 13 Events |

---

## 🎯 Q2 2026 (Abril - Junio) — EN CURSO

### 🔴 Alta Prioridad — Deuda Técnica Crítica

| Tarea | Estado | Detalle | Impacto |
|-------|--------|---------|---------|
| **Bloquear `/admin/roles/*` endpoints** | ✅ Completada | Protegido con `DYNAMIC_RBAC_ENABLED=false` y verificado con 12 tests en `admin-guardrails.test.ts` | 🛡️ Seguridad |
| **Esconder `/admin/tenants` con feature flag** | ✅ Completada | Protegido con `MULTI_TENANT_ENABLED=false` y verificado en `admin-guardrails.test.ts` | 🛡️ Seguridad multi-tenant |
| **Consolidar baseline de migraciones** | 📋 Planificada | Hay drift entre `schema.prisma` y `prisma/migrations/`. Crear baseline consolidado para poder volver a usar `migrate dev` sin riesgo de reset | 🛠️ Mantenibilidad |
| **Pulir Certificado PDF (beta → GA)** | ✅ 100% | Folio secuencial, evaluación real, re-descarga desde snapshot (`GET /api/v1/reportes/certificado/folio/[folio]`) y suite `certificado.test.ts` | 📄 Certificación |

### 🟡 Media Prioridad — Saneamiento y Consolidación

| Tarea | Estado | Detalle |
|-------|--------|---------|
| **Consolidar enums de Postgres** | 📋 Planificada | Eliminar 9 valores deprecados de `EstadoNeumaticoEnum` y 6 de `TipoEventoNeumaticoEnum`. Requiere validar 0 uso en producción durante 1 mes previo |
| **Arreglar errores pre-existentes en `design-patterns.ts`** | 📋 Planificada | 3 errores de template literal mal cerrado detectados por `tsc` |
| **Refactorizar mock legacy `mockSessions.consultor`** | 📋 Planificada | Migrar 5 archivos de tests a un mock read-only explícito |
| **Tests de integración nuevos servicios** | 🔄 Parcialmente | Cobertura ≥ 80% en `certificado.service.ts` (completada) y `forecast.service.ts` |

### 🟢 Baja Prioridad — Mejoras

| Tarea | Estado | Detalle |
|-------|--------|---------|
| **UI de listado `/dashboard/certificados`** | 📋 Planificada | Vista con filtros por fecha, vehículo, estado. Re-descarga desde snapshot |
| **Endpoint GET `/certificado/{folio}`** | ✅ Completada | Endpoint `GET /api/v1/reportes/certificado/folio/[folio]` implementado y testeado |
| **Configurabilidad de `OPERATIVIDAD_THRESHOLDS`** | 💡 Idea | Mover a `ParametroSistema` por empresa |

---

## ✅ Entregas recientes (2026 Q1)

<details>
<summary>Ver fases completadas y cambios recientes</summary>

### 2026-04-10 — Saneamiento estructural (3 commits)

- **`fix(reportes)`**: canonicalizar filtros a `INSTALADO` y `EN_STOCK`. 3 endpoints productivos devolvían datasets vacíos silenciosamente por filtrar por valores huérfanos del enum.
- **`refactor(rbac)`**: canonicalizar `ADMIN` y eliminar rol `CONSULTOR` fantasma. Sprawl de naming eliminado en 11 archivos.
- **`feat(certificado)`**: refactor profesional de Certificado de Operatividad. Reemplaza MVP con folio aleatorio por sistema con folio secuencial único, evaluación real APTO/CONDICIONAL/NO_APTO, snapshot inmutable y filtro `empresa_id`.

### Fase 1: Infraestructura Base
- Next.js App Router + API Routes
- Prisma ORM + Supabase PostgreSQL
- NextAuth v5 (JWT)
- CRUD: Neumáticos, Vehículos, Almacenes, Catálogos
- Sistema de Eventos (`EventoNeumatico`)
- OpenAPI/Swagger auto-generado
- Audit logging completo
- RBAC dinámico en UI

### Fase 2: KPIs y Métricas
- `GET /api/v1/reportes/cpk` — Costo por kilómetro
- `GET /api/v1/reportes/desgaste` — Tasa de desgaste
- `GET /api/v1/reportes/comparativo-marcas`

### Fase 3: Sistema de Alertas
- Modelo `Alerta` con tipos y severidades
- Triggers automáticos
- Notificaciones Email (Resend API)

### Fase 4: Políticas de Seguridad
- Campo `permite_reencauchado` en posiciones
- Validación en montaje
- Tests E2E de seguridad

### Fase 5: Dashboard y Reportes
- Dashboard con Chart.js
- Mapa Visual de Ejes
- Exportación CSV
- Endpoint IoT/TPMS (ingesta de sensores)
- Reportes PDF: Certificado de Operatividad (base, refactorizado en 2026-04-10)

### Fase 6: PWA + Inspecciones
- PWA Infrastructure (manifest, service worker)
- Offline fallback page
- Install prompt component
- API `POST /api/v1/inspecciones`
- Modal de inspección manual
- Migración DB para `lecturas_presion`
- Alertas automáticas de presión
- Historial Presión UI con gráficos (Recharts)

### Fase 6A (2026 Q1)
- Historial de Instalaciones por Posición
- Matriz Semáforo por Medida

### Fase 6B (2026 Q1)
- Inspecciones Digitalizadas
- Alertas Post-Inspección Automáticas
- Predicción de Vida Útil
- Frecuencia de Inspección Adaptativa

### Fase 6C (2026 Q1)
- TCO (Total Cost of Ownership)
- Benchmarking
- Scoring
- Forecast de compras

### Event-Driven Architecture (2026 Q1)
- EventBus core + 6 Observers (Audit, Notification, Analytics, Alert, Cache, NeumaticoUpdate)
- 13 Event types
- Integración con sistema de webhooks
- Documentación completa en [`docs/events/`](./docs/events/)

</details>

---

## 🔮 Visión Q3-Q4 2026 (tentativa, sin compromiso)

> ⚠️ **Esta sección es exploratoria**. Las fechas y features pueden cambiar, postergarse o descartarse. Ver PRD sección 9 para más contexto.

### Q3 2026
- **Activación multi-tenant**: gestión de múltiples empresas desde una instancia
- **Integración con ERP del cliente** (por definir)
- **Machine Learning** para predicción de vida útil con datos históricos
- **IoT Scalability**: escalar ingesta TPMS si hay volumen significativo

### Q4 2026
- **Optimización de rutas** de rotación basada en patrones históricos
- **App nativa** (React Native wrapper) si la PWA no cubre operadores

### 2027+
- Marketplace interno de intercambio de neumáticos entre sedes
- Integración directa con proveedores de reencauche

---

## 🔗 Enlaces útiles

- **Documentación completa**: [`docs/00_INDEX.md`](./docs/00_INDEX.md)
- **PRD (qué hace el sistema)**: [`docs/00_PRD.md`](./docs/00_PRD.md)
- **Arquitectura**: [`docs/01_ARQUITECTURA.md`](./docs/01_ARQUITECTURA.md)
- **Eventos**: [`docs/events/07_ROADMAP_EVENTOS.md`](./docs/events/07_ROADMAP_EVENTOS.md)
- **Gobernanza de desarrollo**: [`AGENT.md`](./AGENT.md)

---

## 📝 Notas

- **Versión actual**: 0.3.0 (Post-Saneamiento Estructural 2026-04-10)
- **Deploy**: Vercel + Supabase (us-west-2)
- **Repositorio**: github.com/Mikisbell/gesneu_api
- **Modelo de tenancy**: Single-tenant operativo (multi-tenant ready en schema, no activado)
