# 🚛 GES_NEU API

API para el sistema de Gestión de Neumáticos (GES_NEU). Esta aplicación proporciona los servicios necesarios para la gestión integral de neumáticos, incluyendo autenticación, catálogos y operaciones específicas del dominio.

## 📌 Estado Actual

### Módulos Implementados
- **Autenticación**: Gestión de usuarios, roles y permisos (Completo ✅)
- **Estructura Base**: Configuración de la aplicación, logging y manejo de errores (Completo ✅)

### Próximos Módulos
- 🚧 Catálogos
- 🚧 Vehículos
- 🚧 Neumáticos

## 🏗️ Arquitectura

La aplicación sigue una arquitectura modular basada en los siguientes principios:

### Estructura de Módulos

```
ges_neu_api/
├── core/                 # Código compartido y componentes centrales
│   ├── __init__.py
│   ├── config.py        # Configuración de la aplicación
│   ├── database.py      # Configuración de la base de datos
│   ├── security.py      # Utilidades de seguridad
│   ├── contracts.py     # Contratos (Protocols) para inyección de dependencias
│   ├── exceptions.py    # Manejo de excepciones globales
│   ├── logging_config.py # Configuración de logging estructurado
│   └── monitoring.py    # Monitoreo y métricas de la aplicación

├── modules/             # Módulos de la aplicación
│   ├── __init__.py
│   ├── auth/            # Módulo de autenticación
│   │   ├── __init__.py
│   │   ├── models.py    # Modelos de datos
│   │   ├── schemas.py   # Esquemas de validación
│   │   ├── service.py   # Lógica de negocio
│   │   └── router.py    # Endpoints de la API
│   └── catalogos/       # Módulo de catálogos
│   └── vehiculos/       # Módulo de vehículos
│   └── neumaticos/      # Módulo de neumáticos

├── tests/               # Pruebas automatizadas
│   └── auth/            # Pruebas del módulo de autenticación

├── migrations/          # Migraciones de base de datos (Alembic)
├── scripts/             # Scripts de utilidad
├── start_server.sh      # Script para iniciar el servidor
└── .env.example         # Plantilla de variables de entorno
```

## 🚀 Guía Rápida

### Requisitos Previos
- Python 3.11+
- Docker y Docker Compose (opcional, solo para desarrollo con contenedores)
- Poetry (gestión de dependencias)

### Configuración Inicial

1. **Clonar el repositorio**
   ```bash
   git clone <repo-url>
   cd ges_neu_api
   ```

2. **Configurar entorno virtual**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # En Windows: .venv\Scripts\activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install poetry
   poetry install
   ```

4. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   # Editar .env con tus configuraciones
   ```

### Iniciar el Servidor

Para desarrollo local:

```bash
# Dar permisos de ejecución al script
chmod +x start_server.sh

# Iniciar el servidor
./start_server.sh
```

El servidor estará disponible en: http://localhost:8001

### Documentación de la API

- **Swagger UI**: http://localhost:8001/docs
- **Documentación Redoc**: http://localhost:8001/redoc

## 🔍 Estructura de Código

### Importaciones

El proyecto utiliza importaciones relativas para un mejor manejo de paquetes:

```python
# Ejemplo de importación relativa
from .core.config import settings
from .modules.auth.router import router as auth_router
```

## 🛠️ Desarrollo

### Estructura de un Módulo

Cada módulo sigue esta estructura:

```
modules/
  └── modulo/
      ├── __init__.py
      ├── models.py      # Modelos SQLAlchemy
      ├── schemas.py     # Esquemas Pydantic
      ├── service.py     # Lógica de negocio
      ├── router.py      # Endpoints de la API
      └── dependencies.py # Dependencias específicas del módulo
```

### Convenciones de Código

- Usar type hints en todas las funciones
- Documentar con docstrings siguiendo el formato Google Style
- Mantener las importaciones ordenadas y agrupadas
- Usar nombres descriptivos para variables y funciones

## 📝 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles.
