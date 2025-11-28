# Guía de Despliegue en Vercel - GesNeu API

**Última actualización:** 2025-11-28 09:36 AM (UTC-5)  
**Versión:** 1.0  
**Tiempo estimado:** 1-2 horas

---

## Prerequisitos

Antes de comenzar, asegúrate de tener:

- ✅ Cuenta en [Vercel](https://vercel.com)
- ✅ Repositorio en GitHub con acceso
- ✅ Base de datos Supabase configurada
- ✅ Cuenta en [Sentry](https://sentry.io) (opcional)
- ✅ Tests pasando localmente (85/85)

---

## Paso 1: Preparación del Proyecto

### 1.1 Verificar build local

```bash
npm run build
```

**Resultado esperado:** Build exitoso sin errores.

### 1.2 Crear `.env.example`

Crea un archivo con las variables necesarias (sin valores sensibles):

```bash
# Database
DATABASE_URL=
DIRECT_URL=

# Auth
NEXTAUTH_URL=
NEXTAUTH_SECRET=
JWT_SECRET_KEY=

# Supabase
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

# Monitoring (opcional)
SENTRY_DSN=
```

### 1.3 Verificar `next.config.js`

Asegúrate de que esté optimizado para producción:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Desactivar telemetría si prefieres
  // telemetry: { enabled: false },
  
  // Headers de seguridad
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'X-Frame-Options', value: 'DENY' },
          { key: 'X-XSS-Protection', value: '1; mode=block' },
        ],
      },
    ];
  },
};

export default nextConfig;
```

---

## Paso 2: Deploy en Vercel

### Opción A: Deploy via Dashboard (Recomendado)

1. **Ir a [Vercel Dashboard](https://vercel.com/new)**

2. **Import Git Repository**
   - Conecta tu cuenta de GitHub si no está conectada
   - Selecciona el repositorio `Mikisbell/gesneu_api`
   - Click en "Import"

3. **Configure Project**
   - **Project Name:** `gesneu-api` (o el nombre que prefieras)
   - **Framework Preset:** Next.js (auto-detectado)
   - **Root Directory:** `./`
   - **Build Command:** `npm run build` (default)
   - **Output Directory:** `.next` (default)
   - **Install Command:** `npm install` (default)

4. **Environment Variables** (¡IMPORTANTE!)

   Click en "Environment Variables" y agrega:

   ```
   DATABASE_URL=postgres://postgres.hwefuosgihhgzhjqajnx:M1k1sB3ll.$@aws-0-us-west-2.pooler.supabase.com:6543/postgres?pgbouncer=true
   
   DIRECT_URL=postgresql://postgres:M1k1sB3ll.$@db.hwefuosgihhgzhjqajnx.supabase.co:5432/postgres
   
   NEXTAUTH_URL=https://tu-proyecto.vercel.app
   
   NEXTAUTH_SECRET=<GENERAR NUEVO - ver abajo>
   
   JWT_SECRET_KEY=<GENERAR NUEVO - ver abajo>
   
   NEXT_PUBLIC_SUPABASE_URL=https://hwefuosgihhgzhjqajnx.supabase.co
   
   NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   
   SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   
   SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx (opcional)
   ```

   **Generar secrets:**

   ```bash
   # En tu terminal local
   openssl rand -base64 32
   ```

5. **Deploy**
   - Click en "Deploy"
   - Espera 2-3 minutos

---

### Opción B: Deploy via CLI

```bash
# Instalar Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel

# Seguir prompts interactivos
```

---

## Paso 3: Configuración Post-Deploy

### 3.1 Actualizar NEXTAUTH_URL

Una vez deployado, Vercel te dará una URL como:

```
https://gesneu-api-xxx.vercel.app
```

**Actualiza la variable de entorno:**

1. Ve a tu proyecto en Vercel Dashboard
2. Settings → Environment Variables
3. Edita `NEXTAUTH_URL` con la URL de Vercel
4. Redeploy: Deployments → … → Redeploy

### 3.2 Configurar Dominio Custom (Opcional)

Si tienes un dominio propio:

1. **Vercel Dashboard** → Tu proyecto → Settings → Domains
2. **Add Domain:** `api.tudominio.com`
3. **Configurar DNS:**
   - Tipo: `CNAME`
   - Name: `api`
   - Value: `cname.vercel-dns.com`
4. **Esperar propagación** (5-60 min)
5. **Actualizar `NEXTAUTH_URL`** al dominio custom

### 3.3 Configurar CORS (Si usarás frontend externo)

En `next.config.js`:

```javascript
async headers() {
  return [
    {
      source: '/api/:path*',
      headers: [
        { 
          key: 'Access-Control-Allow-Origin', 
          value: 'https://tu-frontend.com' // o '*' para desarrollo
        },
        { 
          key: 'Access-Control-Allow-Methods', 
          value: 'GET, POST, PUT, DELETE, OPTIONS' 
        },
        { 
          key: 'Access-Control-Allow-Headers', 
          value: 'Content-Type, Authorization' 
        },
      ],
    },
  ];
},
```

---

## Paso 4: Verificación

### 4.1 Probar Endpoints

**Swagger UI:**

```
https://tu-proyecto.vercel.app/api/docs
```

**Health Check (crear endpoint primero):**

```
https://tu-proyecto.vercel.app/api/health
```

**Test con cURL:**

```bash
# Neumaticos (sin auth - debería dar 401)
curl https://tu-proyecto.vercel.app/api/v1/neumaticos

# Respuesta esperada:
# {"success":false,"error":"No autorizado","timestamp":"..."}
```

### 4.2 Verificar Logs

**Vercel Dashboard:**

- Tu proyecto → Deployments → Latest → View Function Logs
- Buscar errores o warnings

**Sentry (si configuraste):**

- Dashboard de Sentry → Ver errores capturados

### 4.3 Probar Autenticación

```bash
# POST login (necesitarás crear usuario primero con seed o directamente en DB)
curl -X POST https://tu-proyecto.vercel.app/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"..."}'
```

---

## Paso 5: Monitoreo

### 5.1 Vercel Analytics

- Automáticamente habilitado
- Ver métricas en Dashboard → Analytics

### 5.2 Vercel Speed Insights

```bash
npm install @vercel/speed-insights
```

```typescript
// app/layout.tsx
import { SpeedInsights } from '@vercel/speed-insights/next';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <SpeedInsights />
      </body>
    </html>
  );
}
```

### 5.3 Configurar Alertas en Sentry

En Sentry Dashboard:

1. Settings → Alerts
2. Crear regla: "Error rate > 10/min"
3. Notificaciones por email

---

## Troubleshooting

### Error: "Build failed"

```bash
# Verificar build local primero
npm run build

# Ver logs detallados en Vercel
```

### Error: "Cannot connect to database"

- Verificar `DATABASE_URL` y `DIRECT_URL`
- Asegurar que Supabase permita conexiones desde Vercel
- Network restrictions en Supabase → permitir todas las IPs

### Error: "NextAuth configuration error"

- Verificar `NEXTAUTH_URL` apunta a la URL de Vercel
- Verificar `NEXTAUTH_SECRET` está configurado
- Redeploy después de cambiar variables

### Lentitud en API

- Usar connection pooling (ya configurado)
- Verificar que usas `DATABASE_URL` (puerto 6543) no `DIRECT_URL`
- Considerar plan superior de Supabase si hay muchas conexiones

---

## Mejores Prácticas

### 1. Variables de Entorno

- ✅ Nunca commitear `.env` al repositorio
- ✅ Usar `.env.example` sin valores reales
- ✅ Rotar secrets regularmente
- ✅ Diferentes secrets para staging/production

### 2. Deployments

- ✅ Usar GitHub integration (auto-deploy en push)
- ✅ Crear branch `staging` para testing
- ✅ Usar preview deploys para PRs
- ✅ Proteger branch `main` en GitHub

### 3. Seguridad

- ✅ HTTPS siempre (automático en Vercel)
- ✅ Headers de seguridad configurados
- ✅ CORS restrictivo en producción
- ✅ Rate limiting (implementar en Fase 8)

---

## Configuración Avanzada

### Serverless Functions Timeout

Por defecto: 10s (hobby), 60s (pro)

En `vercel.json`:

```json
{
  "functions": {
    "api/**/*.ts": {
      "maxDuration": 10
    }
  }
}
```

### Edge Config (Opcional)

Para feature flags y configuración dinámica:

```bash
vercel env add EDGE_CONFIG
```

---

## Rollback

Si algo sale mal:

1. **Vercel Dashboard** → Deployments
2. Encuentra el deployment anterior exitoso
3. Click en **… → Promote to Production**

O via CLI:

```bash
vercel rollback
```

---

## Próximos Pasos

Una vez deployado exitosamente:

- [ ] Marcar tareas de Fase 5 como completadas
- [ ] Comenzar Fase 6: Testing y QA
- [ ] Crear colección de Thunder Client/Postman
- [ ] Documentar casos de uso

---

## Recursos

- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [Supabase + Vercel](https://supabase.com/docs/guides/hosting/vercel)
- [NextAuth Deployment](https://next-auth.js.org/deployment)

---

**¿Problemas?** Revisa los logs en Vercel y Sentry, o consulta la documentación oficial.
