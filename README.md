# 🚀 GesNeu API - Sistema de Gestión de Neumáticos

**Última actualización:** 2025-11-28 09:48 AM  
**Estado:** ✅ Listo para Deploy a Vercel  
**Tests:** 85/85 passing (100%)

Una API REST empresarial construida con **Next.js 14** y **TypeScript** para la gestión integral de neumáticos y vehículos de flota.

---

## 📊 Estado del Proyecto

![Tests](https://img.shields.io/badge/tests-85%2F85%20passing-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)
![Build](https://img.shields.io/badge/build-passing-brightgreen)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue)
![Next.js](https://img.shields.io/badge/Next.js-14.x-black)
![Prisma](https://img.shields.io/badge/Prisma-7.x-2D3748)

**Características:**

- ✅ 7 módulos completos (Neumáticos, Vehículos, Operaciones, Catálogos, Usuarios)
- ✅ Sistema RBAC con 4 roles y 40+ permisos granulares
- ✅ Documentación Swagger completa
- ✅ Audit logging para trazabilidad
- ✅ 85 tests de integración y unitarios
- ✅ Arquitectura en capas documentada

---

## 📦 Stack Tecnológico

| Categoría | Tecnología | Versión |
|-----------|------------|---------|
| **Framework** | Next.js | 14.2+ |
| **Lenguaje** | TypeScript | 5.x |
| **ORM** | Prisma | 7.0+ |
| **Base de Datos** | PostgreSQL (Supabase) | 15+ |
| **Autenticación** | NextAuth.js | 4.x |
| **Validación** | Zod | 3.x |
| **Testing** | Jest + Supertest | Latest |
| **Deploy** | Vercel | Latest |
| **Monitoring** | Sentry | Latest |

---

## 🏗️ Arquitectura

```
src/
├── app/
│   ├── api/v1/              # API Routes (Presentation Layer)
│   │   ├── neumaticos/      # Gestión de neumáticos
│   │   ├── vehiculos/       # Gestión de vehículos  
│   │   ├── operaciones/     # 7 tipos de operaciones
│   │   │   ├── montaje/
│   │   │   ├── desmontaje/
│   │   │   ├── rotacion/
│   │   │   ├── inspeccion/
│   │   │   ├── reparacion/
│   │   │   ├── reencauche/
│   │   │   └── desecho/
│   │   ├── catalogos/       # Almacenes, Proveedores
│   │   └── usuarios/        # CRUD Usuarios (Admin)
│   └── docs/                # Swagger UI
├── lib/
│   ├── auth/                # Authentication & Authorization
│   ├── services/            # Business Logic Layer
│   ├── validators/          # Zod Schemas (DTOs)
│   ├── utils/               # Helpers & Constants
│   └── prisma.ts            # Database Client
└── __tests__/               # Integration & Unit Tests
    ├── integration/
    └── lib/
```

**Ver documentación completa:** [ARCHITECTURE.md](./ARCHITECTURE.md)

---

## 🚀 Inicio Rápido

### Prerequisites

- Node.js 18+
- PostgreSQL (o cuenta en [Supabase](https://supabase.com))
- Git

### Instalación Local

```bash
# 1. Clonar repositorio
git clone https://github.com/Mikisbell/gesneu_api.git
cd gesneu_api

# 2. Instalar dependencias
npm install

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de Supabase

# 4. Generar Prisma Client
npx prisma generate

# 5. Ejecutar migraciones (opcional - DB ya está configurada)
npx prisma db push

# 6. Iniciar en desarrollo
npm run dev
```

La API estará disponible en: **<http://localhost:3005>**

### Deploy a Producción (Vercel)

Ver guía completa en: **[VERCEL_SETUP.md](./VERCEL_SETUP.md)** (30 minutos)

```bash
# Opción rápida:
# 1. Ve a https://vercel.com/new
# 2. Import Mikisbell/gesneu_api
# 3. Configura variables de entorno (ver VERCEL_SETUP.md)
# 4. Click "Deploy" ✨
```

---

## 📡 API Endpoints

### Documentación Interactiva

```
http://localhost:3005/api/docs
```

**Swagger UI completo** con todos los endpoints, schemas y ejemplos.

### Módulos Principales

#### Neumáticos

```
GET    /api/v1/neumaticos       # Listar (paginado)
POST   /api/v1/neumaticos       # Crear
GET    /api/v1/neumaticos/:id   # Ver detalle
PUT    /api/v1/neumaticos/:id   # Actualizar
DELETE /api/v1/neumaticos/:id   # Soft delete
```

#### Vehículos

```
GET    /api/v1/vehiculos        # Listar
POST   /api/v1/vehiculos        # Crear
GET    /api/v1/vehiculos/:id    # Ver detalle
PUT    /api/v1/vehiculos/:id    # Actualizar
DELETE /api/v1/vehiculos/:id    # Soft delete
```

#### Operaciones

```
POST   /api/v1/operaciones/montaje
POST   /api/v1/operaciones/desmontaje
POST   /api/v1/operaciones/rotacion
POST   /api/v1/operaciones/inspeccion
POST   /api/v1/operaciones/reparacion/entrada
POST   /api/v1/operaciones/reparacion/salida
POST   /api/v1/operaciones/reencauche/entrada
POST   /api/v1/operaciones/reencauche/salida
POST   /api/v1/operaciones/desecho
```

#### Catálogos

```
GET    /api/v1/catalogos/almacenes
POST   /api/v1/catalogos/almacenes
GET    /api/v1/catalogos/proveedores
POST   /api/v1/catalogos/proveedores
```

#### Usuarios (Admin only)

```
GET    /api/v1/usuarios         # Listar
POST   /api/v1/usuarios         # Crear
GET    /api/v1/usuarios/:id     # Ver detalle
PUT    /api/v1/usuarios/:id     # Actualizar
DELETE /api/v1/usuarios/:id     # Soft delete
```

---

## 🔐 Autenticación y Seguridad

### Sistema RBAC

**4 Roles:**

- `ADMINISTRADOR` - Acceso total
- `GESTOR` - Gestión operativa
- `OPERADOR` - Operaciones básicas
- `CONSULTOR` - Solo lectura

**40+ Permisos Granulares:**

- Por módulo: `read`, `create`, `update`, `delete`
- Ejemplo: `NEUMATICOS_CREATE`, `VEHICULOS_UPDATE`

### Autenticación (NextAuth.js)

```typescript
// Login
POST /api/auth/signin
{
  "username": "admin",
  "password": "tu_contraseña"
}

// Response
{
  "user": {
    "id": "...",
    "username": "admin",
    "rol": "ADMINISTRADOR"
  },
  "token": "eyJhbGci..."
}
```

**Todos los endpoints** requieren autenticación y validación de permisos.

---

## 🧪 Testing

```bash
# Ejecutar todos los tests
npm test

# Tests de integración solamente
npm run test:integration

# Con coverage
npm run test:coverage
```

**Resultado esperado:**

```
Test Suites: 7 passed, 7 total
Tests:       85 passed, 85 total
```

**Incluye:**

- 19 tests de autorización
- 13 tests de validadores
- 53 tests de integración (endpoints)

---

## 📚 Documentación

| Documento | Descripción |
|-----------|-------------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Arquitectura completa del sistema |
| [VERCEL_SETUP.md](./VERCEL_SETUP.md) | Guía de deploy a Vercel (30 min) |
| [.env.example](./.env.example) | Variables de entorno requeridas |
| `/api/docs` | Swagger UI interactiva |

---

## 🛠️ Desarrollo

### Scripts Disponibles

```bash
npm run dev          # Desarrollo (puerto 3005)
npm run build        # Build de producción
npm run start        # Iniciar producción
npm run lint         # Linter
npm test             # Ejecutar tests
```

### Estructura de Branches

- `main` - Producción (protegido)
- `staging` - Testing (opcional)
- `feature/*` - Nuevas características

---

## 🚢 Deploy

### Vercel (Recomendado)

**Auto-deploy configurado:**

- Push a `main` → Deploy automático
- PR creado → Preview deploy
- Rollback con 1 click

**Ver guía completa:** [VERCEL_SETUP.md](./VERCEL_SETUP.md)

---

## 🤝 Contribuir

Ver [CONTRIBUTING.md](./CONTRIBUTING.md) (si existe) o contactar al equipo.

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
