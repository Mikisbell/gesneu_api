
# 🤝 Contribuir a GesNeu API

¡Gracias por tu interés en contribuir! Este documento establece los lineamientos para mantener la calidad y estabilidad de nuestro sistema crítico de gestión de flota.

## 🛠️ Desarrollo Local

1. **Requisitos Previos**:
   - Node.js > v20 LTS
   - Base de datos PostgreSQL local o remota (Supabase recomendado)
   - Git configurado

2. **Setup Rápido**:
   ```bash
   git clone [repo-url]
   npm install
   cp .env.example .env # Configurar credenciales DB
   npx prisma generate
   npm run dev
   ```

## 🧪 Estándares de Calidad (Automáticos)

Hemos integrado **Husky** y **GitHub Actions** para asegurar la calidad.

### Antes de hacer Commit (Husky)
Al ejecutar `git commit`, localmente se verificará automáticamente:
- **Linting (ESLint)**: Verificación de sintaxis y reglas de código.
- **Prettier**: Formato consistente.
*Si falla alguno, el commit será rechazado. Ejecuta `npm run lint --fix` si tienes problemas.*

### Flujo de Pull Request (GitHub Actions)
Cada PR dispara automáticamente:
1. **CI Quality**: Linting y Type Checking (Build dry-run).
2. **Playwright E2E**: Ejecuta la suite completa de tests End-to-End.

## 🧪 Testing

### Tests E2E (Playwright)
Son obligatorios para cualquier nueva funcionalidad crítica.
```bash
# Ejecutar suite completa (headless)
npm run test:e2e

# Modo UI interactivo (útil para debug)
npm run test:e2e:ui
```

### Tests de Integración (Jest)
Para lógica de negocio compleja y utilidades.
```bash
npm test
```

## 📝 Convenciones

1. **Commits Semánticos**:
   - `feat: ...` para nuevas funcionalidades
   - `fix: ...` para corrección de bugs
   - `docs: ...` para documentación
   - `chore: ...` para configuración (CI, deps)

2. **Ramas**:
   - `main`: Producción estable.
   - `feature/nombre-tarea`: Desarrollo de nuevas features.
   - `fix/nombre-bug`: Correcciones rápidas.

## 🚨 Monitoreo (Logging Interno)
Usa el `LoggerService` para eventos críticos, NO uses `console.log` en producción.

```typescript
import { logger } from '@/lib/logger';

// ✅ Correcto
await logger.error('Fallo en pago', error, { userId });

// ❌ Incorrecto
console.log('Error pago', error);
```

¡Gracias por ayudar a construir un sistema robusto! 🚛
