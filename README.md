# 🚛 GES_NEU API

API para el sistema de Gestión de Neumáticos (GES_NEU). Esta aplicación proporciona los servicios necesarios para la gestión integral de neumáticos, incluyendo autenticación, catálogos y operaciones específicas del dominio.

## 📌 Estado Actual

### Módulos Implementados
- **Autenticación**: Gestión de usuarios, roles y permisos (Completo ✅)
- **Vehículos**: Gestión de flota, tipos y configuraciones (Completo ✅)
- **Catálogos**: Proveedores, almacenes, motivos de desecho (Completo ✅)
- **Neumáticos**: Fabricantes, modelos y gestión de neumáticos (Completo ✅)
- **Inventario**: Control de stock y movimientos (Completo ✅)
- **Eventos**: Historial y seguimiento de neumáticos (Completo ✅)
- **Garantías**: Gestión de garantías de neumáticos (Completo ✅)
- **Alertas**: Sistema de notificaciones y alertas (Completo ✅)
- **Bitácoras**: Auditoría y registro de operaciones (Modelos ✅)
- **Sistema**: Parámetros y configuración del sistema (Modelos ✅)
- **Estructura Base**: Configuración de la aplicación, logging y manejo de errores (Completo ✅)

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
   python -m venv .venvpython -c "print('Probando neumaticos con Index...'); import ges_neu_api.modules.neumaticos.models; print('✅ Neumaticos OK')"
Probando neumaticos con Index...
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    print('Probando neumaticos con Index...'); import ges_neu_api.modules.neumaticos.models; print('✅ Neumaticos OK')
                                               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "E:\FREECLOUD\FREECLOUD - IA\gesneu_api\ges_neu_api\modules\neumaticos\models.py", line 49, in <module>
    class ModeloNeumatico(BaseModel, table=True):
    ...<20 lines>...
        )
  File "C:\Users\Mateo\AppData\Local\Programs\Python\Python313\Lib\site-packages\sqlmodel\main.py", line 641, in __init__
    DeclarativeMeta.__init__(cls, classname, bases, dict_, **kw)
    ~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Mateo\AppData\Local\Programs\Python\Python313\Lib\site-packages\sqlalchemy\orm\decl_api.py", line 198, in __init__
    _as_declarative(reg, cls, dict_)
    ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
  File "C:\Users\Mateo\AppData\Local\Programs\Python\Python313\Lib\site-packages\sqlalchemy\orm\decl_base.py", line 245, in _as_declarative
    return _MapperConfig.setup_mapping(registry, cls, dict_, None, {})
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Mateo\AppData\Local\Programs\Python\Python313\Lib\site-packages\sqlalchemy\orm\decl_base.py", line 326, in setup_mapping
    return _ClassScanMapperConfig(
        registry, cls_, dict_, table, mapper_kw
    )
  File "C:\Users\Mateo\AppData\Local\Programs\Python\Python313\Lib\site-packages\sqlalchemy\orm\decl_base.py", line 577, in __init__
    self._setup_table(table)
    ~~~~~~~~~~~~~~~~~^^^^^^^
  File "C:\Users\Mateo\AppData\Local\Programs\Python\Python313\Lib\site-packages\sqlalchemy\orm\decl_base.py", line 1762, in _setup_table
    table_cls(
    ~~~~~~~~~^
        tablename,
        ^^^^^^^^^^
    ...<3 lines>...
        **table_kw,
        ^^^^^^^^^^^
    ),
    ^
  File "<string>", line 2, in __new__
  File "C:\Users\Mateo\AppData\Local\Programs\Python\Python313\Lib\site-packages\sqlalchemy\util\deprecations.py", line 281, in warned
    return fn(*args, **kwargs)  # type: ignore[no-any-return]
  File "C:\Users\Mateo\AppData\Local\Programs\Python\Python313\Lib\site-packages\sqlalchemy\sql\schema.py", line 429, in __new__
    return cls._new(*args, **kw)
           ~~~~~~~~^^^^^^^^^^^^^
  File "C:\Users\Mateo\AppData\Local\Programs\Python\Python313\Lib\site-packages\sqlalchemy\sql\schema.py", line 483, in _new
    with util.safe_reraise():
         ~~~~~~~~~~~~~~~~~^^
  File "C:\Users\Mateo\AppData\Local\Programs\Python\Python313\Lib\site-packages\sqlalchemy\util\langhelpers.py", line 224, in __exit__
    raise exc_value.with_traceback(exc_tb)
  File "C:\Users\Mateo\AppData\Local\Programs\Python\Python313\Lib\site-packages\sqlalchemy\sql\schema.py", line 479, in _new
    table.__init__(name, metadata, *args, _no_init=False, **kw)  # type: ignore[misc] # noqa: E501
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Mateo\AppData\Local\Programs\Python\Python313\Lib\site-packages\sqlalchemy\sql\schema.py", line 873, in __init__
    self._init_items(
    ~~~~~~~~~~~~~~~~^
        *args,
        ^^^^^^
    ...<3 lines>...
        all_names={},
        ^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\Mateo\AppData\Local\Programs\Python\Python313\Lib\site-packages\sqlalchemy\sql\schema.py", line 233, in _init_items
    spwd(self, **kw)
    ~~~~^^^^^^^^^^^^
  File "C:\Users\Mateo\AppData\Local\Programs\Python\Python313\Lib\site-packages\sqlalchemy\sql\base.py", line 1347, in _set_parent_with_dispatch
    self._set_parent(parent, **kw)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^
  File "C:\Users\Mateo\AppData\Local\Programs\Python\Python313\Lib\site-packages\sqlalchemy\sql\schema.py", line 2336, in _set_parent
    raise exc.ArgumentError(
    ...<2 lines>...
    )
sqlalchemy.exc.ArgumentError: Column object 'id' already assigned to Table 'fabricantes_neumatico'
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
