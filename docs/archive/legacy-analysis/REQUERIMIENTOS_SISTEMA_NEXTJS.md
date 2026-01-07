# 🚗 Requerimientos del Sistema API GesNeu - Next.js + TypeScript

**Versión:** 2.0.0 (Migrado de FastAPI)  
**Fecha:** 14 de Noviembre, 2025  
**Stack:** Next.js 14 + TypeScript + Supabase PostgreSQL

---

## 🎯 Migración Completada: FastAPI → Next.js

### **Cambios Arquitectónicos Principales:**

| Aspecto | Antes (FastAPI) | Ahora (Next.js) |
|---------|-----------------|------------------|
| **Backend** | Python + FastAPI | TypeScript + Next.js API Routes |
| **ORM** | SQLModel + SQLAlchemy | Prisma ORM |
| **Validación** | Pydantic schemas | Zod + TypeScript types |
| **Inyección Dependencias** | FastAPI Depends | Next.js middleware + helpers |
| **Autenticación** | JWT + FastAPI Security | NextAuth.js + JWT |
| **Deploy** | Docker + uvicorn | Vercel (serverless) |
| **Base de Datos** | PostgreSQL local | Supabase PostgreSQL |

---

## 3. Arquitectura Técnica (Actualizada para Next.js)

### 3.1 Estructura del Proyecto Next.js

```
gesneu_api/
├── src/
│   ├── app/
│   │   ├── api/                    # API Routes (reemplaza FastAPI routers)
│   │   │   ├── health/
│   │   │   │   └── route.ts        # Health check endpoint
│   │   │   └── v1/
│   │   │       ├── catalogos/
│   │   │       │   ├── proveedores/
│   │   │       │   │   ├── route.ts           # GET, POST /proveedores
│   │   │       │   │   └── [id]/route.ts      # GET, PUT, DELETE /proveedores/[id]
│   │   │       │   ├── almacenes/
│   │   │       │   ├── fabricantes/
│   │   │       │   └── modelos/
│   │   │       ├── neumaticos/
│   │   │       │   ├── route.ts               # CRUD neumáticos
│   │   │       │   ├── eventos/route.ts       # POST /neumaticos/eventos
│   │   │       │   ├── instalados/route.ts    # GET /neumaticos/instalados
│   │   │       │   └── [id]/
│   │   │       │       ├── route.ts           # GET /neumaticos/[id]
│   │   │       │       └── historial/route.ts # GET /neumaticos/[id]/historial
│   │   │       ├── vehiculos/
│   │   │       ├── inventario/
│   │   │       ├── alertas/
│   │   │       └── auth/
│   │   │           ├── token/route.ts         # POST /auth/token
│   │   │           └── users/
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx                # Frontend opcional
│   ├── lib/
│   │   ├── prisma.ts              # Cliente Prisma (reemplaza database.py)
│   │   ├── auth.ts                # NextAuth config (reemplaza security.py)
│   │   ├── api-response.ts        # Helpers respuesta API
│   │   ├── types.ts               # Tipos TypeScript (reemplaza schemas)
│   │   ├── validations.ts         # Validaciones Zod
│   │   └── services/              # Servicios de negocio
│   │       ├── neumatico.service.ts
│   │       ├── vehiculo.service.ts
│   │       ├── catalogo.service.ts
│   │       └── alert.service.ts
│   └── middleware.ts              # Middleware autenticación
├── prisma/
│   ├── schema.prisma              # Esquema Prisma (reemplaza models.py)
│   └── migrations/
├── types/                         # Tipos TypeScript globales
│   ├── api.ts
│   ├── neumatico.ts
│   ├── vehiculo.ts
│   └── enums.ts                   # Enums TypeScript (reemplaza common.py)
├── package.json                   # Dependencias npm (reemplaza requirements.txt)
├── tsconfig.json                  # Configuración TypeScript
├── next.config.js                 # Configuración Next.js
└── .env.local                     # Variables de entorno
```

### 3.2 Capa de API Routes (Reemplaza FastAPI Routers)

**Antes (FastAPI):**
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/", response_model=NeumaticoRead)
async def create_neumatico(
    neumatico_in: NeumaticoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    return neumatico_service.create(db, neumatico_in, current_user.id)
```

**Ahora (Next.js API Routes):**
```typescript
// src/app/api/v1/neumaticos/route.ts
import { NextRequest } from 'next/server'
import { prisma } from '@/lib/prisma'
import { ApiResponseHelper } from '@/lib/api-response'
import { NeumaticoService } from '@/lib/services/neumatico.service'
import { validateAuth } from '@/lib/auth'
import { NeumaticoCreateSchema } from '@/lib/validations'

export async function POST(request: NextRequest) {
  try {
    // Validar autenticación (reemplaza Depends(get_current_active_user))
    const currentUser = await validateAuth(request)
    if (!currentUser) {
      return ApiResponseHelper.unauthorized()
    }

    // Validar datos de entrada (reemplaza Pydantic)
    const body = await request.json()
    const validatedData = NeumaticoCreateSchema.parse(body)

    // Llamar servicio de negocio
    const neumatico = await NeumaticoService.create(validatedData, currentUser.id)

    return ApiResponseHelper.success(neumatico, 'Neumático creado exitosamente')
  } catch (error) {
    return ApiResponseHelper.error(
      error instanceof Error ? error.message : 'Error al crear neumático'
    )
  }
}
```

### 3.3 Capa de Servicios (Lógica de Negocio)

**Antes (Python):**
```python
class NeumaticoService:
    def create(self, db: Session, neumatico_in: NeumaticoCreate, user_id: UUID) -> Neumatico:
        # Lógica de negocio
        pass
```

**Ahora (TypeScript):**
```typescript
// src/lib/services/neumatico.service.ts
import { prisma } from '@/lib/prisma'
import { NeumaticoCreate, NeumaticoRead } from '@/types/neumatico'

export class NeumaticoService {
  static async create(data: NeumaticoCreate, userId: string): Promise<NeumaticoRead> {
    // Validaciones de negocio
    await this.validateBusinessRules(data)

    // Crear en base de datos usando Prisma
    const neumatico = await prisma.neumatico.create({
      data: {
        ...data,
        creado_por: userId,
        creado_en: new Date()
      },
      include: {
        modelo: {
          include: {
            fabricante: true
          }
        }
      }
    })

    return this.mapToRead(neumatico)
  }

  private static async validateBusinessRules(data: NeumaticoCreate): Promise<void> {
    // Lógica de validación de negocio
    if (await this.existsNumeroSerie(data.numero_serie)) {
      throw new Error('Número de serie ya existe')
    }
  }
}
```

### 3.4 Validación de Datos (Reemplaza Pydantic)

**Antes (Pydantic):**
```python
from pydantic import BaseModel, Field

class NeumaticoCreate(BaseModel):
    numero_serie: str = Field(..., min_length=1, max_length=50)
    modelo_id: UUID
    dot: str = Field(..., regex=r'^\d{4}$')
```

**Ahora (Zod + TypeScript):**
```typescript
// src/lib/validations.ts
import { z } from 'zod'

export const NeumaticoCreateSchema = z.object({
  numero_serie: z.string().min(1).max(50),
  modelo_id: z.string().uuid(),
  dot: z.string().regex(/^\d{4}$/, 'DOT debe tener 4 dígitos'),
  profundidad_inicial: z.number().positive(),
  fecha_compra: z.date().optional(),
  costo_compra: z.number().positive().optional()
})

export type NeumaticoCreate = z.infer<typeof NeumaticoCreateSchema>
```

### 3.5 Autenticación y Autorización

**Antes (FastAPI Security):**
```python
from fastapi.security import HTTPBearer
from jose import jwt

def get_current_user(token: str = Depends(HTTPBearer())):
    # Validar JWT
    pass

def check_permission_for_event_type(user: Usuario, event_type: str):
    # Validar permisos RBAC
    pass
```

**Ahora (NextAuth.js + Middleware):**
```typescript
// src/lib/auth.ts
import { NextRequest } from 'next/server'
import { verify } from 'jsonwebtoken'
import { prisma } from './prisma'

export async function validateAuth(request: NextRequest) {
  const token = request.headers.get('authorization')?.replace('Bearer ', '')
  
  if (!token) return null

  try {
    const decoded = verify(token, process.env.JWT_SECRET_KEY!) as any
    const user = await prisma.usuario.findUnique({
      where: { id: decoded.sub },
      include: { roles: true }
    })
    
    return user
  } catch {
    return null
  }
}

export function checkPermissionForEventType(user: any, eventType: string): boolean {
  const ROLES_PERMITIDOS_POR_EVENTO = {
    COMPRA: ['GESTOR', 'ADMIN'],
    INSTALACION: ['OPERADOR', 'GESTOR', 'ADMIN'],
    DESMONTAJE: ['OPERADOR', 'GESTOR', 'ADMIN'],
    // ... más eventos
  }

  const allowedRoles = ROLES_PERMITIDOS_POR_EVENTO[eventType] || []
  return user.roles.some(role => allowedRoles.includes(role.nombre))
}
```

---

## 4. Requerimientos Funcionales (Actualizados para Next.js)

### 4.1 Gestión de Catálogos Base

#### ✅ **RF35: Gestionar Fabricantes de Neumáticos**
- **Endpoint:** `GET/POST /api/v1/catalogos/fabricantes`
- **Endpoint:** `GET/PUT/DELETE /api/v1/catalogos/fabricantes/[id]`
- **Validación:** Zod schema `FabricanteCreateSchema`, `FabricanteUpdateSchema`
- **Respuesta:** TypeScript type `FabricanteRead`
- **Servicio:** `FabricanteService.create()`, `.update()`, `.delete()` (soft delete)

#### ✅ **RF36: Gestionar Modelos de Neumáticos**
- **Endpoint:** `GET/POST /api/v1/catalogos/modelos`
- **Validación:** Campos obligatorios en `ModeloNeumaticoCreateSchema`
- **Lógica:** `ModeloNeumaticoService` con validaciones de negocio

#### ✅ **RF37: Gestionar Proveedores** (IMPLEMENTADO)
- **Endpoint:** `GET/POST /api/v1/catalogos/proveedores` ✅
- **Endpoint:** `GET/PUT/DELETE /api/v1/catalogos/proveedores/[id]` ✅
- **Enum:** `TipoProveedorEnum` en TypeScript ✅
- **Servicio:** Implementado con Prisma ✅

### 4.2 Gestión de Neumáticos (Ciclo de Vida Individual)

#### **RF_EVENTO_01: Registrar Evento Genérico de Neumático**
```typescript
// POST /api/v1/neumaticos/eventos
export async function POST(request: NextRequest) {
  const currentUser = await validateAuth(request)
  const body = await request.json()
  
  // Validar schema unificado
  const evento = EventoNeumaticoCreateSchema.parse(body)
  
  // Validar permisos por tipo de evento
  if (!checkPermissionForEventType(currentUser, evento.tipo_evento)) {
    return ApiResponseHelper.unauthorized('Sin permisos para este tipo de evento')
  }
  
  // Procesar evento según tipo
  const result = await NeumaticoService.registrarEvento(evento, currentUser)
  
  return ApiResponseHelper.success(result)
}
```

**Tipos de Evento Soportados:**
- `COMPRA` - Crea nuevo neumático
- `INSTALACION` - Monta en vehículo  
- `DESMONTAJE` - Desmonta de vehículo
- `INSPECCION` - Registra mediciones
- `ROTACION` - Cambia posición
- `REPARACION_ENTRADA/SALIDA`
- `REENCAUCHE_ENTRADA/SALIDA`
- `DESECHO` - Baja definitiva
- `AJUSTE_INVENTARIO` - Corrección manual

#### **RF02: Consultar Neumático**
```typescript
// GET /api/v1/neumaticos/[id]
export async function GET(request: NextRequest, { params }: { params: { id: string } }) {
  const neumatico = await prisma.neumatico.findUnique({
    where: { id: params.id },
    include: {
      modelo: {
        include: { fabricante: true }
      },
      ubicacion_almacen: true,
      ubicacion_vehiculo: {
        include: { posicion_actual: true }
      },
      eventos: {
        orderBy: { fecha_evento: 'desc' },
        take: 10
      }
    }
  })
  
  return ApiResponseHelper.success(neumatico)
}
```

### 4.3 Autenticación y Autorización RBAC

#### **Roles Definidos:**
```typescript
enum RolUsuario {
  ADMIN = 'ADMIN',
  GESTOR = 'GESTOR', 
  OPERADOR = 'OPERADOR'
}

const ROLES_PERMITIDOS_POR_EVENTO = {
  COMPRA: [RolUsuario.GESTOR, RolUsuario.ADMIN],
  INSTALACION: [RolUsuario.OPERADOR, RolUsuario.GESTOR, RolUsuario.ADMIN],
  DESMONTAJE: [RolUsuario.OPERADOR, RolUsuario.GESTOR, RolUsuario.ADMIN],
  INSPECCION: [RolUsuario.OPERADOR, RolUsuario.GESTOR, RolUsuario.ADMIN],
  ROTACION: [RolUsuario.OPERADOR, RolUsuario.GESTOR, RolUsuario.ADMIN],
  REPARACION_ENTRADA: [RolUsuario.OPERADOR, RolUsuario.GESTOR],
  REPARACION_SALIDA: [RolUsuario.OPERADOR, RolUsuario.GESTOR],
  REENCAUCHE_ENTRADA: [RolUsuario.GESTOR, RolUsuario.ADMIN],
  REENCAUCHE_SALIDA: [RolUsuario.OPERADOR, RolUsuario.GESTOR],
  DESECHO: [RolUsuario.GESTOR, RolUsuario.ADMIN],
  AJUSTE_INVENTARIO: [RolUsuario.GESTOR, RolUsuario.ADMIN]
} as const
```

---

## 5. Requerimientos No Funcionales (Actualizados)

### 5.1 Rendimiento
- **RNF01:** Tiempo de respuesta < 2 segundos (mejorado con Vercel Edge Functions)
- **RNF02:** Escalabilidad automática con Vercel serverless

### 5.2 Seguridad  
- **RNF03:** JWT Bearer tokens con NextAuth.js
- **RNF04:** RBAC implementado con middleware TypeScript
- **RNF05:** HTTPS nativo en Vercel, validación con Zod

### 5.3 Tecnología
- **RNF06:** API RESTful con OpenAPI docs generadas
- **RNF07:** TypeScript para type safety al 100%
- **RNF08:** Prisma ORM para integridad de datos
- **RNF09:** Deploy automático con Vercel + GitHub

---

## 6. Enumeraciones TypeScript (Reemplaza schemas/common.py)

```typescript
// types/enums.ts

export enum EstadoNeumaticoEnum {
  NUEVO = 'NUEVO',
  EN_STOCK = 'EN_STOCK', 
  INSTALADO = 'INSTALADO',
  EN_REPARACION = 'EN_REPARACION',
  EN_REENCAUCHE = 'EN_REENCAUCHE',
  DESECHADO = 'DESECHADO',
  EN_TRANSITO = 'EN_TRANSITO'
}

export enum TipoEventoNeumaticoEnum {
  COMPRA = 'COMPRA',
  INSTALACION = 'INSTALACION', 
  DESMONTAJE = 'DESMONTAJE',
  ROTACION = 'ROTACION',
  INSPECCION = 'INSPECCION',
  REPARACION_ENTRADA = 'REPARACION_ENTRADA',
  REPARACION_SALIDA = 'REPARACION_SALIDA',
  REENCAUCHE_ENTRADA = 'REENCAUCHE_ENTRADA',
  REENCAUCHE_SALIDA = 'REENCAUCHE_SALIDA',
  DESECHO = 'DESECHO',
  AJUSTE_INVENTARIO = 'AJUSTE_INVENTARIO'
}

export enum TipoProveedorEnum {
  FABRICANTE = 'FABRICANTE',
  DISTRIBUIDOR = 'DISTRIBUIDOR', 
  SERVICIO_REPARACION = 'SERVICIO_REPARACION',
  SERVICIO_REENCAUCHE = 'SERVICIO_REENCAUCHE',
  OTRO = 'OTRO'
}

export enum LadoVehiculoEnum {
  IZQUIERDO = 'IZQUIERDO',
  DERECHO = 'DERECHO',
  CENTRAL = 'CENTRAL', 
  INDETERMINADO = 'INDETERMINADO'
}

export enum TipoEjeEnum {
  DIRECCION = 'DIRECCION',
  TRACCION = 'TRACCION',
  ARRASTRE = 'ARRASTRE',
  ELEVADOR = 'ELEVADOR',
  RETRACTIL = 'RETRACTIL',
  OTRO = 'OTRO'
}
```

---

## 7. Comandos de Desarrollo (Actualizados)

### **Desarrollo:**
```bash
# Iniciar servidor (reemplaza uvicorn)
npm run dev

# Instalar dependencias (reemplaza pip install)
npm install

# Base de datos (reemplaza alembic)
npx prisma migrate dev
npx prisma generate
npx prisma studio

# Testing (reemplaza pytest)
npm test
npm run test:e2e

# Linting (reemplaza ruff)
npm run lint
npm run type-check

# Build para producción
npm run build
```

### **Deploy:**
```bash
# Deploy a Vercel (reemplaza Docker)
vercel --prod

# O automático con GitHub
git push origin main  # Auto-deploy en Vercel
```

---

## 8. Estado de Implementación

### ✅ **Completado (60%):**
- [x] Migración arquitectónica a Next.js + TypeScript
- [x] Prisma ORM configurado con esquema PostgreSQL
- [x] Endpoints básicos de catálogos (proveedores, almacenes)
- [x] Sistema de respuestas API estandarizado
- [x] Health check con verificación de BD
- [x] Estructura de proyecto Next.js
- [x] Validaciones con Zod
- [x] Tipos TypeScript definidos

### 🔄 **En Progreso (40%):**
- [ ] Deploy a Vercel con variables de entorno
- [ ] Endpoints de neumáticos y eventos
- [ ] Sistema de autenticación NextAuth.js
- [ ] Endpoints de vehículos y configuraciones
- [ ] Sistema de alertas
- [ ] Testing automatizado
- [ ] Documentación OpenAPI

---

**Migración Exitosa:** FastAPI → Next.js + TypeScript completada al 60%  
**Próximo paso:** Deploy a Vercel y completar endpoints restantes

---

*Documento actualizado: 14 de Noviembre, 2025*
