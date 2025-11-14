# PARTE 2: ESPECIFICACIÓN TÉCNICA DETALLADA
## Prisma Schema + API Routes + Middleware

**Fecha:** 14 de Noviembre, 2025  
**Versión:** 1.0  
**Dependencias:** PARTE 1 completada

---

## 🗄️ PRISMA SCHEMA COMPLETO

### **1. Configuración Base**
```prisma
// prisma/schema.prisma
generator client {
  provider = "prisma-client-js"
  output   = "../src/generated/prisma"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}
```

### **2. Enums Críticos (15 identificados)**
```prisma
// Estados y tipos principales
enum EstadoNeumaticoEnum {
  EN_STOCK
  INSTALADO
  EN_REPARACION
  EN_REENCAUCHE
  DESECHADO
  EN_TRANSITO
  @@map("estado_neumatico_enum")
}

enum TipoEventoNeumaticoEnum {
  INSTALACION
  DESMONTAJE
  ROTACION
  INSPECCION
  REPARACION
  REENCAUCHE_ENTRADA
  REENCAUCHE_SALIDA
  DESECHO
  MOVIMIENTO_ALMACEN
  AJUSTE_INVENTARIO
  CAMBIO_ESTADO
  @@map("tipoeventoneumaticoenum")
}

enum TipoProveedorEnum {
  FABRICANTE
  DISTRIBUIDOR
  SERVICIO_REPARACION
  SERVICIO_REENCAUCHE
  OTRO
  @@map("tipoproveedorenum")
}

enum LadoVehiculoEnum {
  IZQUIERDO
  DERECHO
  CENTRAL
  INDETERMINADO
  @@map("lado_vehiculo_enum")
}

enum EstadoOperacionEnum {
  PENDIENTE
  EN_PROCESO
  COMPLETADA
  CANCELADA
  VENCIDA
  @@map("estado_operacion_enum")
}
```

### **3. Modelos Core (37 tablas)**
```prisma
// CATÁLOGOS
model Proveedor {
  id                String            @id @default(uuid()) @db.Uuid
  tipo              TipoProveedorEnum
  nombre            String            @db.VarChar(200)
  ruc               String?           @unique @db.VarChar(20)
  contacto_principal String?          @db.VarChar(200)
  telefono          String?           @db.VarChar(20)
  email             String?           @db.VarChar(100)
  direccion         String?           @db.Text
  activo            Boolean           @default(true)
  creado_en         DateTime          @default(now()) @db.Timestamptz(6)
  creado_por        String?           @db.Uuid
  actualizado_en    DateTime?         @db.Timestamptz(6)
  actualizado_por   String?           @db.Uuid

  // Relaciones
  eventos_neumaticos EventoNeumatico[]
  alertas           Alerta[]

  @@map("proveedores")
}

// VEHÍCULOS
model Vehiculo {
  id                    String    @id @default(uuid()) @db.Uuid
  placa                 String    @unique @db.VarChar(10)
  tipo_vehiculo_id      String    @db.Uuid
  marca                 String?   @db.VarChar(50)
  modelo                String?   @db.VarChar(50)
  anio                  Int?
  kilometraje_actual    Float?
  activo                Boolean   @default(true)
  creado_en            DateTime  @default(now()) @db.Timestamptz(6)
  actualizado_en       DateTime? @db.Timestamptz(6)

  // Relaciones
  tipo_vehiculo        TipoVehiculo     @relation(fields: [tipo_vehiculo_id], references: [id])
  neumaticos_instalados Neumatico[]
  eventos_neumaticos   EventoNeumatico[]
  registros_odometro   RegistroOdometro[]
  alertas              Alerta[]

  @@map("vehiculos")
}

// NEUMÁTICOS (Entidad principal)
model Neumatico {
  id                        String              @id @default(uuid()) @db.Uuid
  numero_serie              String              @unique @db.VarChar(50)
  modelo_id                 String              @db.Uuid
  dot                       String              @db.VarChar(4)
  estado_actual             EstadoNeumaticoEnum @default(EN_STOCK)
  profundidad_inicial_mm    Float
  profundidad_actual_mm     Float?
  presion_actual_psi        Float?
  kilometraje_acumulado     Float               @default(0)
  vida_actual               Int                 @default(1)
  reencauches_realizados    Int                 @default(0)
  es_reencauchado          Boolean             @default(false)
  fecha_compra             Date?
  costo_compra             Decimal?            @db.Decimal(10,2)
  fecha_instalacion        DateTime?           @db.Timestamptz(6)
  fecha_desecho            DateTime?           @db.Timestamptz(6)
  ubicacion_almacen_id     String?             @db.Uuid
  ubicacion_vehiculo_id    String?             @db.Uuid
  ubicacion_posicion_id    String?             @db.Uuid
  activo                   Boolean             @default(true)
  creado_en               DateTime            @default(now()) @db.Timestamptz(6)
  actualizado_en          DateTime?           @db.Timestamptz(6)

  // Relaciones
  modelo                  ModeloNeumatico      @relation(fields: [modelo_id], references: [id])
  ubicacion_almacen       Almacen?            @relation(fields: [ubicacion_almacen_id], references: [id])
  ubicacion_vehiculo      Vehiculo?           @relation(fields: [ubicacion_vehiculo_id], references: [id])
  ubicacion_posicion      PosicionNeumatico?  @relation(fields: [ubicacion_posicion_id], references: [id])
  eventos                 EventoNeumatico[]
  historial_estados       HistorialEstadoNeumatico[]
  mediciones_profundidad  MedicionProfundidad[]
  garantias               GarantiaNeumatico[]
  alertas                 Alerta[]

  @@map("neumaticos")
}
```

---

## 🛣️ API ROUTES ARCHITECTURE

### **1. Estructura de Rutas**
```
src/app/api/
├── health/route.ts                    # Health check
├── v1/
│   ├── auth/
│   │   ├── login/route.ts            # POST /auth/login
│   │   ├── refresh/route.ts          # POST /auth/refresh
│   │   └── logout/route.ts           # POST /auth/logout
│   ├── catalogos/
│   │   ├── proveedores/
│   │   │   ├── route.ts              # GET, POST /proveedores
│   │   │   └── [id]/route.ts         # GET, PUT, DELETE /proveedores/[id]
│   │   ├── almacenes/
│   │   ├── fabricantes/
│   │   └── modelos/
│   ├── vehiculos/
│   │   ├── route.ts                  # CRUD vehículos
│   │   ├── [id]/
│   │   │   ├── route.ts             # GET, PUT, DELETE
│   │   │   └── neumaticos/route.ts  # GET neumáticos instalados
│   │   └── tipos/route.ts           # CRUD tipos vehículo
│   ├── neumaticos/
│   │   ├── route.ts                 # GET, POST neumáticos
│   │   ├── [id]/
│   │   │   ├── route.ts            # GET, PUT, DELETE
│   │   │   ├── historial/route.ts  # GET historial completo
│   │   │   └── eventos/route.ts    # POST nuevo evento
│   │   ├── eventos/route.ts        # POST eventos masivos
│   │   └── instalados/route.ts     # GET neumáticos instalados
│   ├── inventario/
│   │   ├── route.ts                # GET estado inventario
│   │   ├── movimientos/route.ts    # GET, POST movimientos
│   │   └── alertas/route.ts        # GET alertas stock
│   ├── reportes/
│   │   ├── dashboard/route.ts      # GET métricas dashboard
│   │   ├── rendimiento/route.ts    # GET reportes rendimiento
│   │   └── auditoria/route.ts      # GET logs auditoría
│   └── sistema/
│       ├── usuarios/route.ts       # CRUD usuarios
│       ├── roles/route.ts          # CRUD roles
│       └── permisos/route.ts       # CRUD permisos
```

### **2. Patrón de API Route Estándar**
```typescript
// src/app/api/v1/neumaticos/route.ts
import { NextRequest } from 'next/server'
import { validateAuth, checkPermissions } from '@/lib/auth/middleware'
import { NeumaticoService } from '@/lib/services/neumatico.service'
import { ApiResponse } from '@/lib/utils/api-response'
import { NeumaticoCreateSchema, NeumaticoQuerySchema } from '@/lib/validators/neumatico'

export async function GET(request: NextRequest) {
  try {
    // 1. Autenticación
    const user = await validateAuth(request)
    if (!user) return ApiResponse.unauthorized()

    // 2. Autorización
    if (!checkPermissions(user, 'neumaticos:read')) {
      return ApiResponse.forbidden()
    }

    // 3. Validación de query params
    const { searchParams } = new URL(request.url)
    const queryParams = NeumaticoQuerySchema.parse({
      page: searchParams.get('page') || '1',
      limit: searchParams.get('limit') || '10',
      estado: searchParams.get('estado'),
      almacen_id: searchParams.get('almacen_id')
    })

    // 4. Lógica de negocio
    const result = await NeumaticoService.findMany(queryParams, user)

    // 5. Respuesta
    return ApiResponse.success(result)
  } catch (error) {
    return ApiResponse.handleError(error)
  }
}

export async function POST(request: NextRequest) {
  try {
    const user = await validateAuth(request)
    if (!user) return ApiResponse.unauthorized()

    if (!checkPermissions(user, 'neumaticos:create')) {
      return ApiResponse.forbidden()
    }

    const body = await request.json()
    const validatedData = NeumaticoCreateSchema.parse(body)

    const neumatico = await NeumaticoService.create(validatedData, user)

    return ApiResponse.created(neumatico)
  } catch (error) {
    return ApiResponse.handleError(error)
  }
}
```

---

## 🔐 MIDDLEWARE ARCHITECTURE

### **1. Middleware Principal**
```typescript
// src/middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { verifyJWT } from '@/lib/auth/jwt'
import { rateLimiter } from '@/lib/utils/rate-limiter'

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // 1. Rate Limiting
  const rateLimitResult = await rateLimiter(request)
  if (!rateLimitResult.success) {
    return new NextResponse('Too Many Requests', { status: 429 })
  }

  // 2. Public routes (no auth required)
  if (pathname === '/api/health' || pathname.startsWith('/api/auth/login')) {
    return NextResponse.next()
  }

  // 3. Protected API routes
  if (pathname.startsWith('/api/v1/')) {
    const token = request.headers.get('authorization')?.replace('Bearer ', '')
    
    if (!token) {
      return new NextResponse('Unauthorized', { status: 401 })
    }

    try {
      const payload = await verifyJWT(token)
      
      // Add user info to headers for downstream handlers
      const requestHeaders = new Headers(request.headers)
      requestHeaders.set('x-user-id', payload.sub)
      requestHeaders.set('x-user-role', payload.role)

      return NextResponse.next({
        request: {
          headers: requestHeaders,
        },
      })
    } catch (error) {
      return new NextResponse('Invalid Token', { status: 401 })
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    '/api/((?!_next/static|_next/image|favicon.ico).*)',
  ],
}
```

### **2. Helpers de Autenticación**
```typescript
// src/lib/auth/middleware.ts
import { NextRequest } from 'next/server'
import { prisma } from '@/lib/prisma'

export async function validateAuth(request: NextRequest) {
  const userId = request.headers.get('x-user-id')
  const userRole = request.headers.get('x-user-role')

  if (!userId) return null

  // Get full user with permissions
  const user = await prisma.usuario.findUnique({
    where: { id: userId },
    include: {
      roles: {
        include: {
          rol: {
            include: {
              permisos: {
                include: {
                  permiso: true
                }
              }
            }
          }
        }
      }
    }
  })

  return user
}

export function checkPermissions(user: any, permission: string): boolean {
  if (!user) return false

  // Extract all permissions from user roles
  const userPermissions = user.roles.flatMap(ur => 
    ur.rol.permisos.map(rp => rp.permiso.codigo)
  )

  return userPermissions.includes(permission)
}
```

---

## 📊 PATRONES DE RESPUESTA API

### **1. Clase ApiResponse Estándar**
```typescript
// src/lib/utils/api-response.ts
import { NextResponse } from 'next/server'

export class ApiResponse {
  static success<T>(data: T, message?: string) {
    return NextResponse.json({
      success: true,
      data,
      message,
      timestamp: new Date().toISOString()
    })
  }

  static created<T>(data: T, message?: string) {
    return NextResponse.json({
      success: true,
      data,
      message: message || 'Resource created successfully',
      timestamp: new Date().toISOString()
    }, { status: 201 })
  }

  static paginated<T>(data: T[], pagination: PaginationMeta) {
    return NextResponse.json({
      success: true,
      data,
      pagination,
      timestamp: new Date().toISOString()
    })
  }

  static error(message: string, status: number = 500) {
    return NextResponse.json({
      success: false,
      error: message,
      timestamp: new Date().toISOString()
    }, { status })
  }

  static unauthorized(message = 'Unauthorized') {
    return this.error(message, 401)
  }

  static forbidden(message = 'Forbidden') {
    return this.error(message, 403)
  }

  static notFound(message = 'Resource not found') {
    return this.error(message, 404)
  }

  static handleError(error: unknown) {
    console.error('API Error:', error)
    
    if (error instanceof ZodError) {
      return this.error('Validation failed: ' + error.message, 400)
    }
    
    if (error instanceof PrismaClientKnownRequestError) {
      return this.error('Database error: ' + error.message, 500)
    }

    return this.error('Internal server error', 500)
  }
}
```

---

**Estado:** ✅ PARTE 2 completada  
**Próximo:** PARTE 3 - Patrones de Implementación
