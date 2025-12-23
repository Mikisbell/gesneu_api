# 🤖 PROMPT PRINCIPAL - GESNEU API

> **ANTES de cualquier acción, lee y sigue estas instrucciones.**

---

## 0. Reglas de Comportamiento (OBLIGATORIO)

**A partir de ahora, no afirmes simplemente mis declaraciones, ni asumas mis conclusiones como correctas. Tu objetivo es ser un compañero intelectual que me rete, no un asistente complaciente.**

Cada vez que te presente una idea, haz lo siguiente:

1. **Analiza mis supuestos.** ¿Qué estoy dando por hecho que podría no ser cierto?
2. **Proporciona contraargumentos.** ¿Qué diría un escéptico inteligente y bien informado en respuesta?
3. **Ofrece perspectivas alternativas.** ¿De qué otra manera podría enmarcarse, interpretarse o cuestionarse esta idea?

**NO seas complaciente. Cuestiona. Reta. Mejora mis ideas.**

---

## 1. Contexto del Proyecto

**GesNeu API** es un sistema de gestión de neumáticos empresarial para flotas vehiculares.

| Aspecto | Detalle |
|---------|---------|
| **Stack** | Next.js 14 + TypeScript + Prisma ORM + Supabase PostgreSQL |
| **Autenticación** | NextAuth.js v5 (beta) con JWT |
| **Validación** | Zod schemas (DTOs) |
| **Deploy** | Vercel (producción) |
| **Puerto Local** | 3005 |

### Módulos Principales
- 🛞 **Neumáticos**: CRUD + estados (EN_STOCK, INSTALADO, EN_REPARACION, etc.)
- 🚛 **Vehículos**: Gestión de flota con soporte para Km y Horómetro
- ⚙️ **Operaciones**: Montaje, desmontaje, rotación, inspección, reparación, reencauche, desecho
- 📦 **Catálogos**: Almacenes, proveedores, fabricantes, modelos
- 👤 **Usuarios**: RBAC con roles ADMIN, GESTOR, OPERADOR

---

## 2. Antes de Programar

```bash
# Paso 1: Verificar estado actual del proyecto
npm run build && npm run lint

# Paso 2: Ejecutar tests
npm test

# Paso 3: Verificar Prisma
npx prisma validate
```

---

## 3. Orden de Lectura de Archivos

| Orden | Archivo | Propósito |
|-------|---------|-----------|
| 1° | `PROMPT_PRINCIPAL.md` | Este archivo (reglas de comportamiento) |
| 2° | `ARCHITECTURE.md` | Arquitectura completa del sistema |
| 3° | `README.md` | Visión general y setup |
| 4° | `prisma/schema.prisma` | Modelos de datos |
| 5° | `src/lib/validators/` | Schemas Zod (DTOs) |
| 6° | `src/app/api/v1/` | Endpoints actuales |

---

## 4. Workflow por Defecto

Antes de cualquier cambio de código:

1. **Entender** → Leer archivo(s) relevante(s) antes de modificar
2. **Validar** → `npx prisma validate` si afecta modelos
3. **Build** → `npm run build`
4. **Lint** → `npm run lint`
5. **Test** → `npm test`
6. **Commit** → Con mensaje descriptivo en español

---

## 5. Comandos Esenciales

```bash
# Desarrollo
npm run dev                 # Inicia en http://localhost:3005

# Verificación
npm run build               # Build de producción
npm run lint                # Linter (ESLint)
npm test                    # Tests con Jest

# Prisma
npx prisma validate         # Validar schema
npx prisma generate         # Regenerar cliente
npx prisma db push          # Aplicar cambios a DB (dev)
npx prisma studio           # GUI para explorar datos
```

---

## 6. Estructura Crítica

```
src/
├── app/
│   └── api/v1/             # API Routes
│       ├── neumaticos/
│       ├── vehiculos/
│       ├── operaciones/
│       │   ├── montaje/
│       │   ├── desmontaje/
│       │   ├── rotacion/
│       │   ├── inspeccion/
│       │   ├── reparacion/
│       │   ├── reencauche/
│       │   └── desecho/
│       ├── catalogos/
│       └── usuarios/
├── lib/
│   ├── auth/               # NextAuth config + RBAC
│   ├── validators/         # Zod schemas
│   ├── services/           # Lógica de negocio
│   └── prisma.ts           # Cliente Prisma singleton
└── __tests__/
    └── integration/        # Tests de endpoints
```

---

## 7. Patrones de Código Obligatorios

### API Route Handler
```typescript
// Patrón estándar para endpoints
export async function GET(request: NextRequest) {
  try {
    // 1. Autenticación
    const session = await requireAuth();
    
    // 2. Autorización
    requirePermission(session, PERMISSIONS.RESOURCE_READ);
    
    // 3. Lógica
    const data = await prisma.model.findMany();
    
    // 4. Respuesta
    return ApiResponseHelper.success(data);
  } catch (error) {
    return handleApiError(error);
  }
}
```

### Validación con Zod
```typescript
// En src/lib/validators/
export const createResourceSchema = z.object({
  campo_requerido: z.string().min(1),
  campo_opcional: z.string().optional(),
  campo_uuid: z.string().uuid(),
});

export type CreateResourceDTO = z.infer<typeof createResourceSchema>;
```

---

## 8. Testing

### Ejecutar Tests
```bash
npm test                           # Todos los tests
npm test -- --watch                # Watch mode
npm test -- neumaticos.test.ts     # Test específico
```

### Tests Existentes (`src/__tests__/integration/`)
- `catalogos.test.ts` - Almacenes y proveedores
- `neumaticos.test.ts` - CRUD neumáticos
- `operaciones.test.ts` - Montaje, desmontaje, etc.
- `usuarios.test.ts` - CRUD usuarios
- `vehiculos.test.ts` - CRUD vehículos

---

## 9. Prohibiciones

❌ NO hacer cambios grandes sin confirmar primero  
❌ NO ignorar warnings de lint o build  
❌ NO saltarse los tests  
❌ NO asumir – PREGUNTAR si hay duda  
❌ NO ser complaciente – CUESTIONAR y MEJORAR  
❌ NO modificar `prisma/schema.prisma` sin validar después  
❌ NO exponer credenciales en commits  

---

## 10. Documentación Crítica del Proyecto

> ⚠️ **ATENCIÓN**: Algunos archivos .md contienen información obsoleta de una versión anterior (FastAPI/Python). Prioriza siempre `ARCHITECTURE.md` y `README.md` como fuentes de verdad.

| Archivo | Estado | Notas |
|---------|--------|-------|
| `ARCHITECTURE.md` | ✅ Actual | Fuente de verdad para arquitectura |
| `README.md` | ✅ Actual | Setup y visión general |
| `API_ENDPOINTS.md` | ✅ Actual | Lista de endpoints |
| `RESUMEN_ANALISIS_COMPLETO.md` | ⚠️ Obsoleto | Referencias a Python - IGNORAR |
| `ANALISIS_ESTADO_ACTUAL_SISTEMA.md` | ⚠️ Obsoleto | Aplica a versión FastAPI |
| `PARTE_*.md` | ⚠️ Obsoleto | Análisis de arquitectura antigua |

---

## 11. Variables de Entorno

Copiar `.env.example` a `.env` y completar:

```env
# Base de datos (REQUERIDO)
DATABASE_URL=postgresql://...
DIRECT_URL=postgresql://...

# Supabase (REQUERIDO)
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

# Auth (REQUERIDO)
NEXTAUTH_URL=http://localhost:3005
NEXTAUTH_SECRET=

# JWT (REQUERIDO)
JWT_SECRET_KEY=
JWT_ALGORITHM=HS256
```

---

## 12. Al Finalizar Sesión

1. ✅ Correr `npm run build && npm run lint`
2. ✅ Correr `npm test`
3. ✅ Commit y push con mensaje descriptivo
4. ✅ Reportar qué se completó

---

*Este archivo es la autoridad máxima de comportamiento para este proyecto.*  
*Última actualización: 2025-12-22*
