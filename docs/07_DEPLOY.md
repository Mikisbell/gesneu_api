# 🚀 Deploy - GesNeu API

> **Última actualización**: Diciembre 2025

---

## Entornos

| Entorno | URL | Provider |
|---------|-----|----------|
| Producción | gesneu-api.vercel.app | Vercel |
| Base de Datos | Supabase us-west-2 | Supabase |

---

## Variables de Entorno

### Requeridas

```env
# Base de datos
DATABASE_URL=postgresql://...
DIRECT_URL=postgresql://...

# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# Auth (SIN FALLBACK)
NEXTAUTH_URL=https://tu-dominio.com
NEXTAUTH_SECRET=<generado>

# JWT
JWT_SECRET_KEY=<generado>
JWT_ALGORITHM=HS256
```

### Opcionales

```env
# Email
RESEND_API_KEY=re_xxx

# Sentry
SENTRY_DSN=https://xxx@sentry.io/xxx

# Redis (rate limiting)
REDIS_URL=redis://host:6379

# Performance
DATABASE_POOL_SIZE=10
DATABASE_TIMEOUT=30000
```

---

## Deploy a Vercel

```bash
# Instalar CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

### Configuración en Vercel Dashboard

1. Agregar variables de entorno
2. Configurar dominio personalizado
3. Habilitar Edge Functions (opcional)

---

## SLIs / SLOs

### Service Level Indicators (Qué medimos)

| Indicador | Objetivo | Crítico |
|-----------|----------|---------|
| Uptime | 99.9% | <99% alert |
| API Response Time (p95) | <200ms | >500ms alert |
| Database Query Time (p95) | <50ms | >200ms alert |
| Error Rate | <0.1% | >5% alert |

### Objetivos de Nivel de Servicio

```yaml
availability:
  monthly_uptime: 99.9%
  
latency:
  p95: 200ms
  p99: 500ms
  
throughput:
  sustained: 1000 req/min
  peak: 2000 req/min

error_budget:
  monthly: 0.1%  # ~43 minutos de downtime permitido
```

---

## Health Checks

### Endpoint `/api/health`

```json
{
  "status": "healthy",
  "timestamp": "2025-12-25T20:00:00Z",
  "version": "1.0.0",
  "checks": {
    "database": true,
    "redis": true
  },
  "uptime": 86400,
  "responseTime": 15
}
```

### Implementación Multi-Servicio

```typescript
export async function GET() {
  const checks = {
    database: false,
    redis: false
  }

  try {
    await prisma.$queryRaw`SELECT 1`
    checks.database = true
  } catch {}

  try {
    await redis.ping()
    checks.redis = true
  } catch {}

  const healthy = Object.values(checks).every(Boolean)
  return Response.json(
    { status: healthy ? 'healthy' : 'unhealthy', checks },
    { status: healthy ? 200 : 503 }
  )
}
```

---

## Logging Estructurado

```typescript
// Winston config para producción
const logger = winston.createLogger({
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'logs/error.log', level: 'error' })
  ]
})

// Uso
logger.info('Evento registrado', {
  correlationId: 'uuid',
  userId: 'uuid',
  tipoEvento: 'INSTALACION',
  duration: 150
})
```

---

## Deploy con Docker

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
EXPOSE 3005
CMD ["npm", "start"]
```

```bash
docker build -t gesneu-api .
docker run -p 3005:3005 --env-file .env gesneu-api
```

---

## Migraciones en Producción

```bash
# Aplicar migraciones pendientes
npx prisma migrate deploy

# Generar cliente
npx prisma generate
```

**⚠️ NUNCA usar `migrate dev` en producción.**

---

## Alertas

| Condición | Severidad | Acción |
|-----------|-----------|--------|
| Downtime >1 min | CRITICAL | Página + Slack |
| Latency >500ms x 2min | WARNING | Slack |
| Error rate >5% x 1min | CRITICAL | Página + Slack |
| Memory >90% x 5min | WARNING | Slack |

---

## Monitoreo

- **Logs**: Vercel Dashboard → Logs
- **Errores**: Sentry (si configurado)
- **DB**: Supabase Dashboard → Logs
- **Métricas**: Prometheus + Grafana (opcional)

---

*Ver `vercel.json` para configuración de headers de seguridad.*
