# 📝 Changelog - GesNeu API

Historial de cambios importantes del proyecto.

---

## [Unreleased]

### Added
- Documentación consolidada en `/docs`
- `AGENT.md` - Gobernanza AI
- Script `npm run docs:audit`
- ROADMAP Q1 2026

---

## [0.2.0] - 2025-12-25

### Added
- PWA Infrastructure (manifest.json, service worker)
- Página offline fallback
- Componente InstallPrompt
- API `POST /api/v1/inspecciones`
- Modal de inspección manual
- Modelo `LecturaPresion` para historial de presiones

### Fixed
- `requireAuth()` corregido en endpoints
- Middleware ahora protege todas las rutas `/api/*`
- `creado_por` poblado en compras de neumáticos
- `vida_actual` incrementado en salida de reencauche

### Security
- Removido fallback de `NEXTAUTH_SECRET`
- Validación Zod en endpoint de neumáticos

---

## [0.1.0] - 2025-12-22

### Added
- Infraestructura base Next.js 16 + Prisma 7
- CRUD completo de neumáticos, vehículos, catálogos
- Sistema de eventos (`EventoNeumatico`)
- Autenticación NextAuth con JWT
- RBAC con roles ADMIN, GESTOR, OPERADOR
- Dashboard con Chart.js
- Mapa visual de ejes
- Sistema de alertas con email (Resend)
- Reportes CPK, desgaste, comparativo
- Tests de integración (28+)

---

*Formato basado en [Keep a Changelog](https://keepachangelog.com/)*
