# Configuración de Vercel y Supabase

Para desplegar la aplicación en Vercel, asegúrate de configurar las siguientes variables de entorno en la configuración del proyecto en Vercel.

## Base de Datos (Supabase)

- `DATABASE_URL`: URL de conexión al Transaction Pooler (puerto 6543).
- `DIRECT_URL`: URL de conexión directa o Session Pooler (puerto 5432). Necesaria para migraciones.

## Autenticación (NextAuth.js)

- `NEXTAUTH_URL`: URL canónica de tu despliegue (ej. `https://tu-proyecto.vercel.app`).
- `NEXTAUTH_SECRET`: Clave secreta para firmar tokens. Generar con `openssl rand -base64 32`.

## Monitoreo (Sentry)

- `SENTRY_AUTH_TOKEN`: Token de autenticación de Sentry (para subir source maps).
- `SENTRY_DSN`: DSN de tu proyecto Sentry.
- `SENTRY_ORG`: Slug de tu organización en Sentry.
- `SENTRY_PROJECT`: Slug de tu proyecto en Sentry.

## Auditoría

- `AUDIT_LOG_ENABLED`: "true" (opcional, si se implementa flag).

## CI/CD

El pipeline de GitHub Actions (`.github/workflows/ci.yml`) ejecutará los tests automáticamente en cada Push y Pull Request a `main`.
