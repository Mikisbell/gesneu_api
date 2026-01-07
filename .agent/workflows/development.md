---
description: Loop de desarrollo continuo - usar cuando digan "Lee PROMPT_PRINCIPAL.md..."
---

# /development - Workflow de Desarrollo Continuo

// turbo-all

**Trigger**: Cuando el usuario diga: "Lee PROMPT_PRINCIPAL.md, corre npm run docs:audit, y continúa con la siguiente tarea del ROADMAP 2026"

---

## FASE 1: Gobernanza (OBLIGATORIO)

// turbo
1. Leer documentos de gobernanza:
```bash
# Analizar reglas de comportamiento y restricciones técnicas
cat PROMPT_PRINCIPAL.md
cat AGENT.md
```

// turbo
2. Auditar documentación:
```bash
npm run docs:audit
```
**Verificar**: 13/13 archivos pasando.

---

## FASE 2: Estado Actual (OBLIGATORIO)

// turbo
3. Estado de base de datos:
```bash
npx prisma migrate status
npx prisma validate
```

// turbo
4. Estado del código:
```bash
npm run build
npm run lint
npm test
```

5. Revisar ROADMAP.md e identificar siguiente tarea con estado 📋 o ⏳

---

## FASE 3: Ejecutar Tarea

6. Planificar:
   - Consultar docs relevantes en `/docs/`
   - Identificar archivos a modificar

7. Implementar:
   - Si afecta modelos → `prisma/schema.prisma`
   - Si nuevo endpoint → `src/app/api/v1/[modulo]/route.ts`
   - Si validación → `src/lib/validators/[modulo].ts`
   - Si lógica compleja → `src/lib/services/[modulo].service.ts`
   - Si UI → `src/components/` o `src/app/`

8. Si modificaste Prisma:
```bash
npx prisma validate
npx prisma generate
```

---

## FASE 4: Verificar y Documentar

// turbo
9. Verificación completa:
```bash
npm run build && npm run lint
npm test
npm run docs:audit
```

10. Actualizar documentación según lo afectado:
    - Arquitectura → `docs/01_ARQUITECTURA.md`
    - Modelo negocio → `docs/02_MODELO_NEGOCIO.md`
    - API → `docs/03_API_REFERENCE.md`
    - BD → `docs/04_BASE_DATOS.md`
    - Seguridad → `docs/05_SEGURIDAD.md`
    - Testing → `docs/06_TESTING.md`
    - Deploy → `docs/07_DEPLOY.md`

11. Sugerir mejoras si se detectan:
    - Patrones repetidos → Abstraer
    - Deuda técnica → Documentar
    - Optimizaciones → Proponer

---

## FASE 5: Marcar Progreso

12. Actualizar ROADMAP.md:
    - `📋` → `⏳` (en progreso)
    - `⏳` → `✅` (completada)

13. Reportar al usuario:
    - Qué se completó
    - Qué docs se actualizaron
    - Sugerencias de mejora
    - Siguiente tarea recomendada

---

## LOOP

14. Preguntar: "¿Continuamos con la siguiente tarea del ROADMAP?"

---

## Diagrama del Loop

```
┌─────────────────────────────────────────────────────────┐
│  1. LEER DOCS ──► 2. ESTADO BD/CÓDIGO ──► 3. EJECUTAR  │
│       │                                        │        │
│       │         5. MARCAR ◄── 4. VERIFICAR ◄───┘        │
│       │              │                                  │
│       └─────────◄── LOOP ──────────────────────────────┘
└─────────────────────────────────────────────────────────┘
```
