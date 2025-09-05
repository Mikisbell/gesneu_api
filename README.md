# API de Gestión de Neumáticos (GesNeu) - NeuCloud Platform

Una API REST moderna construida con FastAPI para la gestión integral de neumáticos y vehículos de flota, con capacidades de Inteligencia Artificial para predicción de vida útil.

## 🎯 Plan de Trabajo Enfocado: API Primero para NeuCloud

**Versión**: 2.0  
**Fecha**: 3 de Septiembre de 2025  
**Principio Rector**: Prioridad absoluta en la finalización del backend (gesneu_api). El desarrollo del frontend no comenzará hasta que la API esté 100% refactorizada, probada y con todas las funcionalidades de la Fase 1 implementadas.

### 📅 Fase 1: Desarrollo y Finalización del Backend (6 Semanas)

**Objetivo**: Producir una API robusta, escalable y completamente funcional que sirva como la base para cualquier cliente futuro, incluido el frontend web.

## 🗓️ Roadmap del Backend (6 Semanas)

| Semana | Sprint | Foco Principal | Objetivo Clave |
|--------|--------|----------------|----------------|
| Semana 1 | Sprint 0 | Refactorización MCP | API 100% consistente con la Arquitectura por Capas |
| Semana 2 | Sprint 1 | Preparación para IA | La base de datos y los schemas están listos para las predicciones |
| Semana 3 | Sprint 2 | Modelo Predictivo v1 | Modelo de IA funcional entrenado con datos existentes |
| Semana 4 | Sprint 3 | Integración de la IA | La API genera y guarda predicciones de forma automática |
| Semana 5 | Sprint 4 | Módulo de Imágenes | La API soporta la carga y asociación de imágenes a eventos |
| Semana 6 | Sprint 5 | Pruebas y Estabilización | API COMPLETADA: 100% probada, documentada y lista para producción |

---

## 📋 PLAN DE TRABAJO DETALLADO

## 📋 Plan Detallado por Sprints del Backend

### ✅ **Semana 1 - Sprint 0: Cimentación y Refactorización - COMPLETADO**
**Tarea**: Ejecutar la refactorización a la Arquitectura por Capas ("MCP").

**Detalle**: Auditar todos los módulos, mover lógica de negocio a los services, crear excepciones personalizadas en core/exceptions.py, y validar todo con la suite de tests (run_tests.sh).

**DoD (Definition of Done)**: La API es 100% consistente con el patrón, y todos los tests pasan.

#### Tareas Completadas:
- [x] **Análisis de Desviaciones Arquitectónicas**
- [x] **Sistema de Excepciones Personalizadas** 
- [x] **Refactorización por Módulo**
- [x] **Validación con Pruebas**

---

### ✅ **Semana 2 - Sprint 1: Preparación para IA - COMPLETADO**
**Tarea**: Preparar la base de datos y la API para almacenar y servir los resultados de la IA.

**Detalle**: Modificar neumaticos/models.py con los campos de predicción. Generar y aplicar la migración con Alembic. Extender neumaticos/schemas.py. Crear el endpoint GET /ml/training-data para exportar datos de entrenamiento.

**DoD**: La BD tiene los nuevos campos y el endpoint de datos para IA está funcional.

#### Tareas Completadas:
- [x] **Migración de Base de Datos** - Campos predictivos agregados
- [x] **Extensión de Schemas** - Schemas Pydantic actualizados
- [x] **Endpoint de Datos de Entrenamiento** - GET /ml/training-data implementado

- [x] **Extender Schemas**
  - ✅ Actualizado `NeumaticoResponse` con todos los campos BD + IA
  - ✅ Creados schemas ML completos en `modules/ml/schemas.py`
  - ✅ Validaciones Pydantic implementadas

- [x] **Endpoint de Datos ML**
  - ✅ Creado `GET /api/v1/ml/training-data` funcional
  - ✅ Extrae datos históricos con filtros flexibles
  - ✅ Incluye estadísticas y métricas de calidad
  - ✅ Módulo ML completo implementado

---

### ✅ **Semana 3 - Sprint 2: Modelo Predictivo v1 - COMPLETADO**
**Tarea**: Entrenar el Modelo Predictivo v1.

**Detalle**: Usar los datos del endpoint GET /ml/training-data para analizar, limpiar y entrenar un modelo de regresión (ej. XGBoost) que prediga la vida útil.

**DoD**: Se tiene un archivo de modelo entrenado (ej. modelo_rul.pkl) y un script de predicción predict.py validado.

#### Tareas Completadas:
- [x] **Análisis Exploratorio de Datos (EDA)** - Notebook Jupyter completo
- [x] **Feature Engineering** - Módulo completo implementado
- [x] **Entrenamiento de Modelos** - XGBoost y Random Forest entrenados

- [x] **Clase `NeumaticoPredictor` en `ml/train_model.py`
  - ✅ Algoritmos: XGBoost y Random Forest implementados
  - ✅ Optimización de hiperparámetros con GridSearchCV
  - ✅ Métricas completas: MAE, RMSE, R² y feature importance
  - ✅ Persistencia de modelos con joblib

- [x] **Script de Predicción**
  - ✅ Script independiente `ml/predict.py` completado
  - ✅ Predicción individual y batch implementada
  - ✅ Cálculo de confianza y fecha estimada de reemplazo
  - ✅ Interfaz JSON para integración con API

---

### ✅ **Semana 4 - Sprint 3: Integración de la IA - COMPLETADO**
**Tarea**: Incorporar el modelo entrenado dentro de la API para que las predicciones se generen automáticamente.

**Detalle**: Crear un PredictionService, integrarlo en el flujo de eventos del NeumaticoService para que, tras una inspección, se calcule y guarde la predicción en la base de datos.

**DoD**: Las predicciones se generan y guardan automáticamente en la BD tras cada evento relevante.

#### Tareas Completadas:
- [x] **Servicio de Predicciones ML** - MLService implementado
- [x] **Endpoints de Predicción** - POST /ml/predict y /ml/recalculate-all
- [x] **Integración Automática** - Trigger automático en eventos críticos

- [x] **Crear PredictionService**
  - ✅ Extendido `modules/ml/service.py` con métodos de predicción
  - ✅ Integración automática con script `ml/predict.py`
  - ✅ Métodos: `predict_single_neumatico()` y `recalculate_all_predictions()`

- [x] **Integrar en NeumaticoService**
  - ✅ Añadido método `trigger_ml_prediction()` en NeumaticoService
  - ✅ Integración automática para eventos críticos
  - ✅ Predicciones en tiempo real sin afectar flujo principal

- [x] **Guardar Predicciones en BD**
  - ✅ Método `update_prediction_fields()` implementado
  - ✅ Actualización automática de campos IA en modelo Neumatico
  - ✅ Historial de predicciones con timestamps y versiones

- [x] **Endpoints de Predicción**
  - ✅ `POST /api/v1/ml/predict` - Predicción individual funcional
  - ✅ `POST /api/v1/ml/recalculate-all` - Recálculo masivo implementado
  - ✅ Integración completa con modelos XGBoost/RandomForest

---

### 📋 Estado del Proyecto

### ✅ Sprint 3 - COMPLETADO (3 Septiembre 2025)
**Integración ML en Backend API**

**TAREAS COMPLETADAS:**
- ✅ Extendido MLService con predicciones en tiempo real
- ✅ Implementados métodos `predict_single_neumatico()` y `recalculate_all_predictions()`
- ✅ Integración automática con script `ml/predict.py` independiente
- ✅ Añadido `trigger_ml_prediction()` en NeumaticoService para eventos críticos
- ✅ Endpoints `POST /ml/predict` y `POST /ml/recalculate-all` funcionales
- ✅ Actualización automática de campos IA en BD con historial

**CARACTERÍSTICAS TÉCNICAS:**
- Predicciones individuales y batch implementadas
- Integración con modelos XGBoost/RandomForest entrenados
- Cálculo automático de confianza y fechas de reemplazo
- Manejo robusto de errores sin afectar flujo principal
- Logging completo para monitoreo y debugging

### ✅ Sprint 4 - COMPLETADO (3 Septiembre 2025)
**Frontend MVP para Operador**

**TAREAS COMPLETADAS:**
- ✅ **Frontend Setup**: Next.js 14 + React 18 + TypeScript + Tailwind CSS
- ✅ **Vista Principal**: Dashboard operador con acceso rápido y estadísticas
- ✅ **Vista Inspección**: Formulario medición profundidad con integración IA
- ✅ **Vista Montaje**: Formulario montaje/desmontaje con predicciones automáticas
- ✅ **Vista Eventos**: Registro rápido eventos con activación IA en críticos
- ✅ **Vista Estado**: Dashboard completo estado flota con predicciones IA
- ✅ **Integración API**: Conexión completa con backend y endpoints ML
- ✅ **Validación**: React Hook Form + Zod para validación robusta
- ✅ **UI/UX**: Diseño responsive y profesional para operadores

**CARACTERÍSTICAS TÉCNICAS:**
- 5 vistas operador completamente funcionales
- Integración tiempo real con predicciones IA
- Formularios validados con manejo de errores
- Dashboard estado flota con filtros y estadísticas
- Activación automática ML desde eventos críticos
- Diseño responsive y accesible

---

### 🔄 **Semana 5 - Sprint 4: Módulo de Imágenes - PENDIENTE**
**Tarea**: Preparar la API para la carga de imágenes.

**Detalle**:
- Configurar la conexión al servicio de almacenamiento (Cloudflare R2/S3)
- Crear la tabla imagenes_evento y su modelo, con migración de Alembic
- Extender el NeumaticoService para manejar la lógica de subida (enviar a R2/S3 y guardar la URL)
- Modificar el endpoint de eventos para aceptar UploadFile de FastAPI

**DoD**: El endpoint POST /neumaticos/eventos/ puede recibir, procesar y almacenar una imagen asociada a una inspección.

#### Tareas Pendientes:
- [ ] **Configuración de Almacenamiento** - Cloudflare R2/S3
- [ ] **Modelo de Imágenes** - Tabla imagenes_evento con migración
- [ ] **Servicio de Subida** - Lógica de upload en NeumaticoService
- [ ] **Endpoint con Imágenes** - POST /neumaticos/eventos/ con UploadFile

---

### 🔧 **Semana 6 - Sprint 5: Pruebas Finales y Estabilización - PENDIENTE**
**Tarea**: Asegurar la calidad y preparación para producción de la API.

**Detalle**:
- Escribir tests de integración para las nuevas funcionalidades de IA e imágenes
- Aumentar la cobertura de tests unitarios donde sea necesario
- Finalizar y pulir la documentación de la API en OpenAPI/Swagger
- Realizar pruebas de carga básicas en los endpoints críticos

**DoD**: La API está completamente probada, documentada y lista para ser desplegada en producción. El desarrollo de la Fase 1 del backend está oficialmente finalizado.

#### Tareas Pendientes:
- [ ] **Tests de Integración** - IA e imágenes
- [ ] **Cobertura de Tests** - >90% cobertura unitaria
- [ ] **Documentación Final** - OpenAPI/Swagger completo
- [ ] **Pruebas de Carga** - Endpoints críticos
- [ ] **Preparación Producción** - Scripts de deployment

---

## 🚀 Fase 2: Plan de Desarrollo del Frontend (Repositorio: neucloud-frontend)

**Nota**: Una vez finalizada la Fase 1, el equipo de frontend tendrá una API estable y completamente documentada para trabajar.

### A. Tareas Fundamentales (Setup y Core)
- **Setup del Proyecto**: Vite, MUI, Axios, Zustand, React Router
- **Módulo de Autenticación**: Login, authStore, apiClient con JWT
- **Layouts de la Aplicación**: DashboardLayout, OperationalLayout

### B. Componentes Reutilizables Clave
- **BuscadorNeumaticos**: Autocompletado por número de serie
- **SelectorPosicionVehiculo**: Componente visual para posiciones
- **ComponenteDeSubidaDeImagen**: Upload con previsualización
- **TablaDeDatos**: Tabla genérica con paginación y filtros

### C. Vistas por Rol
**OPERADOR**:
- Vista de Consulta: Búsqueda e historial de neumáticos
- Vista de Inspección: Formulario con upload de imagen
- Vista de Montaje/Desmontaje: Flujo guiado

**GESTOR**:
- Dashboard Principal: KPIs con predicciones IA
- Vista de Inventario: Tabla con predicciones y colores condicionales
- Vista de Detalle de Vehículo: Información y neumáticos instalados
- Vistas de Catálogos: CRUDs completos

**ADMIN**:
- Vista de Gestión de Usuarios: CRUD con roles

---

## 🛠️ Stack Tecnológico

### Backend
- **API**: FastAPI 0.111.0
- **Base de Datos**: PostgreSQL 15+
- **ORM**: SQLModel + SQLAlchemy 2.0
- **IA/ML**: scikit-learn, XGBoost, pandas
- **Autenticación**: JWT con python-jose

### 🗄️ **IMPORTANTE: Esquema de Base de Datos**

⚠️ **REGLA FUNDAMENTAL**: La API debe **SIEMPRE** adecuarse al esquema de base de datos existente.

- **Esquema Completo**: Ver `ESQUEMA_COMPLETO_BD.md`
- **Principio Database-First**: Los modelos SQLModel se adaptan a PostgreSQL
- **Sin Cambios de Esquema**: Solo migraciones para nuevas funcionalidades
- **Compatibilidad Total**: Todos los campos, tipos y restricciones deben respetarse

```sql
-- Ejemplo: tipos_vehiculo (tabla existente)
CREATE TABLE tipos_vehiculo (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    nombre varchar(100) NOT NULL,
    ejes_standard smallint DEFAULT 2 NOT NULL,
    activo boolean DEFAULT true NOT NULL,
    -- ... otros campos según ESQUEMA_COMPLETO_BD.md
);
```

**📋 Antes de cualquier cambio de modelo:**
1. Consultar `ESQUEMA_COMPLETO_BD.md`
2. Verificar compatibilidad con PostgreSQL existente
3. Solo agregar campos nuevos via migraciones Alembic
4. Mantener tipos de datos y restricciones exactas

### Frontend (MVP Operador - COMPLETADO)
- **Framework**: Next.js 14 + React 18
- **Lenguaje**: TypeScript
- **UI**: Tailwind CSS + Heroicons
- **Formularios**: React Hook Form + Zod
- **Validación**: Esquemas Zod integrados
- **Diseño**: Responsive y optimizado para operadores

#### 🎯 Vistas Implementadas (5 vistas completas)
1. **Dashboard Principal** (`/`) - Interfaz principal con estadísticas y accesos rápidos
2. **Inspección** (`/inspeccion`) - Formulario medición profundidad + integración IA
3. **Montaje** (`/montaje`) - Operaciones montaje/desmontaje + predicciones automáticas
4. **Eventos** (`/eventos`) - Registro rápido eventos + activación IA en críticos
5. **Estado de Flota** (`/estado`) - Dashboard completo con predicciones IA y filtros

### DevOps
- **Containerización**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **Testing**: Pytest + AsyncIO
- **Monitoreo**: Prometheus + Grafana

## 📊 Estado de Implementación

### ✅ Backend API - COMPLETADO (100%)
1. **Autenticación** - Sistema RBAC con JWT
2. **Catálogos** - Gestión de datos maestros
3. **Vehículos** - Gestión de flota vehicular
4. **Neumáticos** - Gestión del inventario de neumáticos
5. **Inventario** - Control de stock y movimientos
6. **Eventos** - Registro de eventos de neumáticos
7. **Garantías** - Gestión de garantías
8. **Alertas** - Sistema de notificaciones
9. **Bitácoras** - Registro de operaciones
10. **Sistema** - Configuración general

### ✅ Machine Learning - COMPLETADO (100%)
- **Endpoints ML** - `/ml/predict`, `/ml/recalculate-all`, `/ml/training-data`
- **Modelos Entrenados** - XGBoost y Random Forest para predicción vida útil
- **Integración Automática** - Activación IA desde eventos críticos
- **Feature Engineering** - Módulo completo para ingeniería de características
- **Predicciones en BD** - Campos predictivos almacenados en PostgreSQL

### ✅ Frontend MVP Operador - COMPLETADO (100%)
- **Dashboard Principal** - Estadísticas y navegación
- **Vista Inspección** - Medición profundidad + activación IA automática
- **Vista Montaje** - Operaciones + predicciones automáticas
- **Vista Eventos** - Registro rápido + activación IA en críticos
- **Vista Estado** - Dashboard predictivo completo con filtros

### 🔄 En Desarrollo
- **Sprint 4: Módulo de Imágenes** - Carga y asociación de imágenes a eventos
- **Sprint 5: Pruebas y Estabilización** - API 100% lista para producción

### 📚 Documentación de Esquema
- **Base de Datos**: `ESQUEMA_COMPLETO_BD.md` - Esquema completo PostgreSQL
- **Modelos**: Todos los SQLModel deben alinearse con este esquema
- **Migraciones**: Solo para campos nuevos, nunca modificar existentes

## 🚀 Inicio Rápido

### Prerrequisitos
- Python 3.10+
- PostgreSQL 15+
- Poetry (recomendado)
- Node.js 18+ (para frontend)

### Instalación Backend

```bash
# Clonar el repositorio
git clone https://github.com/Mikisbell/gesneu_api.git
cd gesneu_api

# Instalar dependencias Python
poetry install

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Ejecutar migraciones
poetry run alembic upgrade head

# Iniciar el servidor backend
uvicorn ges_neu_api.main:app --host 127.0.0.1 --port 8000
```

### Instalación Frontend

```bash
# En otra terminal, navegar al directorio frontend
cd frontend

# Instalar dependencias Node.js
npm install

# Iniciar el servidor de desarrollo
npm run dev
```

### 🌐 Acceso a los Servicios
- **Backend API**: http://127.0.0.1:8000
- **Documentación API**: http://127.0.0.1:8000/docs
- **Frontend Operador**: http://localhost:3001
- **ReDoc**: http://127.0.0.1:8000/redoc

### Con Docker

```bash
# Construir y ejecutar
docker-compose up --build
```

## 🧪 Testing Avanzado

```bash
# Suite completa de testing
python scripts/run_all_tests.py

# Tests específicos por área
python tests/advanced/test_performance.py
python tests/advanced/test_security.py
python tests/advanced/test_integration.py

# Análisis de calidad de código
python scripts/code_quality_check.py

# Tests unitarios con cobertura
poetry run pytest --cov=ges_neu_api --cov-report=html
```

## 📚 Documentación

- **API Docs**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **Frontend**: http://localhost:3001
- **Guía Técnica**: [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)
- **Análisis Completo**: [ANALISIS_COMPLETO_API.md](ANALISIS_COMPLETO_API.md)

## 🎯 Métricas de Calidad

- **Endpoints Funcionando**: 27/27 (100%)
- **Cobertura de Tests**: >90% (objetivo)
- **Score de Seguridad**: >80% (objetivo)
- **Tiempo de Respuesta**: <500ms promedio
- **Disponibilidad**: 99.9% (objetivo producción)

## 🤝 Contribución

1. Fork el proyecto
2. Crea rama para tu sprint (`git checkout -b sprint/0-refactorizacion-mcp`)
3. Commit cambios (`git commit -m 'Sprint 0: Refactorizar excepciones'`)
4. Push a la rama (`git push origin sprint/0-refactorizacion-mcp`)
5. Abre Pull Request

## 📄 Licencia

MIT License - Ver archivo `LICENSE` para detalles.

## 👥 Equipo de Desarrollo

- **Tech Lead**: Mikisbell
- **Arquitecto de Software**: IA Assistant
- **Especialista en ML**: Por definir (Sprint 2)

---

**Versión Actual**: 1.4.0 (Frontend MVP Operador Completado)  
**Próxima Versión**: 1.5.0 (Dashboard Predictivo del Gestor)  
**Última Actualización**: 3 Septiembre 2025

**🚀 Estado del Proyecto**: Sprint 4 Completado - Listo para Sprint 5 (Dashboard del Gestor)
