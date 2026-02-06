# 📚 Documentación GesNeu API

Bienvenido a la documentación técnica de **GesNeu API**, el sistema integral para gestión de activos de neumáticos y flotas.

## 🗂 Estructura de Documentación

1.  [**Arquitectura del Sistema**](./01_ARQUITECTURA.md)
    *   Diseño de alto nivel, stack tecnológico y patrones.
2.  [**Modelo de Negocio**](./02_MODELO_NEGOCIO.md)
    *   Entidades principales, ciclo de vida del neumático y reglas.
3.  [**Referencia API**](./03_API_REFERENCE.md)
    *   Endpoints, autenticación y especificaciones técnicas.
4.  [**Base de Datos**](./04_BASE_DATOS.md)
    *   Diagrama ER, esquemas Prisma y migraciones.
5.  [**Seguridad**](./05_SEGURIDAD.md)
    *   Roles, permisos (RBAC) y auditoría.
6.  [**Testing & QA**](./06_TESTING.md)
    *   Estrategias de prueba, unitarias y E2E.
7.  [**Guía de Despliegue**](./07_DEPLOY.md)
    *   Configuración de Vercel, Supabase y variables de entorno.
8.  [**Integraciones & Webhooks**](./08_INTEGRACIONES.md) 🆕
    *   Guía para conectar ERPs y sistemas externos.
9.  [**Sistema de Eventos (Event-Driven Architecture)**](./events/README.md) 🔔
    *   Ver [suite completa](./events/) (8 documentos especializados por audiencia).
10. [**Tipado Profesional**](./10_TIPADO_PROFESIONAL.md)
    *   Guía avanzada de TypeScript y branded types.
11. [**Changelog**](./99_CHANGELOG.md)

    *   Historial de cambios y versiones.

---

## 🚀 Inicio Rápido

### Requisitos Previos
*   Node.js 18+
*   PostgreSQL 14+ (Supabase recomendado)

### Instalación
```bash
git clone https://github.com/Mikisbell/gesneu_api.git
cd gesneu_api
npm install
```

### Desarrollo
```bash
npm run dev
```

---

## 🤝 Contribución
Consulte `AGENT.md` para las reglas de desarrollo y estilo de código.
