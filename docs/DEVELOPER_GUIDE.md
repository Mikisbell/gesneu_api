# GUÍA TÉCNICA PARA DESARROLLADORES - API GESNEU

## 🚀 Introducción

Esta guía proporciona toda la información técnica necesaria para desarrollar, mantener y extender la API GesNeu. La API está construida con FastAPI y sigue principios de arquitectura limpia y patrones de diseño modernos.

## 📋 Tabla de Contenidos

1. [Configuración del Entorno](#configuración-del-entorno)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Patrones de Desarrollo](#patrones-de-desarrollo)
5. [Testing Avanzado](#testing-avanzado)
6. [Despliegue y CI/CD](#despliegue-y-cicd)
7. [Monitoreo y Observabilidad](#monitoreo-y-observabilidad)
8. [Mejores Prácticas](#mejores-prácticas)

## 🛠️ Configuración del Entorno

### Requisitos del Sistema
- Python 3.10+
- PostgreSQL 15+
- Poetry (gestión de dependencias)
- Docker & Docker Compose
- Git

### Configuración Inicial

```bash
# Clonar repositorio
git clone https://github.com/Mikisbell/gesneu_api.git
cd gesneu_api

# Instalar Poetry (si no está instalado)
curl -sSL https://install.python-poetry.org | python3 -

# Instalar dependencias
poetry install

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Inicializar base de datos
poetry run alembic upgrade head

# Ejecutar servidor de desarrollo
poetry run uvicorn ges_neu_api.main:app --reload
```

### Variables de Entorno Críticas

```bash
# Base de datos
DATABASE_URL=postgresql://postgres:password@localhost:5432/ges_neu_bd
POSTGRES_USER=postgres
POSTGRES_PASSWORD=B3ll1c0s
POSTGRES_DB=ges_neu_bd

# Seguridad
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Aplicación
APP_ENV=development
DEBUG=true
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

## 🏗️ Arquitectura del Sistema

### Principios Arquitectónicos

1. **Arquitectura Hexagonal**: Separación clara entre lógica de negocio y adaptadores
2. **Domain-Driven Design**: Modelos que reflejan el dominio de negocio
3. **SOLID Principles**: Código mantenible y extensible
4. **Clean Architecture**: Dependencias apuntan hacia el interior

### Capas de la Aplicación

```
ges_neu_api/
├── core/           # Configuración, base de datos, utilidades
├── modules/        # Módulos de dominio
│   ├── auth/       # Autenticación y autorización
│   ├── vehiculos/  # Gestión de vehículos
│   ├── neumaticos/ # Gestión de neumáticos
│   └── ...
└── main.py         # Punto de entrada de la aplicación
```

### Patrón por Módulo

Cada módulo sigue la misma estructura:

```
module_name/
├── __init__.py
├── models.py       # Modelos SQLModel/SQLAlchemy
├── schemas.py      # Esquemas Pydantic para validación
├── service.py      # Lógica de negocio
├── router.py       # Endpoints REST
├── dependencies.py # Dependencias específicas del módulo
└── enums.py        # Enumeraciones del dominio
```

## 📁 Estructura del Proyecto

### Directorio Core

```python
# core/config.py - Configuración centralizada
class Settings(BaseSettings):
    PROJECT_NAME: str = "API GesNeu"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    DATABASE_URL: str
    
    class Config:
        env_file = ".env"

# core/database.py - Configuración de base de datos
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

# core/security.py - Utilidades de seguridad
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

### Modelos de Datos

```python
# Ejemplo: modules/vehiculos/models.py
class Vehiculo(SQLModel, table=True):
    __tablename__ = "vehiculos"
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    placa: str = Field(max_length=20, unique=True)
    tipo_vehiculo_id: UUID = Field(foreign_key="tipos_vehiculo.id")
    activo: bool = Field(default=True)
    
    # Campos de auditoría
    creado_en: datetime = Field(default_factory=datetime.utcnow)
    creado_por: UUID = Field(foreign_key="usuarios.id")
    actualizado_en: Optional[datetime] = None
    actualizado_por: Optional[UUID] = Field(foreign_key="usuarios.id")
```

### Servicios de Negocio

```python
# Ejemplo: modules/vehiculos/service.py
class VehiculoService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_vehiculo(self, vehiculo_data: VehiculoCreate) -> Vehiculo:
        db_vehiculo = Vehiculo(**vehiculo_data.dict())
        self.db.add(db_vehiculo)
        await self.db.commit()
        await self.db.refresh(db_vehiculo)
        return db_vehiculo
    
    async def get_vehiculos(self, skip: int = 0, limit: int = 100) -> List[Vehiculo]:
        result = await self.db.execute(
            select(Vehiculo).offset(skip).limit(limit)
        )
        return result.scalars().all()
```

### Routers REST

```python
# Ejemplo: modules/vehiculos/router.py
@router.get("/", response_model=List[VehiculoResponse])
async def list_vehiculos(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_session),
    current_user: Usuario = Depends(get_current_active_user)
):
    service = VehiculoService(db)
    vehiculos = await service.get_vehiculos(skip=skip, limit=limit)
    return vehiculos
```

## 🧪 Testing Avanzado

### Estructura de Tests

```
tests/
├── conftest.py              # Configuración global de pytest
├── unit/                    # Tests unitarios
│   ├── test_auth/
│   ├── test_vehiculos/
│   └── ...
├── integration/             # Tests de integración
│   ├── test_api_flows.py
│   └── test_database.py
└── advanced/                # Tests avanzados
    ├── test_performance.py  # Tests de rendimiento
    ├── test_security.py     # Tests de seguridad
    └── test_integration.py  # Tests end-to-end
```

### Configuración de Tests

```python
# conftest.py
@pytest.fixture(scope="session")
async def test_db():
    # Configurar base de datos de pruebas
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

@pytest.fixture
async def client(test_db):
    # Cliente HTTP para tests
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
```

### Tests de Performance

```python
# tests/advanced/test_performance.py
@pytest.mark.asyncio
async def test_endpoint_response_time():
    suite = PerformanceTestSuite()
    results = await suite.test_response_times(["/api/v1/vehiculos/"], iterations=50)
    
    for endpoint, data in results.items():
        assert data["avg_ms"] < 500, f"Response time too high: {data['avg_ms']}ms"
        assert data["success_rate"] >= 95, f"Success rate too low: {data['success_rate']}%"
```

### Tests de Seguridad

```python
# tests/advanced/test_security.py
@pytest.mark.asyncio
async def test_sql_injection_protection():
    suite = SecurityTestSuite()
    results = await suite.test_input_validation()
    
    assert results["sql_injection_login"]["status"] == "PASS"
    assert results["xss_parameters"]["status"] == "PASS"
```

## 🚀 Despliegue y CI/CD

### Pipeline de CI/CD

El proyecto incluye configuración completa de GitHub Actions:

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: ges_neu_bd_test
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: poetry install
      - name: Run tests
        run: poetry run pytest --cov=ges_neu_api
```

### Configuración Docker

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Instalar Poetry
RUN pip install poetry

# Copiar archivos de dependencias
COPY pyproject.toml poetry.lock ./

# Instalar dependencias
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev

# Copiar código fuente
COPY . .

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "ges_neu_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose para Desarrollo

```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/ges_neu_bd
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ges_neu_bd
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

## 📊 Monitoreo y Observabilidad

### Métricas con Prometheus

```python
# core/monitoring.py
from prometheus_fastapi_instrumentator import Instrumentator

def setup_metrics(app: FastAPI):
    instrumentator = Instrumentator()
    instrumentator.instrument(app).expose(app)
    
    # Métricas personalizadas
    REQUEST_COUNT = Counter(
        "http_requests_total",
        "Total HTTP requests",
        ["method", "endpoint", "status"]
    )
```

### Logging Estructurado

```python
# core/logging_config.py
import structlog

def setup_structured_logging():
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
```

### OpenTelemetry

```python
# core/tracing.py
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

def setup_tracing(app: FastAPI):
    FastAPIInstrumentor.instrument_app(app)
    SQLAlchemyInstrumentor().instrument(engine=engine)
```

## 🎯 Mejores Prácticas

### Desarrollo

1. **Seguir principios SOLID**
2. **Usar type hints en todo el código**
3. **Documentar funciones complejas**
4. **Mantener funciones pequeñas y enfocadas**
5. **Usar nombres descriptivos**

### Base de Datos

1. **Usar migraciones para cambios de esquema**
2. **Indexar campos de búsqueda frecuente**
3. **Usar transacciones para operaciones críticas**
4. **Validar datos en múltiples capas**

### Seguridad

1. **Validar toda entrada de usuario**
2. **Usar HTTPS en producción**
3. **Implementar rate limiting**
4. **Auditar cambios críticos**
5. **Mantener dependencias actualizadas**

### Performance

1. **Usar paginación en listados**
2. **Implementar caching estratégico**
3. **Optimizar consultas SQL**
4. **Monitorear métricas de performance**

## 🔧 Herramientas de Desarrollo

### Scripts Útiles

```bash
# Ejecutar todos los tests
python scripts/run_all_tests.py

# Análisis de calidad de código
python scripts/code_quality_check.py

# Generar migración
poetry run alembic revision --autogenerate -m "descripción"

# Aplicar migraciones
poetry run alembic upgrade head

# Formatear código
poetry run ruff format .

# Verificar tipos
poetry run mypy ges_neu_api/
```

### Configuración del Editor

Configuración recomendada para VS Code:

```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "ruff",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests/"]
}
```

## 📚 Recursos Adicionales

### Documentación de Referencia

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

### Comandos de Desarrollo Frecuentes

```bash
# Desarrollo local
poetry run uvicorn ges_neu_api.main:app --reload --host 0.0.0.0 --port 8000

# Tests con cobertura
poetry run pytest --cov=ges_neu_api --cov-report=html

# Linting y formateo
poetry run ruff check . --fix
poetry run ruff format .

# Verificación de tipos
poetry run mypy ges_neu_api/

# Análisis de seguridad
poetry run bandit -r ges_neu_api/
```

## 🚨 Solución de Problemas Comunes

### Error de Conexión a Base de Datos

```bash
# Verificar que PostgreSQL esté ejecutándose
sudo systemctl status postgresql

# Verificar configuración de conexión
echo $DATABASE_URL

# Probar conexión manual
psql -h localhost -U postgres -d ges_neu_bd
```

### Problemas de Migraciones

```bash
# Ver estado actual
poetry run alembic current

# Ver historial
poetry run alembic history

# Revertir migración
poetry run alembic downgrade -1
```

### Issues de Performance

```bash
# Ejecutar tests de performance
python tests/advanced/test_performance.py

# Monitorear queries SQL
# Agregar logging en core/database.py
```

---

**Última actualización**: 3 Septiembre 2025  
**Versión de la API**: 1.0.0  
**Mantenido por**: Equipo de Desarrollo GesNeu
