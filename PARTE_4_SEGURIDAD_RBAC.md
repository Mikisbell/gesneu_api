# PARTE 4: SISTEMA DE SEGURIDAD Y RBAC
## NextAuth + JWT + Permisos Granulares

**Fecha:** 14 de Noviembre, 2025  
**Versión:** 1.0  
**Dependencias:** PARTE 1, 2 y 3 completadas

---

## 🔐 ARQUITECTURA DE SEGURIDAD

### **1. Stack de Seguridad**
```
CAPA DE AUTENTICACIÓN:
├── NextAuth.js (OAuth + Credentials)
├── JWT Tokens (Access + Refresh)
├── Bcrypt (Password hashing)
└── Rate Limiting (DDoS protection)

CAPA DE AUTORIZACIÓN:
├── RBAC (Role-Based Access Control)
├── Permisos granulares por recurso
├── Middleware de autorización
└── Context-aware permissions

CAPA DE AUDITORÍA:
├── Logs de autenticación
├── Tracking de cambios
├── Session management
└── Security events
```

### **2. Configuración NextAuth.js**
```typescript
// src/lib/auth/config.ts
import { NextAuthOptions } from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'
import { PrismaAdapter } from '@next-auth/prisma-adapter'
import { prisma } from '@/lib/prisma'
import { compare } from 'bcryptjs'
import { JWT } from 'next-auth/jwt'

export const authOptions: NextAuthOptions = {
  adapter: PrismaAdapter(prisma),
  providers: [
    CredentialsProvider({
      name: 'credentials',
      credentials: {
        username: { label: 'Username', type: 'text' },
        password: { label: 'Password', type: 'password' }
      },
      async authorize(credentials) {
        if (!credentials?.username || !credentials?.password) {
          return null
        }

        const user = await prisma.usuario.findUnique({
          where: { username: credentials.username },
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

        if (!user || !user.activo) {
          return null
        }

        const isPasswordValid = await compare(credentials.password, user.password_hash)
        
        if (!isPasswordValid) {
          return null
        }

        // Registrar login exitoso
        await prisma.auditoriaLog.create({
          data: {
            esquema_tabla: 'public',
            nombre_tabla: 'usuarios',
            operacion: 'LOGIN',
            usuario_aplicacion_id: user.id,
            usuario_aplicacion_username: user.username,
            contexto_aplicacion: {
              evento: 'login_exitoso',
              timestamp: new Date().toISOString()
            }
          }
        })

        return {
          id: user.id,
          username: user.username,
          email: user.email,
          nombre_completo: user.nombre_completo,
          roles: user.roles.map(ur => ({
            id: ur.rol.id,
            nombre: ur.rol.nombre,
            permisos: ur.rol.permisos.map(rp => rp.permiso.codigo)
          }))
        }
      }
    })
  ],
  session: {
    strategy: 'jwt',
    maxAge: 8 * 60 * 60, // 8 horas
  },
  jwt: {
    maxAge: 8 * 60 * 60, // 8 horas
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.sub = user.id
        token.username = user.username
        token.roles = user.roles
        token.permissions = user.roles.flatMap(r => r.permisos)
      }
      return token
    },
    async session({ session, token }) {
      if (token) {
        session.user.id = token.sub
        session.user.username = token.username
        session.user.roles = token.roles
        session.user.permissions = token.permissions
      }
      return session
    }
  },
  pages: {
    signIn: '/auth/login',
    error: '/auth/error'
  },
  events: {
    async signOut({ token }) {
      // Registrar logout
      if (token?.sub) {
        await prisma.auditoriaLog.create({
          data: {
            esquema_tabla: 'public',
            nombre_tabla: 'usuarios',
            operacion: 'LOGOUT',
            usuario_aplicacion_id: token.sub as string,
            contexto_aplicacion: {
              evento: 'logout',
              timestamp: new Date().toISOString()
            }
          }
        })
      }
    }
  }
}
```

---

## 👥 SISTEMA RBAC COMPLETO

### **1. Modelos de Seguridad (Prisma)**
```prisma
// Agregado al schema.prisma existente

model Rol {
  id              String    @id @default(uuid()) @db.Uuid
  nombre          String    @unique @db.VarChar(50)
  descripcion     String?   @db.Text
  activo          Boolean   @default(true)
  creado_en       DateTime  @default(now()) @db.Timestamptz(6)
  creado_por      String?   @db.Uuid
  actualizado_en  DateTime? @db.Timestamptz(6)
  actualizado_por String?   @db.Uuid

  // Relaciones
  usuarios        UsuarioRol[]
  permisos        RolPermiso[]

  @@map("roles")
}

model Permiso {
  id              String    @id @default(uuid()) @db.Uuid
  codigo          String    @unique @db.VarChar(100)
  nombre          String    @db.VarChar(100)
  descripcion     String?   @db.Text
  recurso         String    @db.VarChar(50)  // neumaticos, vehiculos, etc.
  accion          String    @db.VarChar(50)  // create, read, update, delete
  activo          Boolean   @default(true)
  creado_en       DateTime  @default(now()) @db.Timestamptz(6)

  // Relaciones
  roles           RolPermiso[]

  @@map("permisos")
}

model UsuarioRol {
  id              String    @id @default(uuid()) @db.Uuid
  usuario_id      String    @db.Uuid
  rol_id          String    @db.Uuid
  asignado_en     DateTime  @default(now()) @db.Timestamptz(6)
  asignado_por    String?   @db.Uuid
  activo          Boolean   @default(true)

  // Relaciones
  usuario         Usuario   @relation(fields: [usuario_id], references: [id])
  rol             Rol       @relation(fields: [rol_id], references: [id])

  @@unique([usuario_id, rol_id])
  @@map("usuarios_roles")
}

model RolPermiso {
  id              String    @id @default(uuid()) @db.Uuid
  rol_id          String    @db.Uuid
  permiso_id      String    @db.Uuid
  asignado_en     DateTime  @default(now()) @db.Timestamptz(6)
  asignado_por    String?   @db.Uuid

  // Relaciones
  rol             Rol       @relation(fields: [rol_id], references: [id])
  permiso         Permiso   @relation(fields: [permiso_id], references: [id])

  @@unique([rol_id, permiso_id])
  @@map("roles_permisos")
}

// Actualizar modelo Usuario existente
model Usuario {
  id              String    @id @default(uuid()) @db.Uuid
  username        String    @unique @db.VarChar(50)
  nombre_completo String    @db.VarChar(200)
  email           String    @unique @db.VarChar(100)
  password_hash   String    @db.Text
  ultimo_login    DateTime? @db.Timestamptz(6)
  intentos_login  Int       @default(0)
  bloqueado_hasta DateTime? @db.Timestamptz(6)
  activo          Boolean   @default(true)
  creado_en       DateTime  @default(now()) @db.Timestamptz(6)
  creado_por      String?   @db.Uuid
  actualizado_en  DateTime? @db.Timestamptz(6)
  actualizado_por String?   @db.Uuid

  // Relaciones
  roles           UsuarioRol[]

  @@map("usuarios")
}
```

### **2. Definición de Permisos del Sistema**
```typescript
// src/lib/auth/permissions.ts
export const PERMISSIONS = {
  // CATÁLOGOS
  CATALOGOS_PROVEEDORES_READ: 'catalogos:proveedores:read',
  CATALOGOS_PROVEEDORES_CREATE: 'catalogos:proveedores:create',
  CATALOGOS_PROVEEDORES_UPDATE: 'catalogos:proveedores:update',
  CATALOGOS_PROVEEDORES_DELETE: 'catalogos:proveedores:delete',
  
  CATALOGOS_ALMACENES_READ: 'catalogos:almacenes:read',
  CATALOGOS_ALMACENES_CREATE: 'catalogos:almacenes:create',
  CATALOGOS_ALMACENES_UPDATE: 'catalogos:almacenes:update',
  CATALOGOS_ALMACENES_DELETE: 'catalogos:almacenes:delete',

  // VEHÍCULOS
  VEHICULOS_READ: 'vehiculos:read',
  VEHICULOS_CREATE: 'vehiculos:create',
  VEHICULOS_UPDATE: 'vehiculos:update',
  VEHICULOS_DELETE: 'vehiculos:delete',
  VEHICULOS_CONFIGURAR: 'vehiculos:configurar',

  // NEUMÁTICOS
  NEUMATICOS_READ: 'neumaticos:read',
  NEUMATICOS_CREATE: 'neumaticos:create',
  NEUMATICOS_UPDATE: 'neumaticos:update',
  NEUMATICOS_DELETE: 'neumaticos:delete',
  
  // EVENTOS DE NEUMÁTICOS (Granular por tipo)
  NEUMATICOS_EVENTO_INSTALACION: 'neumaticos:evento:instalacion',
  NEUMATICOS_EVENTO_DESMONTAJE: 'neumaticos:evento:desmontaje',
  NEUMATICOS_EVENTO_ROTACION: 'neumaticos:evento:rotacion',
  NEUMATICOS_EVENTO_INSPECCION: 'neumaticos:evento:inspeccion',
  NEUMATICOS_EVENTO_REPARACION: 'neumaticos:evento:reparacion',
  NEUMATICOS_EVENTO_REENCAUCHE: 'neumaticos:evento:reencauche',
  NEUMATICOS_EVENTO_DESECHO: 'neumaticos:evento:desecho',
  NEUMATICOS_EVENTO_AJUSTE: 'neumaticos:evento:ajuste',

  // INVENTARIO
  INVENTARIO_READ: 'inventario:read',
  INVENTARIO_MOVIMIENTOS: 'inventario:movimientos',
  INVENTARIO_AJUSTES: 'inventario:ajustes',

  // REPORTES
  REPORTES_DASHBOARD: 'reportes:dashboard',
  REPORTES_RENDIMIENTO: 'reportes:rendimiento',
  REPORTES_AUDITORIA: 'reportes:auditoria',

  // SISTEMA
  SISTEMA_USUARIOS_READ: 'sistema:usuarios:read',
  SISTEMA_USUARIOS_CREATE: 'sistema:usuarios:create',
  SISTEMA_USUARIOS_UPDATE: 'sistema:usuarios:update',
  SISTEMA_USUARIOS_DELETE: 'sistema:usuarios:delete',
  SISTEMA_ROLES_MANAGE: 'sistema:roles:manage',
  SISTEMA_PERMISOS_MANAGE: 'sistema:permisos:manage',
  SISTEMA_AUDITORIA_READ: 'sistema:auditoria:read'
} as const

export type Permission = typeof PERMISSIONS[keyof typeof PERMISSIONS]
```

### **3. Roles Predefinidos del Sistema**
```typescript
// src/lib/auth/roles.ts
import { PERMISSIONS } from './permissions'

export const SYSTEM_ROLES = {
  ADMIN: {
    nombre: 'ADMINISTRADOR',
    descripcion: 'Acceso completo al sistema',
    permisos: Object.values(PERMISSIONS) // Todos los permisos
  },

  GESTOR: {
    nombre: 'GESTOR',
    descripcion: 'Gestión operativa completa',
    permisos: [
      // Catálogos - CRUD completo
      PERMISSIONS.CATALOGOS_PROVEEDORES_READ,
      PERMISSIONS.CATALOGOS_PROVEEDORES_CREATE,
      PERMISSIONS.CATALOGOS_PROVEEDORES_UPDATE,
      PERMISSIONS.CATALOGOS_ALMACENES_READ,
      PERMISSIONS.CATALOGOS_ALMACENES_CREATE,
      PERMISSIONS.CATALOGOS_ALMACENES_UPDATE,

      // Vehículos - CRUD completo
      PERMISSIONS.VEHICULOS_READ,
      PERMISSIONS.VEHICULOS_CREATE,
      PERMISSIONS.VEHICULOS_UPDATE,
      PERMISSIONS.VEHICULOS_CONFIGURAR,

      // Neumáticos - CRUD completo
      PERMISSIONS.NEUMATICOS_READ,
      PERMISSIONS.NEUMATICOS_CREATE,
      PERMISSIONS.NEUMATICOS_UPDATE,

      // Eventos - Todos excepto ajustes
      PERMISSIONS.NEUMATICOS_EVENTO_INSTALACION,
      PERMISSIONS.NEUMATICOS_EVENTO_DESMONTAJE,
      PERMISSIONS.NEUMATICOS_EVENTO_ROTACION,
      PERMISSIONS.NEUMATICOS_EVENTO_INSPECCION,
      PERMISSIONS.NEUMATICOS_EVENTO_REPARACION,
      PERMISSIONS.NEUMATICOS_EVENTO_REENCAUCHE,
      PERMISSIONS.NEUMATICOS_EVENTO_DESECHO,

      // Inventario - Lectura y movimientos
      PERMISSIONS.INVENTARIO_READ,
      PERMISSIONS.INVENTARIO_MOVIMIENTOS,

      // Reportes - Dashboard y rendimiento
      PERMISSIONS.REPORTES_DASHBOARD,
      PERMISSIONS.REPORTES_RENDIMIENTO
    ]
  },

  OPERADOR: {
    nombre: 'OPERADOR',
    descripcion: 'Operaciones diarias de campo',
    permisos: [
      // Catálogos - Solo lectura
      PERMISSIONS.CATALOGOS_PROVEEDORES_READ,
      PERMISSIONS.CATALOGOS_ALMACENES_READ,

      // Vehículos - Solo lectura
      PERMISSIONS.VEHICULOS_READ,

      // Neumáticos - Lectura y eventos operativos
      PERMISSIONS.NEUMATICOS_READ,
      PERMISSIONS.NEUMATICOS_EVENTO_INSTALACION,
      PERMISSIONS.NEUMATICOS_EVENTO_DESMONTAJE,
      PERMISSIONS.NEUMATICOS_EVENTO_ROTACION,
      PERMISSIONS.NEUMATICOS_EVENTO_INSPECCION,

      // Inventario - Solo lectura
      PERMISSIONS.INVENTARIO_READ,

      // Reportes - Solo dashboard
      PERMISSIONS.REPORTES_DASHBOARD
    ]
  },

  CONSULTOR: {
    nombre: 'CONSULTOR',
    descripcion: 'Solo lectura y reportes',
    permisos: [
      // Solo permisos de lectura
      PERMISSIONS.CATALOGOS_PROVEEDORES_READ,
      PERMISSIONS.CATALOGOS_ALMACENES_READ,
      PERMISSIONS.VEHICULOS_READ,
      PERMISSIONS.NEUMATICOS_READ,
      PERMISSIONS.INVENTARIO_READ,
      PERMISSIONS.REPORTES_DASHBOARD,
      PERMISSIONS.REPORTES_RENDIMIENTO
    ]
  }
} as const
```

---

## 🛡️ MIDDLEWARE DE AUTORIZACIÓN

### **1. Middleware Principal Actualizado**
```typescript
// src/middleware.ts (actualizado)
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { getToken } from 'next-auth/jwt'
import { rateLimiter } from '@/lib/utils/rate-limiter'

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // 1. Rate Limiting por IP
  const rateLimitResult = await rateLimiter(request)
  if (!rateLimitResult.success) {
    return new NextResponse('Too Many Requests', { 
      status: 429,
      headers: {
        'Retry-After': '60'
      }
    })
  }

  // 2. Rutas públicas
  const publicRoutes = [
    '/api/health',
    '/api/auth/signin',
    '/api/auth/signout',
    '/api/auth/session',
    '/api/auth/providers',
    '/api/auth/callback',
    '/api/auth/csrf'
  ]

  if (publicRoutes.some(route => pathname.startsWith(route))) {
    return NextResponse.next()
  }

  // 3. Rutas protegidas de API
  if (pathname.startsWith('/api/v1/')) {
    const token = await getToken({ 
      req: request, 
      secret: process.env.NEXTAUTH_SECRET 
    })

    if (!token) {
      return new NextResponse('Unauthorized', { status: 401 })
    }

    // Verificar si el usuario está activo
    const user = await prisma.usuario.findUnique({
      where: { id: token.sub }
    })

    if (!user || !user.activo) {
      return new NextResponse('Account disabled', { status: 403 })
    }

    // Verificar bloqueo por intentos fallidos
    if (user.bloqueado_hasta && user.bloqueado_hasta > new Date()) {
      return new NextResponse('Account temporarily locked', { status: 423 })
    }

    // Agregar información del usuario a headers
    const requestHeaders = new Headers(request.headers)
    requestHeaders.set('x-user-id', token.sub!)
    requestHeaders.set('x-user-username', token.username as string)
    requestHeaders.set('x-user-permissions', JSON.stringify(token.permissions))

    return NextResponse.next({
      request: {
        headers: requestHeaders,
      },
    })
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    '/api/((?!_next/static|_next/image|favicon.ico).*)',
    '/((?!_next/static|_next/image|favicon.ico).*)'
  ],
}
```

### **2. Helper de Autorización Avanzado**
```typescript
// src/lib/auth/authorization.ts
import { NextRequest } from 'next/server'
import { Permission } from './permissions'

export class AuthorizationHelper {
  static getUserFromRequest(request: NextRequest) {
    const userId = request.headers.get('x-user-id')
    const username = request.headers.get('x-user-username')
    const permissionsHeader = request.headers.get('x-user-permissions')
    
    if (!userId || !permissionsHeader) {
      return null
    }

    try {
      const permissions = JSON.parse(permissionsHeader) as string[]
      return {
        id: userId,
        username,
        permissions
      }
    } catch {
      return null
    }
  }

  static hasPermission(user: any, permission: Permission): boolean {
    if (!user || !user.permissions) {
      return false
    }

    return user.permissions.includes(permission)
  }

  static hasAnyPermission(user: any, permissions: Permission[]): boolean {
    if (!user || !user.permissions) {
      return false
    }

    return permissions.some(permission => 
      user.permissions.includes(permission)
    )
  }

  static hasAllPermissions(user: any, permissions: Permission[]): boolean {
    if (!user || !user.permissions) {
      return false
    }

    return permissions.every(permission => 
      user.permissions.includes(permission)
    )
  }

  // Verificación contextual (ej: solo puede editar sus propios registros)
  static canAccessResource(
    user: any, 
    permission: Permission, 
    resourceOwnerId?: string
  ): boolean {
    if (!this.hasPermission(user, permission)) {
      return false
    }

    // Si no hay owner específico, el permiso es suficiente
    if (!resourceOwnerId) {
      return true
    }

    // Los admins pueden acceder a todo
    if (this.hasPermission(user, 'sistema:usuarios:delete' as Permission)) {
      return true
    }

    // Los usuarios solo pueden acceder a sus propios recursos
    return user.id === resourceOwnerId
  }
}
```

### **3. Decorador de Autorización para API Routes**
```typescript
// src/lib/auth/decorators.ts
import { NextRequest } from 'next/server'
import { AuthorizationHelper } from './authorization'
import { ApiResponse } from '@/lib/utils/api-response'
import { Permission } from './permissions'

export function requirePermissions(permissions: Permission[]) {
  return function (
    target: any,
    propertyName: string,
    descriptor: PropertyDescriptor
  ) {
    const method = descriptor.value

    descriptor.value = async function (request: NextRequest, ...args: any[]) {
      const user = AuthorizationHelper.getUserFromRequest(request)
      
      if (!user) {
        return ApiResponse.unauthorized('Authentication required')
      }

      if (!AuthorizationHelper.hasAllPermissions(user, permissions)) {
        return ApiResponse.forbidden('Insufficient permissions')
      }

      return method.apply(this, [request, ...args])
    }

    return descriptor
  }
}

// Uso en API Routes:
// @requirePermissions([PERMISSIONS.NEUMATICOS_CREATE])
// export async function POST(request: NextRequest) { ... }
```

---

## 🔍 AUDITORÍA Y LOGGING

### **1. Sistema de Auditoría Completo**
```typescript
// src/lib/services/auditoria.service.ts
import { prisma } from '@/lib/prisma'

export class AuditoriaService {
  async registrarCambio(
    tabla: string,
    entidadId: string,
    operacion: string,
    datosAntiguos: any,
    datosNuevos: any,
    usuarioId: string,
    contextoAdicional?: any,
    tx?: any
  ) {
    const client = tx || prisma

    const cambios = this.calcularCambios(datosAntiguos, datosNuevos)

    return client.auditoriaLog.create({
      data: {
        esquema_tabla: 'public',
        nombre_tabla: tabla,
        operacion: operacion.toUpperCase(),
        usuario_aplicacion_id: usuarioId,
        id_entidad: entidadId,
        datos_antiguos: datosAntiguos,
        datos_nuevos: datosNuevos,
        cambios,
        contexto_aplicacion: {
          ...contextoAdicional,
          timestamp: new Date().toISOString(),
          user_agent: contextoAdicional?.userAgent,
          ip_address: contextoAdicional?.ipAddress
        }
      }
    })
  }

  async registrarEventoSeguridad(
    evento: string,
    usuarioId: string | null,
    detalles: any,
    nivelSeveridad: 'INFO' | 'WARN' | 'CRITICAL' = 'INFO'
  ) {
    return prisma.auditoriaLog.create({
      data: {
        esquema_tabla: 'security',
        nombre_tabla: 'eventos_seguridad',
        operacion: evento.toUpperCase(),
        usuario_aplicacion_id: usuarioId,
        contexto_aplicacion: {
          evento,
          detalles,
          nivel_severidad: nivelSeveridad,
          timestamp: new Date().toISOString()
        }
      }
    })
  }

  private calcularCambios(datosAntiguos: any, datosNuevos: any): any {
    if (!datosAntiguos || !datosNuevos) {
      return null
    }

    const cambios: any = {}
    
    for (const key in datosNuevos) {
      if (datosAntiguos[key] !== datosNuevos[key]) {
        cambios[key] = {
          anterior: datosAntiguos[key],
          nuevo: datosNuevos[key]
        }
      }
    }

    return Object.keys(cambios).length > 0 ? cambios : null
  }

  // Consultas de auditoría
  async getLogsPorUsuario(usuarioId: string, limite: number = 100) {
    return prisma.auditoriaLog.findMany({
      where: { usuario_aplicacion_id: usuarioId },
      orderBy: { timestamp_log: 'desc' },
      take: limite
    })
  }

  async getLogsPorEntidad(tabla: string, entidadId: string) {
    return prisma.auditoriaLog.findMany({
      where: {
        nombre_tabla: tabla,
        id_entidad: entidadId
      },
      orderBy: { timestamp_log: 'desc' }
    })
  }
}
```

### **2. Rate Limiting Avanzado**
```typescript
// src/lib/utils/rate-limiter.ts
import { NextRequest } from 'next/server'

interface RateLimitConfig {
  windowMs: number
  maxRequests: number
  skipSuccessfulRequests?: boolean
}

const rateLimitConfigs: Record<string, RateLimitConfig> = {
  '/api/auth/signin': { windowMs: 15 * 60 * 1000, maxRequests: 5 }, // 5 intentos por 15 min
  '/api/v1/': { windowMs: 60 * 1000, maxRequests: 100 }, // 100 req por minuto
  'default': { windowMs: 60 * 1000, maxRequests: 60 } // 60 req por minuto
}

const requestCounts = new Map<string, { count: number; resetTime: number }>()

export async function rateLimiter(request: NextRequest) {
  const ip = request.ip || request.headers.get('x-forwarded-for') || 'unknown'
  const pathname = request.nextUrl.pathname
  
  // Determinar configuración de rate limit
  let config = rateLimitConfigs.default
  for (const [path, pathConfig] of Object.entries(rateLimitConfigs)) {
    if (pathname.startsWith(path)) {
      config = pathConfig
      break
    }
  }

  const key = `${ip}:${pathname}`
  const now = Date.now()
  const windowStart = now - config.windowMs

  // Limpiar entradas expiradas
  for (const [k, v] of requestCounts.entries()) {
    if (v.resetTime < now) {
      requestCounts.delete(k)
    }
  }

  const current = requestCounts.get(key)
  
  if (!current) {
    requestCounts.set(key, { count: 1, resetTime: now + config.windowMs })
    return { success: true }
  }

  if (current.count >= config.maxRequests) {
    return { 
      success: false, 
      resetTime: current.resetTime,
      limit: config.maxRequests,
      remaining: 0
    }
  }

  current.count++
  return { 
    success: true, 
    limit: config.maxRequests,
    remaining: config.maxRequests - current.count
  }
}
```

---

**Estado:** ✅ PARTE 4 completada  
**Próximo:** PARTE 5 - Testing y Calidad
