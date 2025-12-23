---
description: Workflow estándar para desarrollo de features
---

# Desarrollo de Nuevas Features

## Pre-requisitos
// turbo
1. Verificar que el build pasa:
```bash
npm run build
```

// turbo
2. Verificar lint:
```bash
npm run lint
```

## Desarrollo

3. Crear/modificar archivos según el feature:
   - Si afecta modelos → `prisma/schema.prisma`
   - Si nuevo endpoint → `src/app/api/v1/[modulo]/route.ts`
   - Si validación → `src/lib/validators/[modulo].ts`
   - Si lógica compleja → `src/lib/services/[modulo].service.ts`

4. Si modificaste Prisma schema:
```bash
npx prisma validate
npx prisma generate
```

5. Agregar tests en `src/__tests__/integration/`

## Verificación
// turbo
6. Ejecutar tests:
```bash
npm test
```

// turbo
7. Build final:
```bash
npm run build
```

## Commit
8. Commit con mensaje descriptivo:
```bash
git add .
git commit -m "feat: [descripción del cambio]"
```

## Notas
- SIEMPRE validar Prisma después de cambios al schema
- Los tests de integración mockean la DB con helpers
- Seguir patrones en `PROMPT_PRINCIPAL.md`
