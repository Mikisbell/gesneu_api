# Plan de Construcción Definitivo: API NeuCLoud v2.0
Versión: 2.0 (Arquitectura Inteligente y Proactiva)

Fecha: 4 de Septiembre de 2025

Filosofía: Construir una plataforma de backend robusta, escalable y preparada para el futuro desde el principio, utilizando una Arquitectura por Capas estricta, contenedores Docker para todo el stack y un enfoque modular. Alineado con el principio DB-first: la API se adapta al esquema PostgreSQL existente o a las migraciones generadas explícitamente.

## Fase 0: La Cimentación (1 Semana)
Objetivo: Establecer un entorno de desarrollo y producción 100% consistente, limpio y automatizado.

### Sprint 0: Configuración del Entorno y Estructura del Proyecto

- Setup del Repositorio
  - Descripción: Inicializar un nuevo repositorio Git (`gesneu_api_v2`). Configurar `pyproject.toml` (Poetry o PDM), `.gitignore` y la estructura de carpetas (`ges_neu_api`, `core`, `modules`, `tests`).
  - DoD: El proyecto base está en Git y tiene una estructura de directorios limpia.

- Crear docker-compose.yml
  - Descripción: Crear `docker-compose.yml` en la raíz del proyecto. Definir los cuatro servicios clave: `api` (FastAPI), `db` (PostgreSQL), `storage` (MinIO) y `mail` (Postfix).
  - DoD: `docker-compose up` levanta los cuatro contenedores, aunque la API falle al inicio.

- Configurar la Base de Datos
  - Descripción: En el servicio `db`, configurar volúmenes para persistencia. Establecer variables de entorno para usuario, contraseña y base de datos en `.env`.
  - DoD: El contenedor de PostgreSQL se inicia y los datos persisten tras reinicios.

- Configurar MinIO y Postfix
  - Descripción: Configurar `storage` y `mail` con volúmenes y variables de entorno (`.env`) para credenciales.
  - DoD: Los contenedores de MinIO y Postfix se inician correctamente. Se puede acceder a la consola de MinIO.

- Conexión a la BD y Alembic
  - Descripción: En `core/database.py`, establecer conexión con el contenedor de BD. Inicializar Alembic para gestionar migraciones.
  - DoD: La API se conecta a la base de datos y Alembic puede generar una primera migración vacía.

## Fase 1: Construcción del Núcleo (2 Semanas)
Objetivo: Implementar los módulos de negocio fundamentales con Arquitectura por Capas.

### Sprint 1: Módulo de Autenticación y Catálogos

- Construir Módulo `auth`
  - Descripción: Crear capas `models.py` (usuarios, roles), `schemas.py`, `crud.py`, `service.py` (hashing), `router.py` (login/token).
  - DoD: Un usuario puede registrarse y obtener un token JWT válido. Rutas protegidas.

- Primera Migración de BD
  - Descripción: Crear y aplicar migración de Alembic para tablas de `auth`.
  - DoD: Tablas de usuarios y roles existen en PostgreSQL.

- Construir Módulo `catalogos`
  - Descripción: Implementar CRUD completo (Proveedores, Almacenes, Marcas, Modelos) siguiendo capas.
  - DoD: Endpoints de datos maestros funcionales y probados.

- Crear Suite de Pruebas
  - Descripción: Configurar `pytest`. Escribir pruebas de integración para login y CRUD de catálogo (setup/teardown de BD de prueba).
  - DoD: `pytest` valida autenticación y catálogos.

### Sprint 2: Módulos de Vehículos y Neumáticos

- Construir Módulo `vehiculos`
  - Descripción: Gestionar vehículos, tipos de vehículo y configuraciones de ejes con patrón de capas.
  - DoD: CRUD completo de vehículos y configuraciones.

- Construir Módulo `neumaticos`
  - Descripción: Gestión de neumáticos (sin eventos aún). Foco en registro inicial y consulta de estado.
  - DoD: Registro de neumático nuevo y consulta detallada.

- Crear Migraciones de BD
  - Descripción: Generar y aplicar migraciones para tablas de vehículos y neumáticos.
  - DoD: Tablas del núcleo de negocio existen en BD.

- Ampliar Cobertura de Pruebas
  - Descripción: Pruebas unitarias en `services` y de integración en endpoints.
  - DoD: Cobertura alta en módulos principales.

## Fase 2: Implementación de Funcionalidades Avanzadas (4 Semanas)
Objetivo: Transformar la API en una plataforma inteligente y proactiva.

### Sprint 3: Módulo de Imágenes con MinIO

- Evolucionar la BD
  - Descripción: Crear `imagenes_evento` y relación con `eventos_neumaticos` vía Alembic.
  - DoD: BD lista para URLs de imágenes.

- Crear `StorageService`
  - Descripción: En `core/storage.py`, encapsular lógica de MinIO (subir, obtener URL, eliminar).
  - DoD: Servicio reutilizable e inyectable en otros servicios.

- Integrar en Módulo de Eventos
  - Descripción: Implementar `eventos`. En `EventoService`, al registrar inspección, subir imagen y guardar URL.
  - DoD: Flujo completo de imagen en MinIO y URL en BD.

- Escribir Pruebas de Carga
  - Descripción: Pruebas que simulan carga de archivos y verifican el flujo.
  - DoD: Funcionalidad de imágenes robusta validada.

### Sprint 4: Implementación de la IA Predictiva

- Preparar la BD para IA
  - Descripción: Añadir campos de predicción a `neumaticos` (p. ej., `vida_util_restante_km`) con migración.
  - DoD: BD lista para resultados de IA.

- Entrenar Modelo v1
  - Descripción: Usar `backup_completo.dump` para entrenar el primer modelo; guardar `modelo_rul.pkl`.
  - DoD: Archivo de modelo funcional disponible.

- Crear e Integrar `PredictionService`
  - Descripción: Servicio que carga el modelo y ofrece predicción. Integrarlo en `EventoService` tras cada inspección.
  - DoD: Predicción de vida útil se genera y persiste tras nuevos datos de desgaste.

### Sprint 5: Motor de Eventos (MCP) y WebSockets

- Construir el `EventBroker`
  - Descripción: Sistema publish/subscribe en `core/events.py`.
  - DoD: Sistema nervioso central listo.

- Integrar con los Servicios
  - Descripción: Modificar servicios clave (`EventoService`, `NeumaticoService`, etc.) para publicar eventos tras operaciones.
  - DoD: Acciones de negocio generan eventos desacoplados.

- Implementar `WebSocketListener`
  - Descripción: Listener que se suscribe al broker y retransmite en tiempo real por WebSockets.
  - DoD: Cambios en BD se reflejan instantáneamente en clientes conectados.

### Sprint 6: Notificaciones Proactivas y Finalización

- Implementar Canales Gratuitos
  - Descripción: Integrar Postfix (Email) y Telegram. Crear `NotificationListener` que se suscribe a eventos críticos.
  - DoD: La API envía alertas proactivas por email y Telegram.

- Evolucionar BD de Usuarios
  - Descripción: Añadir `telegram_chat_id` a `usuarios` vía migración.
  - DoD: BD lista para notificaciones personalizadas.

- Pruebas de Flujo Completo
  - Descripción: Tests end-to-end: inspección con desgaste crítico -> actualiza BD -> predicción -> WebSocket -> notificación.
  - DoD: Robustez y funcionamiento integral garantizados.

- Revisión de Seguridad y Documentación
  - Descripción: Revisar seguridad de endpoints y documentar en OpenAPI (Swagger).
  - DoD: API lista para producción.

## Fase 3: Plan de Acción para el Frontend

- Core y Autenticación
  - Descripción: Setup del proyecto frontend (`neucloud-frontend`), conexión con la API, login y rutas protegidas.

- Gestor de MCP (WebSockets)
  - Descripción: Implementar cliente que se conecta al `WebSocketListener` para actualizaciones en tiempo real.

- Vistas del Operador
  - Descripción: Interfaces para registrar eventos, incluyendo subida de imágenes.

- Vistas del Gestor
  - Descripción: Dashboard, tabla de inventario (datos en tiempo real y predicciones de IA) y CRUDs de catálogos.

- Centro de Notificaciones
  - Descripción: UI para ver historial de alertas y configurar datos de contacto (por ejemplo `telegram_chat_id`).

# Plan de Corrección Sistemática - API GesNeu
 A partir de ahora en Español

## Objetivo Principal
**PRIORIDAD CRÍTICA**: Asegurar que todos los modelos SQLModel estén exactamente alineados con `ESQUEMA_COMPLETO_BD.md` (esquema PostgreSQL real) y que todos los tests reflejen correctamente los modelos corregidos.

## ⚠️ PRINCIPIO FUNDAMENTAL
**ESQUEMA_COMPLETO_BD.md ES LA ÚNICA FUENTE DE VERDAD**
- Todos los modelos deben coincidir EXACTAMENTE con este esquema
- Nombres de tablas, campos, tipos, constraints deben ser IDÉNTICOS
- La API se adapta al esquema existente, NUNCA al revés

### Filosofía de trabajo (DB-first, estricto)
- Los modelos Python son un espejo 1:1 del esquema PostgreSQL. No “aproximaciones”.
- Los valores por defecto y checks deben usar `server_default` y expresiones exactamente como en PostgreSQL.
- Los enums se mapean a `SQLAlchemy Enum` con `name` EXACTO al tipo en PostgreSQL.
- Los índices deben incluir condiciones parciales, funciones y unicidad exactamente como el esquema (incluyendo nombres).
- No se cambian tablas ni migraciones para “acomodar” modelos: el código se adapta a la BD.

## Problema Crítico Identificado
**Error UUID en SQLAlchemy**: Los modelos que usan `sa_column=Column(PG_UUID(as_uuid=True), primary_key=True)` junto con `Field(primary_key=True)` causan el error `'str' object has no attribute 'hex'`.

### Solución Aplicada Exitosamente en Auth
```python
# ANTES (ERROR)
id: UUID = Field(
    default_factory=uuid4, 
    primary_key=True,
    sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
)

# DESPUÉS (CORRECTO)
id: UUID = Field(default_factory=uuid4, primary_key=True)
```

## Plan de Ejecución por Fases

### FASE 1: VERIFICACIÓN OBLIGATORIA DE ALINEACIÓN CON ESQUEMA_COMPLETO_BD.md

#### 1.1 PROCESO OBLIGATORIO ANTES DE CUALQUIER CORRECCIÓN
1. **Leer ESQUEMA_COMPLETO_BD.md** para cada tabla
2. **Comparar campo por campo** con modelos SQLModel existentes
3. **Identificar discrepancias** en nombres, tipos, constraints
4. **Corregir modelos** para coincidir EXACTAMENTE con esquema PostgreSQL
5. **Solo después** corregir problemas técnicos como UUID

Checklist por tabla (pasos rápidos)
- [ ] Nombres: tabla/columnas idénticos a `ESQUEMA_COMPLETO_BD.md`
- [ ] Tipos: `Numeric(p,s)`, `SmallInt`, `TIMESTAMP(timezone=True)`, `Text`, `String(n)`, etc.
- [ ] Defaults: `server_default` mismo literal/expresión (ej. `now()`, `'PEN'::character varying`)
- [ ] Enums: `SQLAlchemyEnum(MiEnum, name="tipo_en_postgres")`
- [ ] CHECKs: expresiones y nombres idénticos
- [ ] UNIQUE/PRIMARY: nombres y columnas idénticos
- [ ] FK: `foreign_key="tabla.columna"` con política ON DELETE si aplica (cuando se use SQLAlchemy puro)
- [ ] Índices: nombres idénticos, columnas, parciales (`postgresql_where`), funcionales (ej. `text('f_immutable_lower_unaccent(col)')`), `unique=True` si corresponde

### FASE 2: Corrección de Modelos UUID (SOLO después de Fase 1)

#### 1.1 Módulos con Problemas UUID Identificados
- ✅ **Auth** - Corregido exitosamente
- 🔄 **Neumáticos** - En corrección
- ❌ **Vehículos** - Pendiente corrección
- ❌ **Catálogos** - Pendiente verificación
- ❌ **Inventario** - Pendiente verificación
- ❌ **Eventos** - Pendiente verificación
- ❌ **Garantías** - Pendiente verificación
- ❌ **Alertas** - Pendiente verificación
- ❌ **Bitácoras** - Pendiente verificación

#### 1.2 Patrón de Corrección UUID
Para cada modelo con problemas UUID:
1. Identificar campos con `sa_column=Column(PG_UUID(as_uuid=True), primary_key=True)`
2. Reemplazar por `Field(default_factory=uuid4, primary_key=True)`
3. Para foreign keys: `Field(foreign_key="tabla.id")` en lugar de `sa_column=Column(PG_UUID...)`
4. Simplificar campos de auditoría (`creado_por`, `actualizado_por`)

Notas importantes UUID
- Evitar mezclar `sa_column=Column(PG_UUID(...))` con `Field(primary_key=True)`.
- Patrón recomendado PK: `Field(default_factory=uuid4, primary_key=True)`.
- Para FK UUID: `Field(default=None, foreign_key="tabla.id")`.

#### 1.3 Archivos con Problemas UUID Detectados
```
vehiculos/models.py - 5 ocurrencias
neumaticos/models.py - múltiples ocurrencias
neumaticos/models_fixed.py - múltiples ocurrencias
```

### FASE 2: Verificación de Alineación con Esquema BD

#### 2.1 Verificar Cada Modelo Contra ESQUEMA_COMPLETO_BD.md
Para cada tabla en el esquema:
1. **Nombres de tabla**: Exactos (ej: `usuarios`, `tipos_vehiculo`, `neumaticos`)
2. **Nombres de campos**: Exactos según esquema PostgreSQL
3. **Tipos de datos**: Alineados con tipos PostgreSQL
4. **Constraints**: Unique, Check, Foreign Keys según esquema
5. **Enums**: Valores exactos según esquema
6. **Índices**: Inclusión de `Index(name, ...)` con `postgresql_where` y funciones si aplica

Patrones concretos usados (ejemplos)
- Enums PostgreSQL
  ```python
  from sqlalchemy import Enum as SQLAlchemyEnum
  estado_actual: EstadoEnum = Field(sa_column=Column(
      SQLAlchemyEnum(EstadoEnum, name="estado_neumatico_enum"),
      nullable=False,
      server_default=text("'EN_STOCK'::estado_neumatico_enum")
  ))
  ```
- Timestamps con zona
  ```python
  creado_en: datetime = Field(sa_column=Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")))
  ```
- Defaults exactos
  ```python
  moneda: str = Field(sa_column=Column(String(3), server_default=text("'PEN'::character varying")))
  ```
- Índice funcional parcial único
  ```python
  Index(
      'idx_modelos_unique',
      'fabricante_id',
      text('f_immutable_lower_unaccent(nombre_modelo::text)'),
      'medida',
      unique=True,
      postgresql_where=text('fabricante_id IS NOT NULL')
  )
  ```

#### 2.2 Tablas Críticas para Verificar
- `usuarios` - ✅ Verificado y corregido
- `roles` - ✅ Verificado y corregido
- `permisos` - ✅ Verificado y corregido (constraint único funcional)
- `usuarios_roles` - ✅ Verificado y corregido
- `roles_permisos` - ✅ Verificado y corregido
- `neumaticos` - 🔄 En verificación
- `modelos_neumatico` - 🔄 En verificación
- `fabricantes_neumatico` - 🔄 En verificación
- `vehiculos` - ❌ Pendiente
- `tipos_vehiculo` - ❌ Pendiente
- `configuraciones_eje` - ❌ Pendiente
- `posiciones_neumatico` - ❌ Pendiente

### FASE 3: Corrección de Tests

#### 3.1 Tests de Auth ✅ (Parcialmente Corregido)
- ✅ `test_permiso_unique_constraint` - Corregido manejo de sesión después de IntegrityError
- ❌ Otros tests pendientes de verificación completa

#### 3.2 Patrón de Corrección de Tests
1. **Verificar nombres de modelos**: Usar nombres exactos de tablas PostgreSQL
2. **Verificar campos**: Usar nombres exactos de campos según esquema
3. **Verificar enums**: Usar valores exactos según esquema
4. **Manejo de sesiones**: Rollback después de excepciones esperadas
5. **Factories**: Alinear con campos reales de modelos
6. **Fixtures DB**: Preparar datos en BD respetando constraints reales (usar `rollback` tras tests que esperan `IntegrityError`).
7. **Enums**: Validar creación, default y filtros por enum (incl. índices parciales por enum si aplica).

#### 3.3 Tests Pendientes de Corrección
- `test_auth_complete.py` - Verificación completa pendiente
- `test_bitacoras_complete.py` - Alineación con modelos
- Tests de otros módulos según se corrijan modelos

### FASE 4: Verificación Final

#### 4.1 Pruebas de Integración
1. **Carga de aplicación**: Sin errores de metadata SQLAlchemy
2. **Endpoints funcionales**: 20/20 endpoints funcionando
3. **Tests unitarios**: Todos los tests pasan
4. **Alineación BD**: Modelos 100% alineados con esquema PostgreSQL

#### 4.2 Checklist Final
- [ ] Todos los modelos cargan sin errores UUID
- [ ] Aplicación arranca sin conflictos de metadata
- [ ] Tests de Auth pasan completamente
- [ ] Tests de otros módulos pasan
- [ ] Endpoints responden correctamente
- [ ] Alineación 100% con ESQUEMA_COMPLETO_BD.md

### Criterios de Aceptación por Módulo
- **Modelos**: 0 diferencias con `\d+` de PostgreSQL (campos, tipos, defaults, checks, índices, FKs).
- **Carga app**: Importa sin warnings/errores de metadata.
- **Tests**: Pasan y los datos cumplen constraints reales.
- **Endpoints**: CRUD básico sin errores de integridad.

## Comandos de Verificación

### Verificar Problemas UUID
PowerShell (Windows)
```powershell
# Buscar usos problemáticos de PG_UUID
Get-ChildItem -Recurse ges_neu_api\modules | Select-String -Pattern "sa_column=Column(PG_UUID"

# Verificar import del app (carga rápida)
python -c "from ges_neu_api.main import app; print('✅ App carga correctamente')"

# Ejecutar tests rápidos por módulo
python -m pytest tests/auth -q
python -m pytest tests/neumaticos -q
```

### Ejecutar Tests Específicos
```bash
# Test específico que falló
python -m pytest tests/test_auth_complete.py::TestPermisoModel::test_permiso_unique_constraint -v

# Todos los tests de Auth
python -m pytest tests/test_auth_complete.py -v

# Tests completos
python -m pytest tests/ -v
```

### Verificar Carga de Aplicación
```bash
python -c "from ges_neu_api.main import app; print('✅ App carga correctamente')"
```

## Notas Importantes

### Principios Fundamentales
1. **Database-First**: La API se adapta al esquema PostgreSQL existente, NUNCA al revés
2. **ESQUEMA_COMPLETO_BD.md es la fuente de verdad**: Todos los modelos deben coincidir exactamente
3. **No modificar BD**: Solo adaptar modelos y código para coincidir con BD existente
4. **Tests alineados**: Los tests deben reflejar exactamente los modelos corregidos

### Errores Comunes a Evitar
1. **Configuración UUID mixta**: No mezclar `sa_column` con `primary_key=True`
2. **Nombres incorrectos**: Usar nombres exactos de tablas y campos según esquema
3. **Enums incorrectos**: Usar valores exactos según esquema PostgreSQL
4. **Manejo de sesiones en tests**: Hacer rollback después de excepciones esperadas

### Estado Actual (4 Septiembre 2025)
- **Auth**: ✅ Modelos corregidos, tests parcialmente corregidos
- **Neumáticos**: ✅ `FabricanteNeumatico` y `ModeloNeumatico` alineados; ✅ `Neumatico` alineado con tipos, defaults, CHECKs e índices (incluidos parciales y funcionales). Pendiente ejecutar suite de tests completa.
- **Vehículos**: ❌ Pendiente corrección UUID y alineación total contra esquema (campos, índices y checks).
- **Catálogos/Inventario/Eventos/Garantías/Alertas/Bitácoras**: ❌ Pendiente verificación sistemática DB-first.
- **Aplicación**: ✅ Debe cargar sin conflictos de metadata tras correcciones (ver comando de verificación).
- **Tests**: 🔄 Corrección en progreso.

---

**Última actualización**: 4 Septiembre 2025 - 18:12
**Próximo paso**: Ejecutar verificación de carga y tests de Neumáticos; iniciar corrección en `vehiculos/models.py` (UUID + alineación completa)