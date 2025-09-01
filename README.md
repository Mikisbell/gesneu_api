# 🚛 GES_NEU API

API para el sistema de Gestión de Neumáticos (GES_NEU). Esta aplicación proporciona los servicios necesarios para la gestión integral de neumáticos, incluyendo autenticación, catálogos y operaciones específicas del dominio.

## 🎉 Estado Actual - COMPLETAMENTE FUNCIONAL

### ✅ API Lista para Producción
- **Servidor**: Funcionando en `http://localhost:8001`
- **Documentación**: Disponible en `/docs` y `/redoc`
- **Autenticación JWT**: Completamente operativa
- **Base de Datos**: Alineada con esquema PostgreSQL existente
- **Modelos**: 100% sincronizados con `ESQUEMA_COMPLETO_BD.md`

### 🔐 Credenciales de Prueba
```
Username: admin
Password: Admin123
```

### Módulos Implementados
- **Autenticación**: Gestión de usuarios, roles y permisos (Funcional ✅)
- **Vehículos**: Gestión de flota, tipos y configuraciones (Funcional ✅)
- **Catálogos**: Proveedores, almacenes, motivos de desecho (Funcional ✅)
- **Neumáticos**: Fabricantes, modelos y gestión de neumáticos (Funcional ✅)
- **Inventario**: Control de stock y movimientos (Funcional ✅)
- **Eventos**: Historial y seguimiento de neumáticos (Funcional ✅)
- **Garantías**: Gestión de garantías de neumáticos (Funcional ✅)
- **Alertas**: Sistema de notificaciones y alertas (Funcional ✅)
- **Bitácoras**: Auditoría y registro de operaciones (Modelos ✅)
- **Sistema**: Parámetros y configuración del sistema (Modelos ✅)
- **Estructura Base**: Configuración de la aplicación, logging y manejo de errores (Funcional ✅)

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
│   ├── monitoring.py    # Monitoreo y métricas de la aplicación
│   ├── base_models.py   # Modelos base compartidos
│   └── crud.py          # Operaciones CRUD genéricas

├── modules/             # Módulos de la aplicación
│   ├── __init__.py
│   ├── auth/            # Módulo de autenticación
│   │   ├── __init__.py
│   │   ├── models.py    # Modelos de datos
│   │   ├── schemas.py   # Esquemas de validación
│   │   ├── service.py   # Lógica de negocio
│   │   └── router.py    # Endpoints de la API
│   ├── vehiculos/       # Módulo de vehículos
│   │   ├── models.py    # Tipos, configuraciones, posiciones
│   │   ├── schemas.py   # Esquemas de validación
│   │   ├── service.py   # Lógica de negocio
│   │   └── router.py    # Endpoints de la API
│   ├── catalogos/       # Módulo de catálogos
│   │   ├── models.py    # Proveedores, almacenes, motivos
│   │   ├── schemas.py   # Esquemas de validación
│   │   ├── service.py   # Lógica de negocio
│   │   └── router.py    # Endpoints de la API
│   ├── neumaticos/      # Módulo de neumáticos
│   │   ├── models.py    # Fabricantes, modelos, neumáticos
│   │   ├── schemas.py   # Esquemas de validación
│   │   ├── service.py   # Lógica de negocio
│   │   └── router.py    # Endpoints de la API
│   ├── inventario/      # Módulo de inventario
│   │   ├── models.py    # Stock y movimientos
│   │   ├── schemas.py   # Esquemas de validación
│   │   ├── service.py   # Lógica de negocio
│   │   └── router.py    # Endpoints de la API
│   ├── eventos/         # Módulo de eventos
│   │   ├── models.py    # Historial y mediciones
│   │   ├── schemas.py   # Esquemas de validación
│   │   ├── service.py   # Lógica de negocio
│   │   └── router.py    # Endpoints de la API
│   ├── garantias/       # Módulo de garantías
│   │   ├── models.py    # Garantías de neumáticos
│   │   ├── schemas.py   # Esquemas de validación
│   │   ├── service.py   # Lógica de negocio
│   │   └── router.py    # Endpoints de la API
│   ├── alertas/         # Módulo de alertas
│   │   ├── models.py    # Sistema de notificaciones
│   │   ├── schemas.py   # Esquemas de validación
│   │   ├── service.py   # Lógica de negocio
│   │   └── router.py    # Endpoints de la API
│   ├── bitacoras/       # Módulo de bitácoras
│   │   └── models.py    # Auditoría y operaciones
│   └── sistema/         # Módulo de sistema
│       └── models.py    # Parámetros y configuración

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
- PostgreSQL 17.6+ (Base de datos)
- Git (Control de versiones)

### Configuración Inicial

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/Mikisbell/gesneu_api.git
   cd gesneu_api
   ```

2. **Configurar entorno virtual**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # En Windows: .venv\Scripts\activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   # Editar .env con tus configuraciones de PostgreSQL
   ```

5. **Configurar Base de Datos PostgreSQL**
   ```bash
   # Asegúrate de tener PostgreSQL ejecutándose
   # Crear base de datos: ges_neu_bd
   # Configurar credenciales en .env
   ```

### Iniciar el Servidor

Para desarrollo local:

```bash
# Método 1: Usando uvicorn directamente
uvicorn ges_neu_api.main:app --host 0.0.0.0 --port 8001 --reload

# Método 2: Usando el script (Linux/Mac)
chmod +x start_server.sh
./start_server.sh
```

El servidor estará disponible en: **http://localhost:8001**

### 🧪 Probar la API

Una vez iniciado el servidor, puedes probar la autenticación:

```bash
curl -X 'POST' \
  'http://localhost:8001/api/v1/auth/token' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=password&username=admin&password=Admin123'
```

Respuesta esperada:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

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
