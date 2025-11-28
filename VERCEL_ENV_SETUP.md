# Configuración de Variables de Entorno para Vercel

## ⚠️ PROBLEMA ACTUAL

**El login funciona en localhost pero NO en Vercel (<https://gesneu.vercel.app>)**

## 🔧 SOLUCIÓN: Configurar Variables de Entorno en Vercel

### Variables Requeridas en Vercel Dashboard

Ve a: **Vercel Dashboard → Tu Proyecto → Settings → Environment Variables**

Agrega las siguientes variables:

#### 1. Autenticación (NextAuth)

```bash
NEXTAUTH_URL=https://gesneu.vercel.app
NEXTAUTH_SECRET=super-secret-dev-key-change-in-prod
```

#### 2. Base de Datos (Supabase)

```bash
DATABASE_URL=postgres://postgres.hwefuosgihhgzhjqajnx:M1k1sB3ll.$@aws-0-us-west-2.pooler.supabase.com:5432/postgres

DIRECT_URL=postgres://postgres.hwefuosgihhgzhjqajnx:M1k1sB3ll.$@aws-0-us-west-2.pooler.supabase.com:5432/postgres
```

#### 3. Supabase API

```bash
NEXT_PUBLIC_SUPABASE_URL=https://hwefuosgihhgzhjqajnx.supabase.co

NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh3ZWZ1b3NnaWhoZ3poanFham54Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQyNjU4MjcsImV4cCI6MjA3OTg0MTgyN30.d-U4XcXadJpSNYJZhx-7djh5KfCGB_lhFXBqBmXGFhQ

SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh3ZWZ1b3NnaWhoZ3poanFham54Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDI2NTgyNywiZXhwIjoyMDc5ODQxODI3fQ.4ehcA_qr_uAd-G9NRRfcF8nebscjjIZZF2Ck3dHoxtI
```

#### 4. JWT y API

```bash
JWT_SECRET_KEY=super-secret-jwt-key-change-in-prod
JWT_ALGORITHM=HS256
API_V1_STR=/api/v1
PROJECT_NAME=GES_NEU API
```

## 🚨 VARIABLES CRÍTICAS

Las MÁS IMPORTANTES para que funcione el login:

1. **NEXTAUTH_URL** → Debe ser `https://gesneu.vercel.app` (NO localhost)
2. **NEXTAUTH_SECRET** → Debe coincidir con el local
3. **DATABASE_URL** → Conexión a Supabase

## 📋 Checklist de Verificación

- [ ] Todas las variables agregadas en Vercel
- [ ] NEXTAUTH_URL es la URL de producción (<https://gesneu.vercel.app>)
- [ ] Re-deploy después de agregar variables
- [ ] Verificar logs de Vercel para errores de conexión

## 🔄 Después de Configurar

1. **Redeploy** el proyecto en Vercel
2. Espera que termine el deployment
3. Intenta login en <https://gesneu.vercel.app/login>
4. Si falla, revisa los **Runtime Logs** en Vercel

## 🆘 Si Sigue Fallando

Revisa los logs en Vercel Dashboard → Deployments → [último deploy] → Runtime Logs
Busca emojis: 🔐 🔍 ✅ ❌
