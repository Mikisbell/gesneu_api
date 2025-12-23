---
description: Workflow para ejecutar y crear tests
---

# Testing Workflow

## Ejecutar Todos los Tests
// turbo
1. Correr suite completa:
```bash
npm test
```

## Ejecutar Test Específico
2. Por archivo:
```bash
npm test -- neumaticos.test.ts
npm test -- vehiculos.test.ts
npm test -- operaciones.test.ts
npm test -- catalogos.test.ts
npm test -- usuarios.test.ts
```

## Watch Mode (Desarrollo)
3. Tests en modo interactivo:
```bash
npm test -- --watch
```

## Crear Nuevo Test

4. Crear archivo en `src/__tests__/integration/[modulo].test.ts`

5. Estructura base:
```typescript
import { NextRequest } from 'next/server';
import { GET, POST } from '@/app/api/v1/[modulo]/route';
import { createMockSession } from '../helpers/auth-helpers';
import { cleanupTestData, createTestData } from '../helpers/database-helpers';

describe('[Módulo] API', () => {
  beforeEach(async () => {
    // Setup test data
  });

  afterEach(async () => {
    // Cleanup
  });

  describe('GET /api/v1/[modulo]', () => {
    it('should return list of items', async () => {
      const request = new NextRequest('http://localhost:3005/api/v1/[modulo]');
      const response = await GET(request);
      expect(response.status).toBe(200);
    });
  });
});
```

## Helpers Disponibles
- `src/__tests__/helpers/auth-helpers.ts` - Mocks de autenticación
- `src/__tests__/helpers/database-helpers.ts` - Setup/cleanup de datos

## Notas
- Tests usan Jest + Testing Library
- Cada test debe limpiar sus datos
- Mockear sesiones para probar autorización
