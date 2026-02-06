# 🚀 GesNeu API - Sistema de Gestión de Neumáticos

**Estado:** ✅ Listo para Producción
**CI/CD:** Activo (GitHub Actions + Vercel)

Una **aplicación web empresarial** construida con **Next.js**, **TypeScript** y **Prisma** para la gestión inteligente de flotas.

---

## 📊 Estado del Proyecto

![E2E Tests](https://img.shields.io/badge/playwright-passing-brightgreen)
![CI Status](https://github.com/Mikisbell/gesneu_api/actions/workflows/ci.yml/badge.svg)
![Type Check](https://img.shields.io/badge/typescript-strict-blue)

**Novedades Fase 2 (Performance & Robustez):**
- ✅ **Monitoreo Interno**: Logging persistente en DB (sin costos externos).
- ✅ **Auditoría UI**: Panel de control para logs técnicos en `/dashboard/admin/logs`.
- ✅ **Automatización**: CI/CD Pipelines para Tests y Linting.
- ✅ **Performance**: Validación N+1 superada (< 300ms/query).

---

[... Secciones de Stack y Arquitectura se mantienen ...]

## 🛠️ Desarrollo Local

```bash
# 1. Setup
git clone [repo]
npm install
cp .env.example .env

# 2. Database
npx prisma generate
npx prisma db push

# 3. Server
npm run dev
```

### 🚨 Troubleshooting Común

**Error: "Prisma Client not initialized" o "Unknown model"**
- Solución: Ejecuta `npx prisma generate` cada vez que cambies el `schema.prisma` o actualices dependencias.

**Error: "Too many connections" en Tests**
- Causa: Serverless + Tests paralelos saturan el pool.
- Solución: Usamos `DIRECT_URL` para migraciones y un pool limitado en `src/lib/prisma.ts`. Asegúrate de no correr tests E2E y de estrés simultáneamente en local contra la misma DB dev.

**Tests E2E fallando en Login**
- Verifica que el usuario `admin` exista en tu DB local. Puedes crearlo manualmente o usar los scripts de seed.

---

## 📡 Monitoreo y Auditoría

El sistema incluye un **Logger Interno** integrado.

```typescript
import { logger } from '@/lib/logger';

// Registra eventos críticos que persistirán en DB
await logger.error('Fallo crítico', error, { context: 'pago' });
```

Accede a los logs visualmente en: **Panel Admin > Auditoría > Logs del Sistema**.

---

## 🤝 Contribuir

Consulte [CONTRIBUTING.md](./CONTRIBUTING.md) para guías sobre:
- Estándares de Commits
- Configuración de Husky (Hooks)
- Ejecución de Tests E2E

---

## 📝 Licencia

Privado - © 2024-2025 Mikisbell

---

## 📞 Soporte

- **Issues:** [GitHub Issues](https://github.com/Mikisbell/gesneu_api/issues)
- **Docs:** `VERCEL_SETUP.md`, `ARCHITECTURE.md`
- **Swagger:** `/api/docs`

---

**Desarrollado con ❤️ usando Next.js, TypeScript y Prisma**
