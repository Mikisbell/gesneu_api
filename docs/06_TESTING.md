# 🧪 Testing - GesNeu API

> **Última actualización**: Diciembre 2025

---

## Stack de Testing

| Tipo | Herramienta | Cobertura |
|------|-------------|-----------|
| Unit Tests | Jest | Services, validators |
| Integration Tests | Jest + Supertest | API endpoints |
| E2E Tests | Playwright | Flujos críticos |
| Security Tests | Jest | Políticas RBAC |

---

## Comandos

```bash
# Ejecutar todos los tests
npm test

# Watch mode
npm run test:watch

# Coverage
npm run test:coverage

# Solo integration
npm run test:integration

# E2E
npm run test:e2e
```

---

## Pirámide de Testing

```
        ┌───────────┐
        │   E2E     │  10% - Flujos críticos
        │ Playwright│
        ├───────────┤
        │Integration│  30% - API endpoints
        │Jest+Super │
        ├───────────┤
        │   Unit    │  60% - Services, validators
        │   Jest    │
        └───────────┘
```

---

## Ubicación de Tests

```
src/__tests__/
├── integration/
│   ├── alertas.test.ts
│   ├── catalogos.test.ts
│   ├── dashboard.test.ts
│   ├── neumaticos.test.ts
│   └── vehiculos.test.ts
├── security/
│   └── retread-policy.test.ts
├── unit/
│   └── services/
└── e2e/
    └── neumatico-lifecycle.spec.ts
```

---

## Patrones de Tests

### Test de Service con Mocking

```typescript
describe('NeumaticoService', () => {
  let service: NeumaticoService
  let mockRepository: jest.Mocked<NeumaticoRepository>

  beforeEach(() => {
    mockRepository = new NeumaticoRepository() as jest.Mocked<NeumaticoRepository>
    service = new NeumaticoService(mockRepository)
  })

  it('debe rechazar instalación de neumático no en stock', async () => {
    mockRepository.findUnique.mockResolvedValue({
      estado_actual: 'INSTALADO'
    })

    await expect(service.registrarEvento({
      tipo_evento: 'INSTALACION',
      neumatico_id: 'uuid'
    }, 'user-id')).rejects.toThrow('Solo se pueden instalar neumáticos en stock')
  })
})
```

### Test de API Endpoint

```typescript
describe('GET /api/v1/neumaticos', () => {
  it('returns paginated list', async () => {
    const res = await request(app)
      .get('/api/v1/neumaticos')
      .set('Authorization', `Bearer ${token}`);
    
    expect(res.status).toBe(200);
    expect(res.body.data).toBeInstanceOf(Array);
    expect(res.body.pagination).toBeDefined();
  });

  it('rechaza sin permisos', async () => {
    const res = await request(app)
      .get('/api/v1/neumaticos')
      .set('x-user-permissions', JSON.stringify([]));
    
    expect(res.status).toBe(403);
  });
});
```

### E2E - Ciclo de Vida Neumático

```typescript
test('ciclo: creación → instalación → desmontaje', async ({ page }) => {
  // 1. Login
  await page.goto('/auth/login')
  await page.fill('[data-testid=username]', 'admin')
  await page.fill('[data-testid=password]', 'Admin123')
  await page.click('[data-testid=login-button]')

  // 2. Crear neumático
  await page.goto('/neumaticos/nuevo')
  await page.fill('[data-testid=numero-serie]', 'E2E-TEST-001')
  await page.click('[data-testid=crear]')
  await expect(page.locator('[data-testid=success]')).toBeVisible()

  // 3. Instalar
  await page.click('[data-testid=instalar]')
  await page.selectOption('[data-testid=vehiculo]', 'ABC-123')
  await page.click('[data-testid=confirmar]')
  
  // 4. Verificar estado
  await expect(page.locator('[data-testid=estado]')).toContainText('INSTALADO')
})
```

---

## Coverage Goals

| Métrica | Objetivo | Threshold CI |
|---------|----------|--------------|
| Statements | ≥ 80% | 70% |
| Branches | ≥ 70% | 60% |
| Functions | ≥ 80% | 70% |
| Lines | ≥ 80% | 70% |

---

## Jest Config

```javascript
// jest.config.js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  coverageThreshold: {
    global: {
      branches: 60,
      functions: 70,
      lines: 70,
      statements: 70
    }
  },
  setupFilesAfterEnv: ['<rootDir>/tests/setup.ts'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1'
  }
}
```

---

## Tests Críticos

- [x] CRUD Neumáticos
- [x] Operaciones de montaje/desmontaje
- [x] Políticas de reencauche (seguridad)
- [x] Generación de alertas
- [x] Dashboard endpoints
- [x] Transacciones con rollback

---

*Ver `jest.config.js` para configuración completa.*
