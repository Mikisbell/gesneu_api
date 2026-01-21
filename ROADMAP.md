# 🚀 ROADMAP - GesNeu API

> **Stack Tecnológico**: Next.js 16 + TypeScript + Prisma 7 + PostgreSQL (Supabase)  
> **Última Actualización**: 2025-12-25  
> **Basado en**: Requerimientos de Sistema API Ges_Neu_Final.pdf v2.1

---

## 📊 Estado Actual

| Fase | Estado | Descripción |
|------|--------|-------------|
| **Fase 1** | ✅ 100% | CRUD, Auth, Eventos, Audit, RBAC |
| **Fase 2** | ✅ 100% | CPK, Desgaste, Comparativo |
| **Fase 3** | ✅ 100% | Alertas, Dashboard, Email Notif. |
| **Fase 4** | ✅ 100% | Políticas reencauchado |
| **Fase 5** | ✅ 100% | Reportes, CSV, Dashboard visual, Mapa Ejes |
| **Fase 6** | ✅ 100% | PWA + Inspecciones Manuales (Backend & Basic UI) |

---

## 🎯 Q1 2026 (Enero - Marzo)

### Prioridad Alta 🔴 (Funcionalidad Core)
| Tarea | Estado | Detalle | Est. |
|-------|--------|---------|-----|
| **Migración DB** | ✅ | Tabla `lecturas_presion` creada y sincronizada | ✅ |
| **Alertas & Webhooks** | ✅ | Alertas, Colas y Notificaciones ERP | ✅ |
| **Reportes PDF** | ✅ | Certificados de Operatividad y Inspección | ✅ Completado |

### Prioridad Media 🟡 (Mejoras UX)
| Tarea | Estado | Detalle | Est. |
|-------|--------|---------|-----|
| **Historial Presión UI** | ✅ | Gráfico de tendencia implementado (Recharts) | ✅ |
| **IoT Scalability** | 📉 | (Postergado) Solo entrada manual por ahora | Q3 2026 |

### Prioridad Media 🟡

| Tarea | Estado | Descripción | ETA |
|-------|--------|-------------|-----|
| **API IoT/TPMS** | ✅ | Endpoint para sensores (Implementado Fase 5) | Completado |

### Prioridad Descartada/Postergada 📉
| Tarea | Estado | Motivo |
|-------|--------|--------|
| **Reportes PDF** | ⏸️ | Cosmético. No crítico para operación. |
| **PWA Icons** | ✅ | Completado (aunque funcionalidad offline pendiente) |

### Prioridad Baja 🟢

| Tarea | Estado | Descripción | ETA |
|-------|--------|-------------|-----|
| **Multi-tenant** | 📋 | Soporte para múltiples empresas | Q2 2026 |
| **App Nativa** | 📋 | React Native wrapper si PWA no es suficiente | Q2 2026 |

---

## ✅ Fases Completadas (2025)

<details>
<summary>Ver historial completo</summary>

### Fase 1: Infraestructura Base
- [x] Next.js App Router + API Routes
- [x] Prisma ORM + Supabase PostgreSQL
- [x] NextAuth (JWT)
- [x] CRUD: Neumáticos, Vehículos, Almacenes, Catálogos
- [x] Sistema de Eventos (`EventoNeumatico`)
- [x] OpenAPI/Swagger auto-generado
- [x] Audit logging completo
- [x] RBAC dinámico en UI

### Fase 2: KPIs y Métricas
- [x] `GET /api/v1/reportes/cpk` - Costo por kilómetro
- [x] `GET /api/v1/reportes/desgaste` - Tasa de desgaste
- [x] `GET /api/v1/reportes/comparativo-marcas`

### Fase 3: Sistema de Alertas
- [x] Modelo `Alerta` con tipos y severidades
- [x] Triggers automáticos
- [x] Notificaciones Email (Resend API)

### Fase 4: Políticas de Seguridad
- [x] Campo `permite_reencauchado` en posiciones
- [x] Validación en montaje
- [x] Tests E2E de seguridad

### Fase 5: Dashboard y Reportes
- [x] Dashboard con Chart.js
- [x] Mapa Visual de Ejes
- [x] Exportación CSV

### Fase 6: PWA + Inspecciones (En Progreso)
- [x] PWA Infrastructure (manifest, service worker)
- [x] Offline fallback page
- [x] Install prompt component
- [x] API `POST /api/v1/inspecciones`
- [x] Modal de inspección manual
- [x] Migración DB para `lecturas_presion`
- [x] Alertas automáticas de presión

</details>

---

## 📝 Notas Técnicas

- **Versión**: 0.2.0 (Post-Auditoría + PWA)
- **Deploy**: Vercel + Supabase (us-west-2)
- **Repo**: github.com/Mikisbell/gesneu_api
- **Docs**: Ver `/docs/00_INDEX.md`

---

## 🔮 Visión Q2-Q4 2026

- **Q2**: Multi-tenant, integración con ERPs (SAP, Oracle)
- **Q3**: Machine Learning para predicción de vida útil
- **Q4**: Marketplace de proveedores de reencauche

*Estas son direcciones tentativas sujetas a validación con clientes.*

---

*Consultar `AGENT.md` para gobernanza de desarrollo.*
