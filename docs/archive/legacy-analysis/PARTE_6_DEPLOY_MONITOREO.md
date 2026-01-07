# PARTE 6: DEPLOY Y MONITOREO
## Vercel + Performance + Observabilidad + Alertas

**Fecha:** 14 de Noviembre, 2025  
**Versión:** 1.0  
**Dependencias:** PARTE 1-5 completadas

---

## 🚀 ESTRATEGIA DE DEPLOYMENT

### **1. Configuración Vercel**
```json
// vercel.json
{
  "version": 2,
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "installCommand": "npm ci",
  "functions": {
    "src/app/api/**/*.ts": {
      "maxDuration": 30
    }
  },
  "env": {
    "DATABASE_URL": "@database_url",
    "NEXTAUTH_SECRET": "@nextauth_secret",
    "NEXTAUTH_URL": "@nextauth_url"
  },
  "build": {
    "env": {
      "SKIP_ENV_VALIDATION": "1"
    }
  },
  "regions": ["iad1"],
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "/api/$1"
    }
  ],
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "no-cache, no-store, must-revalidate"
        },
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        }
      ]
    }
  ]
}
```

### **2. Variables de Entorno Producción**
```bash
# .env.production
DATABASE_URL="postgresql://user:pass@host:5432/gesneu_prod"
NEXTAUTH_SECRET="production-secret-key-256-bits"
NEXTAUTH_URL="https://gesneu-api.vercel.app"
NODE_ENV="production"
APP_ENV="production"

# Monitoring
SENTRY_DSN="https://key@sentry.io/project"
VERCEL_ANALYTICS_ID="analytics-id"

# Database Connection Pool
DATABASE_POOL_SIZE="10"
DATABASE_MAX_OVERFLOW="20"
DATABASE_TIMEOUT="30000"

# Rate Limiting
REDIS_URL="redis://redis-host:6379"
RATE_LIMIT_WINDOW="60000"
RATE_LIMIT_MAX="100"
```

---

## 📊 MONITOREO Y OBSERVABILIDAD

### **1. Instrumentación con Sentry**
```typescript
// src/instrumentation.ts
import * as Sentry from '@sentry/nextjs'

export function register() {
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    Sentry.init({
      dsn: process.env.SENTRY_DSN,
      environment: process.env.NODE_ENV,
      tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.1 : 1.0,
      integrations: [
        new Sentry.Integrations.Prisma({ client: prisma }),
        new Sentry.Integrations.Http({ tracing: true })
      ],
      beforeSend(event) {
        // Filtrar información sensible
        if (event.request?.data) {
          delete event.request.data.password
          delete event.request.data.token
        }
        return event
      }
    })
  }

  if (process.env.NEXT_RUNTIME === 'edge') {
    Sentry.init({
      dsn: process.env.SENTRY_DSN,
      tracesSampleRate: 0.1
    })
  }
}
```

### **2. Métricas Personalizadas**
```typescript
// src/lib/monitoring/metrics.ts
import { Histogram, Counter, register } from 'prom-client'

// Métricas HTTP
export const httpRequestDuration = new Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.1, 0.3, 0.5, 0.7, 1, 3, 5, 7, 10]
})

export const httpRequestTotal = new Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status_code']
})

// Métricas de Base de Datos
export const dbQueryDuration = new Histogram({
  name: 'db_query_duration_seconds',
  help: 'Duration of database queries in seconds',
  labelNames: ['operation', 'table'],
  buckets: [0.01, 0.05, 0.1, 0.3, 0.5, 1, 3, 5]
})

export const dbConnectionPool = new Counter({
  name: 'db_connection_pool_total',
  help: 'Database connection pool usage',
  labelNames: ['status'] // 'acquired', 'released', 'timeout'
})

// Métricas de Negocio
export const neumaticoEvents = new Counter({
  name: 'neumatico_events_total',
  help: 'Total neumatico events processed',
  labelNames: ['event_type', 'status']
})

export const activeUsers = new Counter({
  name: 'active_users_total',
  help: 'Total active users',
  labelNames: ['role']
})

register.registerMetric(httpRequestDuration)
register.registerMetric(httpRequestTotal)
register.registerMetric(dbQueryDuration)
register.registerMetric(dbConnectionPool)
register.registerMetric(neumaticoEvents)
register.registerMetric(activeUsers)
```

### **3. Middleware de Métricas**
```typescript
// src/lib/monitoring/middleware.ts
import { NextRequest, NextResponse } from 'next/server'
import { httpRequestDuration, httpRequestTotal } from './metrics'

export function metricsMiddleware(request: NextRequest) {
  const start = Date.now()
  const { pathname, method } = request.nextUrl

  return NextResponse.next().then((response) => {
    const duration = (Date.now() - start) / 1000
    const statusCode = response.status.toString()

    // Registrar métricas
    httpRequestDuration
      .labels(method, pathname, statusCode)
      .observe(duration)
    
    httpRequestTotal
      .labels(method, pathname, statusCode)
      .inc()

    return response
  })
}
```

---

## 🔍 LOGGING ESTRUCTURADO

### **1. Configuración Winston**
```typescript
// src/lib/logging/logger.ts
import winston from 'winston'

const logFormat = winston.format.combine(
  winston.format.timestamp(),
  winston.format.errors({ stack: true }),
  winston.format.json(),
  winston.format.printf(({ timestamp, level, message, ...meta }) => {
    return JSON.stringify({
      timestamp,
      level,
      message,
      service: 'gesneu-api',
      environment: process.env.NODE_ENV,
      ...meta
    })
  })
)

export const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: logFormat,
  transports: [
    new winston.transports.Console(),
    ...(process.env.NODE_ENV === 'production' ? [
      new winston.transports.File({
        filename: 'logs/error.log',
        level: 'error',
        maxsize: 5242880, // 5MB
        maxFiles: 5
      }),
      new winston.transports.File({
        filename: 'logs/combined.log',
        maxsize: 5242880,
        maxFiles: 5
      })
    ] : [])
  ]
})

// Logging helpers
export const loggers = {
  auth: logger.child({ component: 'auth' }),
  neumaticos: logger.child({ component: 'neumaticos' }),
  vehiculos: logger.child({ component: 'vehiculos' }),
  database: logger.child({ component: 'database' }),
  api: logger.child({ component: 'api' })
}
```

### **2. Structured Logging en Services**
```typescript
// Ejemplo en NeumaticoService
import { loggers } from '@/lib/logging/logger'

export class NeumaticoService {
  async registrarEvento(eventoData: any, userId: string) {
    const correlationId = crypto.randomUUID()
    
    loggers.neumaticos.info('Iniciando registro de evento', {
      correlationId,
      userId,
      tipoEvento: eventoData.tipo_evento,
      neumaticoId: eventoData.neumatico_id
    })

    try {
      const result = await this.repository.prisma.$transaction(async (tx) => {
        // ... lógica de negocio
        
        loggers.neumaticos.debug('Evento procesado exitosamente', {
          correlationId,
          eventoId: evento.id,
          estadoAnterior: neumatico.estado_actual,
          estadoNuevo: result.neumatico.estado_actual
        })

        return result
      })

      // Métricas
      neumaticoEvents
        .labels(eventoData.tipo_evento, 'success')
        .inc()

      loggers.neumaticos.info('Evento registrado exitosamente', {
        correlationId,
        eventoId: result.evento.id,
        duration: Date.now() - start
      })

      return result
    } catch (error) {
      neumaticoEvents
        .labels(eventoData.tipo_evento, 'error')
        .inc()

      loggers.neumaticos.error('Error registrando evento', {
        correlationId,
        error: error.message,
        stack: error.stack,
        eventoData
      })

      throw error
    }
  }
}
```

---

## ⚡ OPTIMIZACIÓN DE PERFORMANCE

### **1. Configuración de Cache**
```typescript
// src/lib/cache/redis.ts
import { Redis } from 'ioredis'

export const redis = new Redis(process.env.REDIS_URL!, {
  retryDelayOnFailover: 100,
  maxRetriesPerRequest: 3,
  lazyConnect: true
})

export class CacheService {
  static async get<T>(key: string): Promise<T | null> {
    try {
      const cached = await redis.get(key)
      return cached ? JSON.parse(cached) : null
    } catch (error) {
      logger.warn('Cache get failed', { key, error: error.message })
      return null
    }
  }

  static async set(key: string, value: any, ttl: number = 300): Promise<void> {
    try {
      await redis.setex(key, ttl, JSON.stringify(value))
    } catch (error) {
      logger.warn('Cache set failed', { key, error: error.message })
    }
  }

  static async invalidate(pattern: string): Promise<void> {
    try {
      const keys = await redis.keys(pattern)
      if (keys.length > 0) {
        await redis.del(...keys)
      }
    } catch (error) {
      logger.warn('Cache invalidation failed', { pattern, error: error.message })
    }
  }

  // Cache específico para catálogos
  static async getCatalogos(tipo: string) {
    const key = `catalogos:${tipo}`
    let data = await this.get(key)
    
    if (!data) {
      data = await prisma[tipo].findMany({ where: { activo: true } })
      await this.set(key, data, 3600) // 1 hora
    }
    
    return data
  }
}
```

### **2. Database Connection Pooling**
```typescript
// src/lib/prisma/client.ts (optimizado)
import { PrismaClient } from '@prisma/client'

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined
}

export const prisma = globalForPrisma.prisma ?? new PrismaClient({
  log: process.env.NODE_ENV === 'development' 
    ? ['query', 'error', 'warn'] 
    : ['error'],
  datasources: {
    db: {
      url: process.env.DATABASE_URL
    }
  }
})

// Configuración de pool para producción
if (process.env.NODE_ENV === 'production') {
  prisma.$connect()
}

if (process.env.NODE_ENV !== 'production') {
  globalForPrisma.prisma = prisma
}

// Middleware para métricas
prisma.$use(async (params, next) => {
  const start = Date.now()
  
  try {
    const result = await next(params)
    
    dbQueryDuration
      .labels(params.action, params.model || 'unknown')
      .observe((Date.now() - start) / 1000)
    
    return result
  } catch (error) {
    loggers.database.error('Database query failed', {
      model: params.model,
      action: params.action,
      error: error.message
    })
    throw error
  }
})
```

---

## 🚨 SISTEMA DE ALERTAS

### **1. Health Checks Avanzados**
```typescript
// src/app/api/health/route.ts (mejorado)
import { NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import { redis } from '@/lib/cache/redis'

export async function GET() {
  const checks = {
    database: false,
    redis: false,
    external_apis: false
  }

  const start = Date.now()

  try {
    // Database check
    await prisma.$queryRaw`SELECT 1`
    checks.database = true
  } catch (error) {
    loggers.api.error('Database health check failed', { error: error.message })
  }

  try {
    // Redis check
    await redis.ping()
    checks.redis = true
  } catch (error) {
    loggers.api.error('Redis health check failed', { error: error.message })
  }

  const healthy = Object.values(checks).every(Boolean)
  const responseTime = Date.now() - start

  const response = {
    status: healthy ? 'healthy' : 'unhealthy',
    timestamp: new Date().toISOString(),
    version: process.env.npm_package_version || '1.0.0',
    environment: process.env.NODE_ENV,
    uptime: process.uptime(),
    responseTime,
    checks,
    memory: process.memoryUsage(),
    cpu: process.cpuUsage()
  }

  return NextResponse.json(response, {
    status: healthy ? 200 : 503
  })
}
```

### **2. Alertas Proactivas**
```typescript
// src/lib/monitoring/alerts.ts
import { logger } from '@/lib/logging/logger'

export class AlertManager {
  static async checkSystemHealth() {
    const alerts = []

    // Check database performance
    const dbMetrics = await this.getDatabaseMetrics()
    if (dbMetrics.avgResponseTime > 1000) {
      alerts.push({
        type: 'performance',
        severity: 'warning',
        message: `Database response time high: ${dbMetrics.avgResponseTime}ms`,
        metric: 'db_response_time',
        value: dbMetrics.avgResponseTime,
        threshold: 1000
      })
    }

    // Check memory usage
    const memUsage = process.memoryUsage()
    const memUsagePercent = (memUsage.heapUsed / memUsage.heapTotal) * 100
    if (memUsagePercent > 85) {
      alerts.push({
        type: 'resource',
        severity: 'critical',
        message: `High memory usage: ${memUsagePercent.toFixed(1)}%`,
        metric: 'memory_usage',
        value: memUsagePercent,
        threshold: 85
      })
    }

    // Check error rate
    const errorRate = await this.getErrorRate()
    if (errorRate > 5) {
      alerts.push({
        type: 'error_rate',
        severity: 'critical',
        message: `High error rate: ${errorRate}%`,
        metric: 'error_rate',
        value: errorRate,
        threshold: 5
      })
    }

    // Send alerts
    for (const alert of alerts) {
      await this.sendAlert(alert)
    }

    return alerts
  }

  private static async sendAlert(alert: any) {
    logger.error('System alert triggered', alert)
    
    // Integración con servicios de alertas
    if (process.env.SLACK_WEBHOOK_URL) {
      await this.sendSlackAlert(alert)
    }
    
    if (process.env.EMAIL_ALERTS_ENABLED) {
      await this.sendEmailAlert(alert)
    }
  }
}
```

---

## 📈 DASHBOARD DE MÉTRICAS

### **1. Endpoint de Métricas**
```typescript
// src/app/api/metrics/route.ts
import { NextResponse } from 'next/server'
import { register } from 'prom-client'

export async function GET() {
  const metrics = await register.metrics()
  
  return new NextResponse(metrics, {
    headers: {
      'Content-Type': register.contentType
    }
  })
}
```

### **2. Configuración Grafana**
```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - ./monitoring/grafana/dashboards:/var/lib/grafana/dashboards
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
```

---

## 🎯 MÉTRICAS DE ÉXITO

### **SLIs (Service Level Indicators):**
- **Availability:** >99.9% uptime
- **Latency:** <200ms (p95) para API calls
- **Error Rate:** <0.1% de requests fallidos
- **Throughput:** >1000 requests/min sostenidos

### **SLOs (Service Level Objectives):**
- **API Response Time:** 95% de requests <200ms
- **Database Query Time:** 95% de queries <50ms
- **System Uptime:** 99.9% mensual
- **Error Budget:** 0.1% mensual

### **Alertas Críticas:**
- **Downtime:** >1 minuto
- **High Latency:** >500ms por >2 minutos
- **Error Spike:** >5% error rate por >1 minuto
- **Resource Usage:** >90% CPU/Memory por >5 minutos

---

**Estado:** ✅ PARTE 6 completada  
**DOCUMENTO COMPLETO:** Requerimientos profesionales Next.js finalizados
