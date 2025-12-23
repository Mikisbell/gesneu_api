---
description: Workflow para verificar estado del proyecto antes de empezar
---

# Verificación Rápida del Proyecto

## Checks Rápidos
// turbo-all

1. Estado de build:
```bash
npm run build
```

2. Linter:
```bash
npm run lint
```

3. Tests:
```bash
npm test
```

4. Prisma Client actualizado:
```bash
npx prisma generate
```

5. Schema válido:
```bash
npx prisma validate
```

## Interpretación de Resultados

### ✅ Todo verde
- Puedes empezar a desarrollar normalmente

### ❌ Build falla
- Revisar errores de TypeScript
- Verificar imports faltantes
- Correr `npx prisma generate` si hay errores de tipos Prisma

### ❌ Lint falla
- Corregir errores de estilo antes de continuar
- Usar `npm run lint -- --fix` para auto-corregir algunos

### ❌ Tests fallan
- Revisar qué test específico falla
- Puede indicar código roto que necesita atención

### ❌ Prisma falla
- Verificar que `DATABASE_URL` está configurado en `.env`
- Correr `npx prisma generate` después de cambios al schema
