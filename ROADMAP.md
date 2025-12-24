# 🚀 ROADMAP - GesNeu API

> **Stack Tecnológico**: Next.js 16 + TypeScript + Prisma 7 + PostgreSQL (Supabase)  
> **Última Actualización**: 2025-12-24  
> **Basado en**: Requerimientos de Sistema API Ges_Neu_Final.pdf v2.1

---

## 📊 Estado Actual (Post-Auditoría)

## 📊 Estado Actual (Post-Auditoría)

| Fase | Estado | Completado | Pendiente |
|------|--------|------------|-----------|
| **Fase 1** | ✅ 100% | CRUD, Auth, Eventos, Audit, RBAC | - |
| **Fase 2** | ✅ 100% | CPK, Desgaste, Comparativo | - |
| **Fase 3** | ✅ 100% | Alertas, Dashboard, Email Notif. | - |
| **Fase 4** | ✅ 100% | Políticas reencauchado | - |
| **Fase 5** | ✅ 100% | Reportes, CSV, Dashboard visual, Mapa Ejes | - |
| **Fase 6** | ⏳ 0% | - | IoT/TPMS, Webhooks |

### Tests
- **Passing**: 28+ tests
- **Gaps**: -

---

## 🎯 Fases Completadas

### ✅ Fase 1: Infraestructura Base
- [x] Next.js App Router + API Routes
- [x] Prisma ORM + Supabase PostgreSQL
- [x] NextAuth (JWT)
- [x] CRUD: Neumáticos, Vehículos, Almacenes, Catálogos
- [x] Sistema de Eventos (`EventoNeumatico`)
- [x] OpenAPI/Swagger auto-generado
- [x] **Audit logging completo** (`updated_by`, `deleted_by`)
- [x] **RBAC dinámico en UI** (PermissionGate)

### ✅ Fase 2: KPIs y Métricas
- [x] `GET /api/v1/reportes/cpk` - Costo por kilómetro
- [x] `GET /api/v1/reportes/desgaste` - Tasa de desgaste
- [x] `GET /api/v1/reportes/comparativo-marcas` - Ranking CPK por marca
- [x] 8 tests unitarios

### ✅ Fase 3: Sistema de Alertas
- [x] Modelo `Alerta` con tipos y severidades
- [x] Trigger: Profundidad < 4mm → CRITICAL
- [x] Trigger: Reencauches >= máximo → WARNING
- [x] `GET /api/v1/alertas` con filtros
- [x] `POST /api/v1/alertas/generar`
- [x] **Notificaciones Email** (Resend API)
- [x] 4 tests unitarios

### ✅ Fase 4: Políticas de Seguridad
- [x] Campo `permite_reencauchado` en `PosicionNeumatico`
- [x] Validación en `/operaciones/montaje`
- [x] `GET/PATCH /api/v1/configuracion/posiciones/:id/politica`
- [x] 7 tests E2E de montaje
- [x] **Test de seguridad**: reglas de reencauchado verificadas

### ✅ Fase 5: Dashboard y Reportes
- [x] `GET /api/v1/dashboard/inventario`
- [x] `GET /api/v1/dashboard/rendimiento`
- [x] `GET /api/v1/dashboard/desechos`
- [x] `GET /api/v1/dashboard/exportar?tipo=X` (CSV)
- [x] **UI Dashboard** en `/panel` con Chart.js
- [x] **Mapa Visual de Ejes** con glassmorphism
- [x] 3 tests unitarios

---

## ⏳ Fase 6: Integraciones (Futuro)

| Prioridad | Tarea | Descripción |
|-----------|-------|-------------|
| 🟡 Media | **API para TPMS** | Recibir datos de sensores de presión/temperatura |
| 🟢 Baja | **Webhooks** | Notificar a ERP sobre eventos críticos |
| 🔴 Alta | **App Móvil** | PWA para operarios en campo (offline first) |

---

## 🔴 Gaps Identificados (ver TECHNICAL_DEBT.md)

*Todos los items de deuda técnica inicial han sido resueltos.* ✅

---

## ✅ Criterios de Éxito (Actualizado)

- [x] CPK calculable para cualquier neumático
- [x] Alertas activas + Email para profundidad mínima
- [x] Políticas de posición funcionando y testeadas
- [x] Al menos 3 reportes operativos disponibles
- [x] Documentación OpenAPI completa
- [x] Dashboard visual funcional
- [x] Audit logging completo
- [x] RBAC dinámico en frontend
- [x] Tests para reglas de seguridad (100% cobertura)
- [x] Mapa visual de ejes premium

---

## 📝 Notas

1. **Stack Actual**: Next.js 16, Prisma 7, TypeScript 5
2. **Deploy**: Vercel + Supabase (us-west-2)
3. **Repositorio**: github.com/Mikisbell/gesneu_api
