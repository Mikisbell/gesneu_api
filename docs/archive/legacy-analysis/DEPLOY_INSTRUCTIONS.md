# 🚀 Guía de Despliegue en Vercel

Sigue estos pasos detallados para poner tu aplicación en producción.

## Opción A: Despliegue desde el Dashboard (Recomendado)

Esta opción es la más visual y fácil para configurar las variables de entorno.

1. **Ve a Vercel:** Abre [https://vercel.com/new](https://vercel.com/new) en tu navegador.
2. **Importar Repositorio:**
    * Busca el repositorio `gesneu_api` en la lista (asegúrate de haber conectado tu cuenta de GitHub).
    * Haz clic en **"Import"**.
3. **Configurar Proyecto:**
    * **Framework Preset:** Next.js (debería detectarse automáticamente).
    * **Root Directory:** `./` (déjalo como está).
4. **Variables de Entorno (Environment Variables):**
    * Haz clic en la sección desplegable **"Environment Variables"**.
    * Agrega las siguientes variables (copia y pega los valores exactos):

    | Nombre (Key) | Valor (Value) |
    |--------------|---------------|
    | `DATABASE_URL` | `postgresql://postgres:M1k1sB3llR1v3ra@db.mdefuvnibcwvnwubksun.supabase.co:5432/postgres` |
    | `NEXTAUTH_SECRET` | `nextauth_gesneu_2024_super_secret_key` |
    | `NEXTAUTH_URL` | `https://gesneu-api.vercel.app` (o la URL que Vercel te asigne después) |
    | `APP_SECRET_KEY` | `gesneu_secret_key_2024_super_secure_mikisbell_production` |
    | `JWT_SECRET_KEY` | `jwt_gesneu_2024_very_secure_key_mikisbell_production_token` |

5. **Desplegar:**
    * Haz clic en **"Deploy"**.
    * Espera a que termine el proceso de construcción (Build).

---

## Opción B: Despliegue desde Terminal (CLI)

Si prefieres usar la terminal, sigue estos pasos:

1. **Iniciar sesión (si no lo has hecho):**

    ```bash
    npx vercel login
    ```

    * Sigue las instrucciones para autenticarte con tu cuenta (GitHub/Email).

2. **Iniciar Despliegue:**

    ```bash
    npx vercel
    ```

3. **Responder Preguntas:**
    * `Set up and deploy "~/gesneu_api"?` → **y** (Yes)
    * `Which scope do you want to deploy to?` → Selecciona tu usuario/equipo.
    * `Link to existing project?` → **n** (No, a menos que ya lo hayas creado en el dashboard).
    * `What’s your project’s name?` → `gesneu-api` (o presiona Enter).
    * `In which directory is your code located?` → `./` (Enter).
    * `Want to modify these settings?` → **n** (No).

4. **Configurar Variables (Importante):**
    * Una vez creado el proyecto, ve al dashboard de Vercel (el enlace que te da la terminal) para agregar las variables de entorno mencionadas en la **Opción A**.
    * O usa el comando:

        ```bash
        npx vercel env add DATABASE_URL
        ```

        (Te pedirá el valor, pega la URL de conexión de Supabase Cloud).

5. **Despliegue a Producción:**

    ```bash
    npx vercel --prod
    ```

---

## ✅ Verificación

Una vez desplegado:

1. Obtén la URL de tu proyecto (ej. `https://gesneu-api.vercel.app`).
2. Prueba el endpoint de salud: `https://gesneu-api.vercel.app/api/health`.
3. Deberías recibir una respuesta JSON con el estado "healthy" (o "unhealthy" si la BD falla, pero responderá).
