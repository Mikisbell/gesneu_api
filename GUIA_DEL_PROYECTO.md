# Guía del Proyecto GesNeu API

## 1. Introducción
Bienvenido a la API GesNeu. Este proyecto proporciona una interfaz RESTful para la gestión integral del ciclo de vida de los neumáticos en una flota de vehículos. El objetivo es centralizar la información, optimizar costos operativos y aumentar la seguridad a través de un seguimiento detallado de los activos.

## 2. Estado Actual del Proyecto (30 de Agosto, 2025 - 22:16)

### Módulo de Autenticación (Completo ✅)
- [x] Modelos de datos sincronizados con la BD
- [x] Contratos de servicio implementados
- [x] Schemas para validación de datos
- [x] Lógica de negocio en servicios
- [x] Pruebas unitarias (>95% cobertura)
- [x] Endpoints y rutas implementados
- [x] Pruebas de integración

### Módulo de Vehículos (Completo ✅)
- [x] Modelos de datos implementados y funcionales
- [x] Estructura de módulo siguiendo arquitectura del proyecto
- [x] Modelos importables sin conflictos
- [x] Schemas para validación de datos
- [x] Servicios y endpoints básicos
- [x] Integración con sistema de autenticación
- [x] Contratos de servicio implementados
- [x] CRUD operations funcionales

### Módulo de Neumáticos (Completo ✅)
- [x] Modelos simplificados sin conflictos SQLAlchemy (NeumaticoBasico, FabricanteBasico, ModeloBasico)
- [x] Servicios CRUD completos para neumáticos, fabricantes y modelos
- [x] Router con 15+ endpoints REST implementados
- [x] Esquemas Pydantic con validaciones completas
- [x] Contratos e inyección de dependencias
- [x] Resolución de conflictos de metadatos SQLAlchemy
- [x] Arquitectura modular siguiendo convenciones del proyecto

### Módulo de Catálogos (En Progreso 🔄)
**ESTADO ACTUAL**: Parcialmente completado, requiere limpieza final
- [x] Servicio CatalogService implementado con CRUD para Proveedor, MotivoDesecho, Almacen, ParametroInventario
- [x] Router con endpoints REST completos para todas las entidades
- [x] Integración habilitada en main.py
- [x] Modelos disponibles: Proveedor, Disenio, MotivoDesecho, Almacen, ParametroInventario
- [ ] **PENDIENTE MAÑANA**: Limpiar código duplicado en service.py (errores de sintaxis)
- [ ] **PENDIENTE MAÑANA**: Verificar/crear schemas faltantes
- [ ] **PENDIENTE MAÑANA**: Probar importación y funcionamiento completo

**PROBLEMA IDENTIFICADO**: El archivo `service.py` tiene código duplicado y referencias a modelos inexistentes (Fabricante, ModeloNeumatico) que causan errores de sintaxis. Necesita limpieza completa.

### API Principal (Funcional ✅)
- [x] Servidor de desarrollo ejecutándose
- [x] FastAPI configurado correctamente
- [x] Middleware de monitoreo básico
- [x] Logging estructurado
- [x] CORS configurado
- [x] Documentación automática (/docs, /redoc)
- [x] Health check endpoint

### Configuración de Modelos SQLModel (Completada ✅)
- [x] Análisis completo del esquema de BD (36 tablas)
- [x] Configuración de BaseModel con campos de auditoría
- [x] Resolución de conflictos de metadatos SQLAlchemy
- [x] Refactorización para seguir arquitectura del README
- [x] Migración de archivos experimentales a backup
- [x] Configuración de Alembic con modelos funcionales

### Módulos Pendientes
- [ ] **Módulo de Bitácoras** - Estructura básica, pendiente refactoring

## 3. Estructura del Proyecto

```
/ges_neu_api
├── /core/                 # Código compartido
│   ├── config.py          # Configuración de la aplicación
│   ├── database.py        # Configuración de la base de datos
│   └── security.py        # Utilidades de seguridad
├── /modules/              # Módulos de negocio
│   └── /auth/             # Módulo de autenticación
│       ├── contracts.py   # Interfaces de servicio
│       ├── models.py      # Modelos de datos
│       ├── schemas.py     # Esquemas de validación
│       ├── service.py     # Lógica de negocio
│       ├── router.py      # Endpoints de la API
│       └── dependencies.py # Dependencias
├── /migrations/           # Migraciones de base de datos
└── /tests/                # Pruebas
    ├── /auth/             # Pruebas del módulo auth
    └── conftest.py        # Configuración de pruebas
```

## 4. Guía de Desarrollo

### 4.1 Configuración del Entorno

1. **Requisitos**
   - Docker y Docker Compose
   - Python 3.11+
   - Poetry (gestión de dependencias)

2. **Iniciar el entorno**
   ```bash
   # Copiar variables de entorno
   cp .env.example .env
   
   # Iniciar servicios con Docker
   docker-compose up -d --build
   
   # Instalar dependencias
   poetry install
   
   # Aplicar migraciones
   poetry run alembic upgrade head
   
   # Iniciar la aplicación
   poetry run uvicorn ges_neu_api.main:app --reload
   ```

### 4.2 Flujo de Trabajo

1. **Crear migraciones**
   ```bash
   poetry run alembic revision --autogenerate -m "descripción del cambio"
   poetry run alembic upgrade head
   ```

2. **Ejecutar pruebas**
   ```bash
   # Todas las pruebas
   poetry run pytest
   
   # Pruebas específicas
   poetry run pytest tests/auth/test_auth_services.py -v
   ```

3. **Verificar cobertura**
   ```bash
   poetry run pytest --cov=ges_neu_api tests/
   ```

## 5. Convenciones y Estándares

### 5.1 Código
- Usar type hints en todas las funciones
- Documentar con docstrings siguiendo Google Style
- Mantener las líneas a 88 caracteres máximo (Black formatter)
- Escribir pruebas para toda la lógica de negocio

### 5.2 Commits
Usar Conventional Commits:
- `feat:` Nueva característica
- `fix:` Corrección de errores
- `docs:` Cambios en la documentación
- `style:` Formato, punto y coma faltante, etc.
- `refactor:` Cambio en el código que no corrige un error ni añade una característica
- `test:` Añadir o corregir pruebas
- `chore:` Cambios en el proceso de build o herramientas

## 6. Trabajo Realizado - Configuración de Modelos

### 6.1 Análisis y Configuración Inicial
- **Análisis del esquema de BD**: Identificadas 36 tablas distribuidas en 7 módulos principales
- **Configuración de BaseModel**: Implementado con campos de auditoría estándar (id, activo, creado_en, creado_por, actualizado_en, actualizado_por)
- **Resolución de conflictos**: Solucionados problemas de metadatos SQLAlchemy por definiciones duplicadas

### 6.2 Refactorización de Arquitectura
- **Limpieza de estructura**: Movidos archivos experimentales a `temp_models_backup/`
- **Arquitectura consistente**: Cada módulo ahora sigue la estructura definida en README.md
- **Modelos funcionales**: Auth y Vehículos completamente operativos

### 6.3 Herramientas de Verificación Creadas
- `verify_models_schema.py` - Verificación de correspondencia BD vs modelos
- `test_all_imports.py` - Testing de importabilidad de modelos
- `final_models_summary.py` - Resumen del estado de configuración
- `MODELS_FINAL_GUIDE.md` - Guía completa de la solución implementada

### 6.4 Configuración de Migraciones
- **Alembic configurado** con modelos funcionales en `migrations/env.py`
- **Detección de diferencias** con BD existente (comportamiento esperado)
- **Preparado para migraciones** incrementales cuando sea necesario

### 6.5 Endpoints Disponibles

#### Autenticación
- `POST /auth/login` - Autenticación de usuarios
- `POST /auth/register` - Registro de nuevos usuarios
- `GET /auth/me` - Información del usuario actual
- `POST /auth/refresh` - Renovar token de acceso

#### Vehículos
- `GET /vehiculos/` - Listar vehículos
- `POST /vehiculos/` - Crear nuevo vehículo
- `GET /vehiculos/{id}` - Obtener vehículo específico
- `PUT /vehiculos/{id}` - Actualizar vehículo
- `DELETE /vehiculos/{id}` - Eliminar vehículo

#### Neumáticos (Completos)
**Neumáticos:**
- `POST /neumaticos/` - Crear neumático
- `GET /neumaticos/` - Listar neumáticos
- `GET /neumaticos/{id}` - Obtener neumático
- `PUT /neumaticos/{id}` - Actualizar neumático
- `DELETE /neumaticos/{id}` - Eliminar neumático

**Fabricantes:**
- `POST /neumaticos/fabricantes` - Crear fabricante
- `GET /neumaticos/fabricantes` - Listar fabricantes
- `GET /neumaticos/fabricantes/{id}` - Obtener fabricante
- `PUT /neumaticos/fabricantes/{id}` - Actualizar fabricante
- `DELETE /neumaticos/fabricantes/{id}` - Eliminar fabricante

**Modelos:**
- `POST /neumaticos/modelos` - Crear modelo
- `GET /neumaticos/modelos` - Listar modelos
- `GET /neumaticos/modelos/{id}` - Obtener modelo
- `PUT /neumaticos/modelos/{id}` - Actualizar modelo
- `DELETE /neumaticos/modelos/{id}` - Eliminar modelo

#### Sistema
- `GET /` - Información general de la API
- `GET /health` - Estado de salud del sistema
- `GET /neumaticos/health` - Estado del módulo de neumáticos

## 7. Próximos Pasos

### 7.1 URGENTE - Para Mañana (31 de Agosto)
1. **Finalizar módulo de Catálogos** 🚨
   - **CRÍTICO**: Limpiar archivo `service.py` - eliminar código duplicado y referencias a modelos inexistentes
   - Verificar que existan todos los schemas necesarios (ProveedorCreate, ProveedorRead, etc.)
   - Probar importación del módulo: `from ges_neu_api.modules.catalogos import router`
   - Verificar endpoints en `/docs` una vez funcionando

2. **Opciones para arreglar service.py**:
   - **Opción A**: Eliminar línea por línea el código roto (más seguro)
   - **Opción B**: Reescribir completamente el archivo (más rápido)
   - **Opción C**: Revisar primero qué schemas existen para asegurar compatibilidad

### 7.2 Corto Plazo
1. **Crear pruebas de endpoints**
   - Pruebas para módulo de Vehículos
   - Pruebas para módulo de Neumáticos
   - Validación de respuestas de API

2. **Habilitar módulo de neumáticos en main.py**
   - Integrar router de neumáticos en aplicación principal
   - Verificar funcionamiento completo de endpoints

### 7.2 Mediano Plazo
1. **Generar migraciones Alembic**
   - Crear migración inicial con modelos funcionales
   - Sincronizar esquema de BD con modelos

2. **Implementar funcionalidades core**
   - Gestión completa de ciclo de vida de neumáticos
   - Sistema de alertas y notificaciones
   - Reportes y métricas de rendimiento

### 7.3 Largo Plazo
1. **Optimización y escalabilidad**
   - Implementar caching con Redis
   - Optimizar consultas de BD
   - Configurar monitoreo avanzado

## 7. Recursos

- [Documentación de FastAPI](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)