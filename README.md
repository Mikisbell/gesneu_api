# 🚀 GesNeu API - Sistema de Gestión de Neumáticos

Una API REST moderna construida con **Next.js 16** y **TypeScript** para la gestión integral de neumáticos y vehículos de flota, con capacidades de Inteligencia Artificial para predicción de vida útil.

## 📦 Stack Tecnológico

- **Framework:** Next.js 16.0.5 (React 19)
- **Lenguaje:** TypeScript
- **ORM:** Prisma 7.0.1
- **Base de Datos:** PostgreSQL (Supabase)
- **Autenticación:** NextAuth.js v5
- **Deploy:** Vercel
- **Build Tool:** Turbopack

## 🏗️ Arquitectura

```
src/
├── app/
│   ├── api/v1/              # API Routes
│   │   ├── catalogos/       # Catálogos (Proveedores, Almacenes)
│   │   ├── vehiculos/       # Gestión de vehículos
│   │   └── neumaticos/      # Gestión de neumáticos
│   └── auth/                # Autenticación
├── lib/
│   ├── repositories/        # Data access layer
│   ├── services/            # Business logic
│   └── utils/               # Utilidades
└── types/                   # TypeScript types
```

## 🚀 Inicio Rápido

### Prerequisitos

- Node.js 18+
- PostgreSQL (o cuenta en Supabase)

### Instalación

```bash
# Clonar repositorio
git clone https://github.com/Mikisbell/gesneu_api.git
cd gesneu_api

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env.local
# Editar .env.local con tus credenciales

# Generar Prisma Client
npx prisma generate

# Ejecutar migraciones
npx prisma migrate dev

# Iniciar desarrollo
npm run dev
```

## 📡 API Endpoints

### Health Check

```
GET /api/health
```

### Catálogos

```
GET    /api/v1/catalogos/proveedores
POST   /api/v1/catalogos/proveedores
GET    /api/v1/catalogos/proveedores/[id]
PUT    /api/v1/catalogos/proveedores/[id]
DELETE /api/v1/catalogos/proveedores/[id]

GET    /api/v1/catalogos/almacenes
POST   /api/v1/catalogos/almacenes
GET    /api/v1/catalogos/almacenes/[id]
PUT    /api/v1/catalogos/almacenes/[id]
DELETE /api/v1/catalogos/almacenes/[id]
```

### Vehículos

```
GET    /api/v1/vehiculos
POST   /api/v1/vehiculos
GET    /api/v1/vehiculos/[id]
PUT    /api/v1/vehiculos/[id]
DELETE /api/v1/vehiculos/[id]
```

### Neumáticos

```
GET    /api/v1/neumaticos
POST   /api/v1/neumaticos
GET    /api/v1/neumaticos/[id]
PUT    /api/v1/neumaticos/[id]
DELETE /api/v1/neumaticos/[id]
```

## 🔐 Autenticación

La API usa NextAuth.js v5 con JWT tokens. Para autenticarte:

```typescript
POST /api/auth/signin
{
  "username": "tu_usuario",
  "password": "tu_contraseña"
}
```

## 🧪 Testing

```bash
# Ejecutar tests de API
bash test-api.sh
```

## 📚 Documentación

- [Plan de Migración](./PLAN_MIGRACION_NEXTJS.md)
- [Requerimientos del Sistema](./REQUERIMIENTOS_SISTEMA_NEXTJS.md)
- [Análisis Arquitectónico](./PARTE_1_ANALISIS_ARQUITECTONICO.md)

## 📝 Licencia

Privado - © 2024 Mikisbell
