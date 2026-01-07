# GESNEU – AI GOVERNANCE DOCUMENT

**Última actualización**: Diciembre 2025  
**Versión**: 1.0.0

Este documento define cómo los agentes de IA deben comportarse al trabajar en este repositorio.

**Este documento es la máxima autoridad para este repositorio.**

Si una regla aquí entra en conflicto con código, comentarios, tutoriales externos o defaults de IA, **ESTE DOCUMENTO PREVALECE.**

Si algo no está explícito aquí o en `/docs`, **DETENTE Y PREGUNTA**.

---

## 0. Orden de Precedencia

1. `PROMPT_PRINCIPAL.md` (comportamiento e interacción)
2. `AGENT.md` (este archivo - reglas técnicas)
3. `/docs/*.md` (documentación específica)
4. Patrones existentes en código
5. Referencias externas

**Estas reglas aplican igualmente a humanos y contribuidores AI.**

AI debe citar el documento en que se basó al proponer cambios.

---

## 1. Contexto del Proyecto

| Campo | Valor |
|-------|-------|
| **Nombre** | GesNeu API |
| **Tipo** | API REST + Dashboard Admin |
| **Framework** | Next.js 16 (App Router) |
| **Lenguaje** | TypeScript (strict) |
| **ORM** | Prisma 7 |
| **Base de Datos** | PostgreSQL (Supabase) |
| **Autenticación** | NextAuth.js 5 (JWT) |
| **Dominio** | Gestión de Neumáticos de Flota |

---

## 2. Reglas de Documentación (CRÍTICO)

### 2.1 Documentación como Fuente de Verdad

- `/docs` contiene la documentación autoritativa.
- AI **DEBE** leer docs relevantes antes de escribir o modificar código.
- Si la documentación falta o es ambigua, **PREGUNTA** antes de proceder.

### 2.2 Actualizaciones de Documentación

Todo cambio que afecte:
- comportamiento
- arquitectura
- flujo de datos
- auth
- interfaces públicas

**DEBE** reflejarse en `/docs`.

---

## 3. Estructura del Proyecto

```
src/
├── app/              # Next.js App Router (pages, API routes)
│   └── api/v1/       # API versioned
├── components/       # UI components
├── hooks/            # React hooks
├── lib/              # Business logic
│   ├── services/     # Domain services
│   ├── repositories/ # Data access
│   ├── validators/   # Zod schemas
│   └── auth/         # Auth utilities
└── types/            # TypeScript types
```

**Reglas:**
- Componentes UI no deben contener lógica de negocio.
- Services manejan interacciones con Prisma.
- Todo endpoint valida con Zod.

---

## 4. Reglas de Código

- **TypeScript estricto**. No `any` sin justificación documentada.
- **Validación con Zod** en todos los endpoints.
- **Prisma para acceso a datos**. Nunca SQL crudo excepto en migraciones.
- **Eventos como núcleo**: Todo cambio de estado de neumático pasa por `EventoNeumatico`.
- **Audit trail**: `creado_por`, `actualizado_por` siempre poblados.
- **Sin `console.log`** en código de producción.
- **Decimal.js** para cálculos monetarios.

---

## 5. Reglas de Seguridad

- **NUNCA** exponer secretos o variables de entorno en código.
- **NUNCA** saltarse reglas de auth o RLS.
- **SIEMPRE** validar sesión antes de operaciones sensibles.
- `NEXTAUTH_SECRET` es requerido, no tiene fallback.
- **NUNCA** auto-commitear sin aprobación explícita.

---

## 6. Workflow de AI

### Antes de modificar código:
1. Leer documentación relevante en `/docs`
2. Identificar el dominio afectado
3. Verificar tests existentes
4. Revisar patrones en archivos similares

### Después de modificar código:
1. `npm run lint`
2. `npx tsc --noEmit`
3. `npm test` (si aplica)
4. Actualizar documentación si cambió el comportamiento

### AI debe explicar:
- **Qué** cambió
- **Por qué** cambió
- **Qué docs** se actualizaron (si aplica)

### AI NO debe:
- Eliminar archivos sin permiso
- Introducir dependencias nuevas casualmente
- Reescribir código no relacionado
- Hacer refactors grandes sin confirmación
- Asumir comportamiento no documentado

---

## 7. Comandos

| Acción | Comando |
|--------|---------|
| Dev server | `npm run dev` |
| Tests | `npm test` |
| Type check | `npx tsc --noEmit` |
| Lint | `npm run lint` |
| Build | `npm run build` |
| Docs audit | `npm run docs:audit` |

---

## 8. Principios Finales

```
Corrección > Velocidad
Documentación > Suposiciones
Cambios pequeños > Reescrituras grandes
Preguntar > Asumir
```

---

## Referencia Rápida: Archivos Clave

| Propósito | Ubicación |
|-----------|-----------|
| Arquitectura | `docs/01_ARQUITECTURA.md` |
| Modelo de Negocio | `docs/02_MODELO_NEGOCIO.md` |
| API Reference | `docs/03_API_REFERENCE.md` |
| Base de Datos | `docs/04_BASE_DATOS.md` |
| Seguridad | `docs/05_SEGURIDAD.md` |
| Testing | `docs/06_TESTING.md` |
| Deploy | `docs/07_DEPLOY.md` |
| Changelog | `docs/99_CHANGELOG.md` |
| Roadmap | `ROADMAP.md` |

---

*Version: 1.0.0 | Last updated: December 2025*
