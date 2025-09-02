# 🚛 GES_NEU API

API para el sistema de Gestión de Neumáticos (GES_NEU). Esta aplicación proporciona los servicios necesarios para la gestión integral de neumáticos, incluyendo autenticación, catálogos y operaciones específicas del dominio.

## 🎉 Estado Actual - EN DESARROLLO ACTIVO

### 🔧 Estado de la API
- **Servidor**: Funcionando en `http://localhost:8000`
- **Documentación**: Disponible en `/docs` y `/redoc`
- **Autenticación JWT**: ✅ Completamente operativa
- **Base de Datos**: ✅ Conectada a PostgreSQL `ges_neu_bd`
- **Modelos**: 🔄 En proceso de alineación con esquema real

### 🔐 Credenciales de Prueba
```
Username: admin
Password: Admin123
```

### 📊 Estado de Módulos

#### ✅ Módulos Funcionales
- **Autenticación**: Gestión de usuarios, roles y permisos
  - Login/logout con JWT ✅
  - Sistema RBAC completo ✅
  - Endpoints: `/api/v1/auth/*` ✅

- **Catálogos**: Proveedores, almacenes, motivos de desecho
  - CRUD completo ✅
  - Endpoints: `/api/v1/catalogos/*` ✅
  - Enums alineados con BD ✅

- **Neumáticos**: Fabricantes y modelos
  - Fabricantes: CRUD completo ✅
  - Endpoints: `/api/v1/neumaticos/fabricantes` ✅
  - Schemas corregidos ✅

#### 🔄 Módulos En Desarrollo
- **Vehículos**: Gestión de flota y configuraciones
  - Modelos: Alineados con BD ✅
  - Schemas: Corregidos ✅
  - Endpoints: En testing 🔄

#### 📝 Módulos Implementados (Solo Modelos)
- **Inventario**: Control de stock y movimientos
- **Eventos**: Historial y seguimiento de neumáticos
- **Garantías**: Gestión de garantías de neumáticos
- **Alertas**: Sistema de notificaciones y alertas
- **Bitácoras**: Auditoría y registro de operaciones
- **Sistema**: Parámetros y configuración del sistema

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
uvicorn ges_neu_api.main:app --host 0.0.0.0 --port 8000 --reload

# Método 2: Usando el script (Linux/Mac)
chmod +x start_server.sh
./start_server.sh
```

El servidor estará disponible en: **http://localhost:8000**

### 🧪 Probar la API

Una vez iniciado el servidor, puedes probar la autenticación:

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/auth/token' \
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

### 📚 Documentación de la API

- **Swagger UI**: http://localhost:8000/docs
- **Documentación Redoc**: http://localhost:8000/redoc

### 🔗 Endpoints Principales

#### Autenticación
- `POST /api/v1/auth/token` - Obtener token JWT
- `GET /api/v1/auth/me` - Información del usuario actual

#### Catálogos
- `GET /api/v1/catalogos/proveedores` - Listar proveedores
- `GET /api/v1/catalogos/almacenes` - Listar almacenes
- `GET /api/v1/catalogos/motivos-desecho` - Listar motivos de desecho

#### Neumáticos
- `GET /api/v1/neumaticos/fabricantes` - Listar fabricantes
- `POST /api/v1/neumaticos/fabricantes` - Crear fabricante

#### Vehículos (En desarrollo)
- `GET /api/v1/vehiculos/` - Listar vehículos
- `POST /api/v1/vehiculos/` - Crear vehículo

## 🔍 Estructura de Código

### Importaciones

El proyecto utiliza importaciones relativas para un mejor manejo de paquetes:

```python
# Ejemplo de importación relativa
from .core.config import settings
from .modules.auth.router import router as auth_router
```

## 🛠️ Desarrollo

### 🎯 Principio Fundamental
**La API se adapta EXACTAMENTE a la base de datos PostgreSQL existente, NO al revés.**

- Modelos SQLModel deben coincidir 100% con `ESQUEMA_COMPLETO_BD.md`
- Tipos de datos, constraints y foreign keys deben ser idénticos
- NO modificar la estructura de la BD existente

### 🏗️ Estructura de un Módulo

Cada módulo sigue esta estructura:

```
modules/
  └── modulo/
      ├── __init__.py
      ├── models.py      # Modelos SQLModel (alineados con BD)
      ├── schemas.py     # Esquemas Pydantic (sin relaciones anidadas)
      ├── service.py     # Lógica de negocio con CRUD genérico
      ├── router.py      # Endpoints FastAPI
      └── dependencies.py # Inyección de dependencias
```

### 🔧 Convenciones de Código

- **Modelos**: Usar SQLModel con tipos exactos de PostgreSQL
- **Schemas**: Evitar relaciones anidadas para prevenir errores 500
- **Dependencias**: Usar `get_session` (no `get_db`) para AsyncSession
- **Enums**: Coincidir exactamente con enums de PostgreSQL
- **Rutas**: Rutas específicas antes que rutas con parámetros

### 🗄️ Base de Datos

**Configuración PostgreSQL:**
```
Host: localhost
Port: 5432
Database: ges_neu_bd
User: postgres
Password: B3ll1c0s
```

**Tablas Principales:**
- `usuarios`, `roles`, `permisos` (Auth)
- `vehiculos`, `tipos_vehiculo` (Vehículos)
- `proveedores`, `almacenes` (Catálogos)
- `fabricantes_neumatico`, `modelos_neumatico` (Neumáticos)
- Y 27 tablas adicionales según `ESQUEMA_COMPLETO_BD.md`

## 🚨 Problemas Conocidos

### En Resolución
- **Vehículos**: Error 500 en endpoints (en corrección)
- **Tipos Personalizados**: Dominio `placa_vehiculo` requiere manejo especial

### Resueltos Recientemente
- ✅ Error 422 en fabricantes (rutas reordenadas)
- ✅ Error 500 en catálogos (dependencias corregidas)
- ✅ Conflictos metadata SQLAlchemy (relaciones eliminadas)

## 📝 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

**Última actualización**: 1 Septiembre 2025 - Estado: Desarrollo activo con correcciones en curso
