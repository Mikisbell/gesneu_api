# PARTE 5: TESTING Y CALIDAD
## Unit Tests + Integration Tests + E2E + CI/CD

**Fecha:** 14 de Noviembre, 2025  
**Versión:** 1.0  
**Dependencias:** PARTE 1-4 completadas

---

## 🧪 ESTRATEGIA DE TESTING

### **1. Pirámide de Testing**
```
E2E Tests (10%)
├── Flujos críticos de usuario
├── Testing de integración completa
└── Cypress/Playwright

Integration Tests (30%)
├── API endpoints completos
├── Base de datos + servicios
└── Jest + Supertest

Unit Tests (60%)
├── Services + Repositories
├── Validators + Utils
└── Jest + Mocking
```

### **2. Configuración Jest**
```typescript
// jest.config.js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src', '<rootDir>/tests'],
  testMatch: [
    '**/__tests__/**/*.test.ts',
    '**/?(*.)+(spec|test).ts'
  ],
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/generated/**',
    '!src/app/api/**' // API routes tested via integration
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },
  setupFilesAfterEnv: ['<rootDir>/tests/setup.ts'],
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1'
  }
}
```

---

## 🔧 UNIT TESTS

### **1. Service Layer Tests**
```typescript
// tests/unit/services/neumatico.service.test.ts
import { NeumaticoService } from '@/lib/services/neumatico.service'
import { NeumaticoRepository } from '@/lib/repositories/neumatico.repository'
import { AlertaService } from '@/lib/services/alerta.service'
import { AuditoriaService } from '@/lib/services/auditoria.service'

// Mocks
jest.mock('@/lib/repositories/neumatico.repository')
jest.mock('@/lib/services/alerta.service')
jest.mock('@/lib/services/auditoria.service')

describe('NeumaticoService', () => {
  let service: NeumaticoService
  let mockRepository: jest.Mocked<NeumaticoRepository>
  let mockAlertaService: jest.Mocked<AlertaService>
  let mockAuditoriaService: jest.Mocked<AuditoriaService>

  beforeEach(() => {
    mockRepository = new NeumaticoRepository() as jest.Mocked<NeumaticoRepository>
    mockAlertaService = new AlertaService() as jest.Mocked<AlertaService>
    mockAuditoriaService = new AuditoriaService() as jest.Mocked<AuditoriaService>
    
    service = new NeumaticoService(mockRepository, mockAlertaService, mockAuditoriaService)
  })

  describe('registrarEvento', () => {
    it('debe procesar instalación correctamente', async () => {
      // Arrange
      const eventoData = {
        tipo_evento: 'INSTALACION',
        neumatico_id: 'uuid-neumatico',
        vehiculo_id: 'uuid-vehiculo',
        posicion_montaje_id: 'uuid-posicion',
        kilometraje_vehiculo: 50000
      }
      
      const mockNeumatico = {
        id: 'uuid-neumatico',
        estado_actual: 'EN_STOCK',
        numero_serie: 'TEST123'
      }

      mockRepository.findUnique.mockResolvedValue(mockNeumatico)
      mockRepository.prisma.$transaction.mockImplementation(async (callback) => {
        return callback({
          neumatico: {
            update: jest.fn().mockResolvedValue({
              ...mockNeumatico,
              estado_actual: 'INSTALADO'
            })
          },
          eventoNeumatico: {
            create: jest.fn().mockResolvedValue({ id: 'uuid-evento' })
          }
        })
      })

      // Act
      const result = await service.registrarEvento(eventoData, 'uuid-user')

      // Assert
      expect(result.neumatico.estado_actual).toBe('INSTALADO')
      expect(mockRepository.findUnique).toHaveBeenCalledWith({ id: 'uuid-neumatico' })
    })

    it('debe rechazar instalación de neumático no en stock', async () => {
      // Arrange
      const eventoData = {
        tipo_evento: 'INSTALACION',
        neumatico_id: 'uuid-neumatico'
      }
      
      const mockNeumatico = {
        estado_actual: 'INSTALADO'
      }

      mockRepository.findUnique.mockResolvedValue(mockNeumatico)

      // Act & Assert
      await expect(service.registrarEvento(eventoData, 'uuid-user'))
        .rejects.toThrow('Solo se pueden instalar neumáticos en stock')
    })
  })
})
```

### **2. Repository Tests**
```typescript
// tests/unit/repositories/neumatico.repository.test.ts
import { NeumaticoRepository } from '@/lib/repositories/neumatico.repository'
import { prisma } from '@/lib/prisma'

jest.mock('@/lib/prisma', () => ({
  prisma: {
    neumatico: {
      findMany: jest.fn(),
      findUnique: jest.fn(),
      create: jest.fn(),
      update: jest.fn(),
      count: jest.fn()
    }
  }
}))

describe('NeumaticoRepository', () => {
  let repository: NeumaticoRepository
  const mockPrisma = prisma as jest.Mocked<typeof prisma>

  beforeEach(() => {
    repository = new NeumaticoRepository()
    jest.clearAllMocks()
  })

  describe('findByNumeroSerie', () => {
    it('debe encontrar neumático por número de serie', async () => {
      // Arrange
      const mockNeumatico = {
        id: 'uuid',
        numero_serie: 'TEST123',
        modelo: { fabricante: { nombre: 'Michelin' } }
      }
      
      mockPrisma.neumatico.findUnique.mockResolvedValue(mockNeumatico)

      // Act
      const result = await repository.findByNumeroSerie('TEST123')

      // Assert
      expect(result).toEqual(mockNeumatico)
      expect(mockPrisma.neumatico.findUnique).toHaveBeenCalledWith({
        where: { numero_serie: 'TEST123' },
        include: expect.objectContaining({
          modelo: { include: { fabricante: true } }
        })
      })
    })
  })
})
```

---

## 🔗 INTEGRATION TESTS

### **1. API Endpoints Tests**
```typescript
// tests/integration/api/neumaticos.test.ts
import { NextRequest } from 'next/server'
import { GET, POST } from '@/app/api/v1/neumaticos/route'
import { prisma } from '@/lib/prisma'
import { createMockUser, createMockNeumatico } from '../helpers/factories'

describe('/api/v1/neumaticos', () => {
  beforeEach(async () => {
    await prisma.$executeRaw`TRUNCATE TABLE neumaticos CASCADE`
  })

  describe('GET /api/v1/neumaticos', () => {
    it('debe retornar lista paginada de neumáticos', async () => {
      // Arrange
      const user = await createMockUser({ permissions: ['neumaticos:read'] })
      const neumaticos = await Promise.all([
        createMockNeumatico(),
        createMockNeumatico()
      ])

      const request = new NextRequest('http://localhost:3000/api/v1/neumaticos?page=1&limit=10')
      request.headers.set('x-user-id', user.id)
      request.headers.set('x-user-permissions', JSON.stringify(user.permissions))

      // Act
      const response = await GET(request)
      const data = await response.json()

      // Assert
      expect(response.status).toBe(200)
      expect(data.success).toBe(true)
      expect(data.data).toHaveLength(2)
      expect(data.pagination).toMatchObject({
        page: 1,
        limit: 10,
        total: 2
      })
    })

    it('debe rechazar acceso sin permisos', async () => {
      // Arrange
      const request = new NextRequest('http://localhost:3000/api/v1/neumaticos')
      request.headers.set('x-user-id', 'uuid-user')
      request.headers.set('x-user-permissions', JSON.stringify([]))

      // Act
      const response = await GET(request)

      // Assert
      expect(response.status).toBe(403)
    })
  })

  describe('POST /api/v1/neumaticos', () => {
    it('debe crear neumático correctamente', async () => {
      // Arrange
      const user = await createMockUser({ permissions: ['neumaticos:create'] })
      const modelo = await createMockModelo()
      
      const neumaticoData = {
        numero_serie: 'TEST123',
        modelo_id: modelo.id,
        dot: '2024',
        profundidad_inicial_mm: 12.5
      }

      const request = new NextRequest('http://localhost:3000/api/v1/neumaticos', {
        method: 'POST',
        body: JSON.stringify(neumaticoData)
      })
      request.headers.set('x-user-id', user.id)
      request.headers.set('x-user-permissions', JSON.stringify(user.permissions))

      // Act
      const response = await POST(request)
      const data = await response.json()

      // Assert
      expect(response.status).toBe(201)
      expect(data.success).toBe(true)
      expect(data.data.numero_serie).toBe('TEST123')
      
      // Verificar en BD
      const neumaticoEnBD = await prisma.neumatico.findUnique({
        where: { numero_serie: 'TEST123' }
      })
      expect(neumaticoEnBD).toBeTruthy()
    })
  })
})
```

### **2. Database Integration Tests**
```typescript
// tests/integration/database/transactions.test.ts
import { prisma } from '@/lib/prisma'
import { NeumaticoService } from '@/lib/services/neumatico.service'

describe('Database Transactions', () => {
  it('debe hacer rollback en caso de error durante evento', async () => {
    // Arrange
    const neumatico = await createMockNeumatico({ estado_actual: 'EN_STOCK' })
    const service = new NeumaticoService(/* deps */)

    // Simular error en alertas
    jest.spyOn(service['alertaService'], 'verificarAlertas')
      .mockRejectedValue(new Error('Error en alertas'))

    const eventoData = {
      tipo_evento: 'INSTALACION',
      neumatico_id: neumatico.id,
      vehiculo_id: 'uuid-vehiculo',
      posicion_montaje_id: 'uuid-posicion'
    }

    // Act & Assert
    await expect(service.registrarEvento(eventoData, 'uuid-user'))
      .rejects.toThrow('Error en alertas')

    // Verificar que no se creó el evento
    const eventos = await prisma.eventoNeumatico.findMany({
      where: { neumatico_id: neumatico.id }
    })
    expect(eventos).toHaveLength(0)

    // Verificar que el neumático no cambió de estado
    const neumaticoActualizado = await prisma.neumatico.findUnique({
      where: { id: neumatico.id }
    })
    expect(neumaticoActualizado?.estado_actual).toBe('EN_STOCK')
  })
})
```

---

## 🌐 E2E TESTS

### **1. Configuración Playwright**
```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
})
```

### **2. Flujo E2E Crítico**
```typescript
// tests/e2e/neumatico-lifecycle.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Flujo completo de neumático', () => {
  test('debe completar ciclo: creación → instalación → desmontaje', async ({ page }) => {
    // 1. Login
    await page.goto('/auth/login')
    await page.fill('[data-testid=username]', 'admin')
    await page.fill('[data-testid=password]', 'Admin123')
    await page.click('[data-testid=login-button]')
    
    await expect(page).toHaveURL('/dashboard')

    // 2. Crear neumático
    await page.goto('/neumaticos/nuevo')
    await page.fill('[data-testid=numero-serie]', 'E2E-TEST-001')
    await page.selectOption('[data-testid=modelo]', { label: 'Michelin XZE' })
    await page.fill('[data-testid=dot]', '2024')
    await page.fill('[data-testid=profundidad]', '12.5')
    await page.click('[data-testid=crear-neumatico]')

    await expect(page.locator('[data-testid=success-message]')).toContainText('Neumático creado')

    // 3. Instalar neumático
    await page.goto('/neumaticos')
    await page.click(`[data-testid=neumatico-E2E-TEST-001] [data-testid=instalar]`)
    await page.selectOption('[data-testid=vehiculo]', { label: 'ABC-123' })
    await page.selectOption('[data-testid=posicion]', { label: 'Delantero Izquierdo' })
    await page.fill('[data-testid=kilometraje]', '50000')
    await page.click('[data-testid=confirmar-instalacion]')

    await expect(page.locator('[data-testid=success-message]')).toContainText('Instalación registrada')

    // 4. Verificar estado
    await page.goto('/neumaticos/E2E-TEST-001')
    await expect(page.locator('[data-testid=estado-actual]')).toContainText('INSTALADO')
    await expect(page.locator('[data-testid=vehiculo-actual]')).toContainText('ABC-123')

    // 5. Desmontar neumático
    await page.click('[data-testid=desmontar]')
    await page.fill('[data-testid=kilometraje-desmontaje]', '55000')
    await page.selectOption('[data-testid=almacen-destino]', { label: 'Almacén Central' })
    await page.click('[data-testid=confirmar-desmontaje]')

    await expect(page.locator('[data-testid=success-message]')).toContainText('Desmontaje registrado')
    await expect(page.locator('[data-testid=estado-actual]')).toContainText('EN_STOCK')
  })
})
```

---

## 📊 QUALITY ASSURANCE

### **1. Code Quality Tools**
```json
// package.json (scripts)
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:e2e": "playwright test",
    "lint": "eslint src --ext .ts,.tsx",
    "lint:fix": "eslint src --ext .ts,.tsx --fix",
    "type-check": "tsc --noEmit",
    "quality": "npm run lint && npm run type-check && npm run test:coverage"
  }
}
```

### **2. ESLint Configuration**
```javascript
// .eslintrc.js
module.exports = {
  extends: [
    'next/core-web-vitals',
    '@typescript-eslint/recommended',
    'prettier'
  ],
  rules: {
    '@typescript-eslint/no-unused-vars': 'error',
    '@typescript-eslint/explicit-function-return-type': 'warn',
    'prefer-const': 'error',
    'no-var': 'error'
  }
}
```

### **3. GitHub Actions CI/CD**
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Type check
        run: npm run type-check
      
      - name: Lint
        run: npm run lint
      
      - name: Unit tests
        run: npm run test:coverage
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test
      
      - name: E2E tests
        run: npm run test:e2e
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
```

---

## 🎯 MÉTRICAS DE CALIDAD

### **Objetivos de Cobertura:**
- **Unit Tests:** >80% cobertura de líneas
- **Integration Tests:** 100% endpoints críticos
- **E2E Tests:** Flujos principales de usuario
- **Type Safety:** 100% TypeScript strict mode

### **Métricas de Performance:**
- **API Response Time:** <200ms (p95)
- **Database Queries:** <50ms (p95)
- **Bundle Size:** <500KB inicial
- **Lighthouse Score:** >90 Performance

---

**Estado:** ✅ PARTE 5 completada  
**Próximo:** PARTE 6 - Deploy y Monitoreo
