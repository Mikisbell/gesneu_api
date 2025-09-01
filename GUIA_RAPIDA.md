# 🚀 Guía Rápida - GesNeu API

## 📋 Requisitos Previos
- **Python 3.11+**
- **Docker y Docker Compose** (opcional, solo para desarrollo con contenedores)
- **Poetry** (gestión de dependencias)
- **PostgreSQL** (base de datos)

## ⚡ Configuración Inicial

### 1. Clonar el repositorio
```bash
git clone <repo-url>
cd ges_neu_api
```

### 2. Configurar entorno virtual
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install poetry
poetry install
```

### 4. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus configuraciones de BD PostgreSQL
```

## 🚀 Iniciar el Servidor

### Para desarrollo local:
```bash
# Dar permisos de ejecución al script (Linux/Mac)
chmod +x start_server.sh

# Iniciar el servidor
./start_server.sh
```

### Alternativa directa:
```bash
python -m uvicorn ges_neu_api.main:app --reload --host 0.0.0.0 --port 8000
```

**El servidor estará disponible en:** http://localhost:8000

## 📚 Documentación de la API
- **Swagger UI:** http://localhost:8000/docs
- **Documentación Redoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/api/v1/health

## 🔍 Estado Actual de Módulos

| Módulo | Estado | Endpoints | Descripción |
|--------|--------|-----------|-------------|
| **Auth** | ✅ Completo | `/api/v1/auth/*` | Autenticación JWT, RBAC |
| **Vehículos** | ✅ Funcional | `/api/v1/vehiculos/*` | CRUD completo |
| **Neumáticos** | 🟡 Básico | `/api/v1/neumaticos/*` | Endpoints placeholder |
| **Catálogos** | ❌ Deshabilitado | - | Conflictos de modelos |

## 🛠️ Estructura de Código

### Importaciones
El proyecto utiliza importaciones relativas para un mejor manejo de paquetes:
```python
# Ejemplo de importación relativa
from .core.config import settings
from .modules.auth.router import router as auth_router
```

### Estructura de un Módulo
Cada módulo sigue esta estructura:
```
modules/
  └── modulo/
      ├── __init__.py
      ├── models.py      # Modelos SQLModel/SQLAlchemy
      ├── schemas.py     # Esquemas Pydantic
      ├── service.py     # Lógica de negocio
      ├── router.py      # Endpoints de la API
      ├── contracts.py   # Interfaces/contratos
      ├── dependencies.py # Dependencias específicas del módulo
      └── crud.py        # Operaciones CRUD (opcional)
```

## 🧪 Pruebas

### Ejecutar pruebas (requiere pytest):
```bash
# Instalar dependencias de testing
pip install pytest httpx

# Ejecutar todas las pruebas
python -m pytest

# Ejecutar pruebas específicas
python -m pytest tests/test_api_endpoints.py -v
```

## 📊 Comandos Útiles

### Verificar modelos:
```bash
python test_all_imports.py
```

### Verificar estado de BD:
```bash
python verify_models_schema.py
```

### Generar migraciones:
```bash
alembic revision --autogenerate -m "descripción"
alembic upgrade head
```

## 🔧 Desarrollo

### Convenciones de Código
- Usar **type hints** en todas las funciones
- Documentar con **docstrings** siguiendo el formato Google Style
- Mantener las **importaciones ordenadas** y agrupadas
- Usar **nombres descriptivos** para variables y funciones
- Seguir la **arquitectura modular** definida en README.md

### Variables de Entorno Importantes
```env
# Base de datos
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ges_neu_bd
DB_USER=tu_usuario
DB_PASSWORD=tu_password

# API
API_V1_STR=/api/v1
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
APP_DEBUG=true

# Seguridad
SECRET_KEY=tu_secret_key_aqui
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 🚨 Solución de Problemas Comunes

### Error de importación de módulos:
```bash
# Verificar que estés en el directorio correcto
pwd
# Verificar que el entorno virtual esté activo
which python
```

### Error de conexión a BD:
```bash
# Verificar variables de entorno
cat .env
# Probar conexión
python -c "from ges_neu_api.core.database import engine; print('BD OK')"
```

### Puerto ocupado:
```bash
# Cambiar puerto en .env o usar otro puerto
python -m uvicorn ges_neu_api.main:app --reload --port 8001
```

## 📝 Próximos Pasos

1. **Configurar BD PostgreSQL** y ejecutar migraciones
2. **Consolidar modelos de Neumáticos** 
3. **Reactivar módulo de Catálogos**
4. **Implementar pruebas automatizadas**
5. **Configurar CI/CD**

---
**🔗 Enlaces Útiles:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs  
- Health: http://localhost:8000/api/v1/health

*Última actualización: 30 de Agosto, 2025*
