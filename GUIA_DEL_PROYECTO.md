# Guía del Proyecto GesNeu API

## 1. Introducción
Bienvenido a la API GesNeu. Este proyecto proporciona una interfaz RESTful para la gestión integral del ciclo de vida de los neumáticos en una flota de vehículos. El objetivo es centralizar la información, optimizar costos operativos y aumentar la seguridad a través de un seguimiento detallado de los activos.

## 2. Estado Actual del Proyecto (29 de Agosto, 2025)

### Módulo de Autenticación (Completo ✅)
- [x] Modelos de datos sincronizados con la BD
- [x] Contratos de servicio implementados
- [x] Schemas para validación de datos
- [x] Lógica de negocio en servicios
- [x] Pruebas unitarias (>95% cobertura)
- [x] Endpoints y rutas implementados
- [x] Pruebas de integración

### Próximos Módulos
- [ ] Módulo de Catálogos
- [ ] Módulo de Vehículos
- [ ] Módulo de Neumáticos

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

## 6. Próximos Pasos

1. **Módulo de Catálogos**
   - Definir modelos de datos
   - Implementar servicios básicos
   - Crear endpoints de la API

2. **Módulo de Vehículos**
   - Diseñar esquema de base de datos
   - Implementar lógica de negocio
   - Integrar con módulo de autenticación

3. **Módulo de Neumáticos**
   - Modelar ciclo de vida de neumáticos
   - Implementar seguimiento de desgaste
   - Crear alertas de mantenimiento

## 7. Recursos

- [Documentación de FastAPI](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)