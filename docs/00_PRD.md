# 📘 Product Requirements Document — GesNeu API

> **Versión**: 1.0.0
> **Estado**: Vivo — refleja el estado del sistema al 2026-04-10
> **Reemplaza a**: `Requerimientos de Sistema API Ges_Neu_Final.pdf v2.1` (archivado, stack obsoleto)
> **Tipo de documento**: Producto (qué hace y para qué) — no arquitectura, no roadmap

---

## 📑 Índice

1. [Visión y problema](#1-visión-y-problema)
2. [Personas y casos de uso](#2-personas-y-casos-de-uso)
3. [Objetivos de negocio y KPIs](#3-objetivos-de-negocio-y-kpis)
4. [Contexto técnico y restricciones arquitectónicas](#4-contexto-técnico-y-restricciones-arquitectónicas)
5. [Alcance funcional (implementado)](#5-alcance-funcional-implementado)
6. [Compromisos próximo trimestre (Q2 2026)](#6-compromisos-próximo-trimestre-q2-2026)
7. [Requerimientos no funcionales](#7-requerimientos-no-funcionales)
8. [Out of scope](#8-out-of-scope)
9. [Visión futura (tentativa, sin compromiso)](#9-visión-futura-tentativa-sin-compromiso)
10. [Glosario y referencias](#10-glosario-y-referencias)

---

## 1. Visión y problema

### 1.1 Visión del producto

**GesNeu API** es un sistema integral de gestión del ciclo de vida de neumáticos en flotas vehiculares de carga pesada. Provee la única fuente de verdad operativa sobre cada neumático de la flota, desde su compra hasta su desecho final.

### 1.2 Problema de negocio

Las empresas de transporte de carga operan flotas donde los neumáticos representan:
- **Un costo operativo significativo** — segunda partida de gasto tras el combustible.
- **Un factor crítico de seguridad** — directamente ligado a siniestralidad vial.
- **Un activo rotativo complejo** — cada neumático tiene múltiples vidas (original + reencauches) con costos, kilometrajes y desgastes que deben rastrearse individualmente.

Sin un sistema dedicado, estas flotas típicamente enfrentan:
- **Imposibilidad de calcular CPK** (Costo por Kilómetro) real de cada neumático y modelo.
- **Decisiones de compra y reencauche a ciegas**, sin data de rendimiento histórico.
- **Riesgos de seguridad** por montajes indebidos (ej. neumáticos reencauchados en ejes de dirección).
- **Procesos manuales** propensos a error en registro de eventos (montaje, desmontaje, inspección, rotación).
- **Incumplimiento de políticas de seguridad** por falta de trazabilidad.

### 1.3 Solución

GesNeu API proporciona:
- **Trazabilidad total** de cada neumático como entidad individual con número de serie único.
- **Sistema de eventos centralizado** que captura todos los movimientos operativos del neumático.
- **Cálculo automático de KPIs** (CPK, desgaste, vida útil estimada) basado en datos reales.
- **Validaciones de seguridad** automáticas al registrar eventos críticos.
- **Reportes certificables** para cumplimiento operativo y legal.
- **Integración con ERPs** vía webhooks para propagar eventos a sistemas empresariales.

---

## 2. Personas y casos de uso

### 2.1 Personas del sistema

#### 👤 **ADMIN** — Administrador del Sistema
- **Perfil**: Responsable técnico del sistema dentro de la empresa. Gestor de IT o responsable de operaciones con permisos plenos.
- **Responsabilidades**:
  - Configuración inicial y mantenimiento del sistema.
  - Gestión de usuarios y asignación de roles.
  - Supervisión general de integridad de datos.
  - Configuración de catálogos base (modelos, fabricantes, almacenes).
  - Acceso a todos los módulos y reportes de auditoría.
- **Caso de uso típico**: "Configurar un nuevo almacén regional y darle acceso al gestor de esa zona."

#### 👤 **GESTOR** — Gestor de Flota / Inventario
- **Perfil**: Responsable de decisiones estratégicas sobre la flota de neumáticos. Jefe de mantenimiento o supervisor de operaciones.
- **Responsabilidades**:
  - Decisiones de compra, reencauche y desecho.
  - Análisis de rendimiento y KPIs (CPK, comparativo de marcas).
  - Gestión de catálogos operativos (modelos, proveedores, parámetros).
  - Supervisión de alertas críticas.
  - Configuración de políticas de rotación y reencauche.
- **Caso de uso típico**: "Revisar el reporte de CPK mensual para decidir con qué proveedor de reencauche seguir trabajando."

#### 👤 **OPERADOR** — Operador de Mantenimiento / Taller
- **Perfil**: Personal de taller y mantenimiento que ejecuta las operaciones físicas sobre los neumáticos en campo.
- **Responsabilidades**:
  - Registro de eventos operativos diarios (montaje, desmontaje, inspección, rotación).
  - Entrada de mediciones de profundidad y presión.
  - Consulta de estado y ubicación de neumáticos.
  - Recepción y atención de alertas operativas.
- **Caso de uso típico**: "Instalar un neumático en una posición del vehículo y registrar el kilometraje actual en el sistema."

### 2.2 Matriz de casos de uso principales

| Caso de uso | Disparador | Rol involucrado | Resultado esperado |
|-------------|-----------|------------------|---------------------|
| Registrar compra de neumático | Llegada de stock nuevo a almacén | GESTOR / ADMIN | Neumático creado en estado `EN_STOCK` con número de serie único |
| Montaje en vehículo | Cambio de neumático en taller | OPERADOR | Transición a `INSTALADO`, validación de posición compatible |
| Inspección programada | Revisión periódica (cada X km) | OPERADOR | Registro de profundidad y presión, posible generación de alerta |
| Desmontaje para reencauche | Neumático alcanza profundidad mínima | OPERADOR / GESTOR | Transición a `EN_REENCAUCHE`, cálculo de km acumulados |
| Análisis de CPK | Toma de decisión de compra | GESTOR | Reporte con CPK por modelo/marca/proveedor |
| Emisión de certificado | Auditoría operativa del vehículo | ADMIN / GESTOR | PDF con folio secuencial y evaluación real de operatividad |
| Alerta crítica de presión | Lectura fuera de rango | Sistema → OPERADOR | Notificación por email + alerta en dashboard |

---

## 3. Objetivos de negocio y KPIs

### 3.1 Objetivos estratégicos

1. **Optimizar costos operativos** mediante cálculo preciso de CPK y comparación de rendimiento entre proveedores.
2. **Aumentar la seguridad de la flota** con alertas automáticas y políticas de montaje validadas.
3. **Maximizar vida útil** de los neumáticos con seguimiento de desgaste y gestión informada del reencauche.
4. **Agilizar operaciones** automatizando el seguimiento y eliminando registros duplicados.
5. **Centralizar información** como única fuente de verdad del ciclo de vida completo del neumático.
6. **Facilitar integraciones** con ERPs y sistemas externos vía APIs y webhooks.

### 3.2 KPIs del sistema (fórmulas implementadas)

#### CPK — Costo por Kilómetro
```
CPK = (Costo_Compra + Σ Costo_Reencauches + Σ Costo_Reparaciones) / Km_Total_Acumulado
```
Se calcula por neumático individual y se agrega por modelo, marca o proveedor.

#### Tasa de Desgaste
```
Desgaste_mm_por_km = (Profundidad_Inicial − Profundidad_Actual) / Km_Recorridos
```
Permite proyectar vida útil y detectar desgaste anormal.

#### Vida Útil Restante Estimada
```
Km_Restantes = (Profundidad_Actual − Profundidad_Mínima) / Tasa_Desgaste
```
Base del módulo de forecast de compras.

### 3.3 KPIs de adopción (a medir post-lanzamiento)

| KPI | Objetivo | Cómo medir |
|-----|----------|------------|
| % eventos registrados en ≤ 24h del suceso | ≥ 90% | Diferencia entre `fecha_evento` y `creado_en` |
| Cobertura de inspecciones por flota | 100% mensual | Neumáticos con al menos 1 inspección en el mes |
| Reducción de desechos prematuros | −20% anual | Comparativo anual de `motivo_desecho` |
| Incremento de reencauches por carcasa | +15% anual | Promedio de `reencauches_realizados` al desecho |

---

## 4. Contexto técnico y restricciones arquitectónicas

> **Nota**: Los detalles técnicos completos están en [`01_ARQUITECTURA.md`](./01_ARQUITECTURA.md). Esta sección documenta **solo las restricciones arquitectónicas que afectan capacidades de producto**.

### 4.1 Stack actual (fuente de verdad)

| Capa | Tecnología | Implicancia de producto |
|------|-----------|-----------------------|
| Backend | Next.js 16 (App Router) + TypeScript | API y frontend en un solo deploy |
| ORM | Prisma 7 | Type safety end-to-end |
| Base de datos | PostgreSQL 15 (Supabase) | Hosting cloud, backups gestionados |
| Autenticación | NextAuth.js v5 (JWT) | Sesiones stateless, multi-dispositivo |
| Validación | Zod schemas | Validación runtime + tipos derivados |
| Deploy | Vercel (serverless) | Cold starts ~1s, sin jobs largos persistentes |
| Email | Resend API | Notificaciones transaccionales |

### 4.2 Decisiones arquitectónicas que definen capacidades

| Decisión | Implicancia de producto |
|----------|------------------------|
| **PWA (Progressive Web App)** | Operadores pueden inspeccionar neumáticos offline en el taller y sincronizar al volver a conectarse |
| **Single-tenant operativo** | Cada instancia atiende a **una sola empresa**. Multi-tenant está implementado a nivel de schema (columna `empresa_id` en tablas clave) pero no activado |
| **Event-driven architecture** | EventBus + observers para auditoría, notificaciones y analytics desacoplados |
| **Webhooks firmados** | Integración con ERPs externos mediante eventos HTTP con firma HMAC |
| **TPMS / IoT ingest endpoint** | Sensores de presión pueden reportar lecturas directamente vía API |
| **Serverless en Vercel** | Sin cron jobs persistentes; tareas programadas se ejecutan vía cron invocable externo |

### 4.3 Modelo de tenancy

**El sistema opera en modo single-tenant en la fase actual.** Una instancia productiva sirve a una única empresa. Sin embargo, el schema de base de datos mantiene la columna `empresa_id` en todas las entidades core (Neumático, Vehículo, Almacén, Proveedor, Usuario, etc.) como **infraestructura dormida**.

**Implicancias:**
- En producción existe **una única fila** en la tabla `Empresa`.
- Todos los registros se crean con ese `empresa_id`.
- Las queries filtran por `empresa_id` aunque no sea estrictamente necesario (preparación para multi-tenant).
- El endpoint `/admin/tenants` existe pero **debe estar bloqueado o escondido con feature flag** hasta la activación multi-tenant (pendiente).

**Cuándo se activará multi-tenant**: posterior a estabilización total del sistema. No en el horizonte de este PRD. Ver [sección 9](#9-visión-futura-tentativa-sin-compromiso).

---

## 5. Alcance funcional (implementado)

### 5.1 Ciclo de vida del neumático

**Estados canónicos del neumático:**

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│    COMPRA ──► EN_STOCK ──► INSTALADO ◄──┐                   │
│                  │              │        │                  │
│                  │              ▼        │                  │
│                  │      EN_REPARACION ───┘                  │
│                  │              │                           │
│                  │              ▼                           │
│                  └────► EN_REENCAUCHE ──► EN_STOCK          │
│                              │                              │
│                              ▼                              │
│                          DESECHADO                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Estados operativos canónicos (6)**:
- `EN_STOCK` — Disponible en almacén
- `INSTALADO` — Montado en vehículo
- `EN_REPARACION` — En taller de reparación
- `EN_REENCAUCHE` — En planta de reencauche
- `EN_TRANSITO` — Moviéndose entre almacenes
- `DESECHADO` — Baja definitiva (estado terminal)

> **Nota técnica**: El enum `EstadoNeumaticoEnum` en Postgres tiene 15 valores por razones históricas (`NUEVO`, `EN_USO`, `EN_ALMACEN`, `PARA_REPARACION`, `REPARADO`, `PARA_REENCAUCHE`, `REENCAUCHADO`, `PARA_DESECHO`, `VENDIDO` además de los canónicos). Los 9 valores no canónicos son **deprecados** — no se usan en escritura. Su remoción del enum Postgres es deuda técnica programada para Q2 2026.

### 5.2 Sistema de eventos centralizado

**Eventos canónicos del neumático (12)** — `POST /api/v1/neumaticos/eventos`:

| Evento | Descripción | Transición | Rol permitido |
|--------|-------------|------------|---------------|
| `COMPRA` | Ingreso de neumático nuevo al sistema | → `EN_STOCK` | GESTOR, ADMIN |
| `INSTALACION` | Montaje en vehículo en una posición | `EN_STOCK` → `INSTALADO` | OPERADOR, GESTOR, ADMIN |
| `DESMONTAJE` | Retiro del vehículo | `INSTALADO` → `EN_STOCK` | OPERADOR, GESTOR, ADMIN |
| `ROTACION` | Cambio de posición dentro del vehículo | `INSTALADO` → `INSTALADO` | OPERADOR, GESTOR, ADMIN |
| `INSPECCION` | Registro de profundidad y presión | Sin cambio de estado | OPERADOR, GESTOR, ADMIN |
| `REPARACION_ENTRADA` | Envío a taller de reparación | → `EN_REPARACION` | OPERADOR, GESTOR |
| `REPARACION_SALIDA` | Retorno de taller | → `EN_STOCK` | OPERADOR, GESTOR |
| `REENCAUCHE_ENTRADA` | Envío a planta de reencauche | → `EN_REENCAUCHE` | GESTOR, ADMIN |
| `REENCAUCHE_SALIDA` | Retorno de reencauche (reset km, vida+1) | → `EN_STOCK` | OPERADOR, GESTOR |
| `DESECHO` | Baja definitiva con motivo | → `DESECHADO` | GESTOR, ADMIN |
| `AJUSTE_INVENTARIO` | Corrección manual de estado/ubicación | Variable | GESTOR, ADMIN |
| `MOVIMIENTO_ENTRE_ALMACENES` | Transferencia física entre almacenes | `EN_STOCK` ↔ `EN_TRANSITO` → `EN_STOCK` | GESTOR |

> **Nota técnica**: El enum `TipoEventoNeumaticoEnum` en Postgres tiene 18 valores por razones históricas. Los 6 no canónicos (`ASIGNACION_A_ALMACEN`, `TRANSFERENCIA_UBICACION`, `DESMONTE_POR_FIN_VIDA_UTIL`, `DESMONTE_TEMPORAL`, `BAJA_POR_ROBO_EXTRAVIO`, `VENTA`) son **deprecados**.

### 5.3 Reglas de negocio y validaciones

#### Validación DOT
El código DOT (4 dígitos: semana + año) se valida al registrar compra. Máximo 10 años de antigüedad de fabricación.

#### Compatibilidad modelo-posición
Al montar un neumático, el sistema valida que el modelo sea compatible con el tipo de eje y vehículo según la tabla `ModeloPosicionPermitida`.

#### Restricción de reencauchados en dirección
Un neumático con `es_reencauchado = true` NO puede montarse en una posición cuyo `configuracion_eje.permite_reencauchados = false` (típicamente ejes de dirección).

#### Límite de reencauches por modelo
No se permite enviar a reencauche si `reencauches_realizados >= modelo.reencauches_maximos`.

#### Cálculo de kilometraje
- En `INSTALACION`: se registra `km_instalacion`.
- En `DESMONTAJE`: `km_recorridos = kilometraje_vehiculo − km_instalacion`, sumado a `kilometraje_acumulado`.
- En `REENCAUCHE_SALIDA`: `kilometraje_acumulado` se **resetea a 0**, `vida_actual += 1`, `reencauches_realizados += 1`.

### 5.4 Módulos funcionales

#### 📋 Gestión de catálogos
CRUD completo con soft delete para:
- Fabricantes de neumáticos
- Modelos de neumáticos (con especificaciones técnicas)
- Proveedores (fabricante, distribuidor, reparación, reencauche)
- Almacenes / ubicaciones físicas
- Motivos de desecho
- Tipos de vehículo + Configuración de ejes + Posiciones
- Parámetros de inventario (stock mínimo, profundidad mínima)
- Centros de costo
- Rutas y tipos de ruta

#### 🚛 Gestión de vehículos
- Alta, baja lógica, actualización y consulta de vehículos
- Asociación a tipo de vehículo con configuración de ejes
- Registro de odómetro (contador de kilometraje)
- Vista de neumáticos instalados por vehículo

#### 🛞 Gestión de neumáticos
- Registro vía evento `COMPRA` (con número de serie único por empresa)
- Consulta de neumático individual con historial de eventos completo
- Listado con filtros: estado, modelo, marca, medida, ubicación, rango de fechas
- Vista de neumáticos instalados por flota

#### 📏 Inspecciones y mediciones
- Endpoint `POST /api/v1/inspecciones` para registro manual
- Captura de profundidad (total + interior/centro/exterior para análisis de desgaste)
- Captura de presión (PSI)
- Fotos opcionales
- Observaciones libres
- Inspector registrado automáticamente desde sesión
- Histórico consultable por neumático

#### 📊 Reportes y KPIs

Endpoints productivos disponibles en `/api/v1/reportes/*`:

| Endpoint | Descripción |
|----------|-------------|
| `/cpk` | Costo por kilómetro por neumático, agregable por modelo/marca/proveedor |
| `/desgaste` | Tasa de desgaste y proyecciones |
| `/comparativo-marcas` | Performance comparativa entre marcas |
| `/forecast` | Proyección de compras basada en desgaste esperado |
| `/tco` | Total Cost of Ownership por neumático |
| `/benchmarking` | Benchmarking entre flotas o períodos |
| `/scoring` | Scoring de neumáticos por múltiples criterios |
| `/rendimiento` | Rendimiento agregado por modelo |
| `/gestion` | Reporte gerencial consolidado |
| `/flota` | Estado global de la flota |
| `/flota/semaforo` | Semáforo por flota |
| `/semaforo-medida` | Semáforo por medida de neumático |
| `/inventario` | Reporte de inventario con filtros |
| `/pareto` | Análisis de Pareto |
| `/historial-cambios` | Histórico de cambios de estado |
| `/historial-posicion` | Histórico de posiciones ocupadas |

#### 📈 Dashboard
- Vista general con KPIs principales
- Gráficos con Chart.js / Recharts
- Mapa visual de ejes por vehículo
- Exportación CSV de datos mostrados
- Dashboard de inventario, rendimiento y desechos

#### 🚨 Sistema de alertas
- Generación automática tras eventos críticos (inspección con profundidad baja, presión fuera de rango)
- Tipos: `PROFUNDIDAD_MINIMA`, `REENCAUCHE_MAXIMO`, `STOCK_MINIMO`, `PRESION_BAJA`, etc.
- Severidades: `CRITICAL`, `WARNING`, `INFO`
- Notificaciones por email vía Resend
- Marcado como leída / resuelta
- Histórico consultable

#### 🔔 Webhooks e integraciones ERP
- Configuración de endpoints externos por tipo de evento
- Firma HMAC para validación de autenticidad
- Cola de reintentos con backoff exponencial
- Logs de envío y resultado (éxito/fallo/reintentos)
- Tipos de evento soportados: eventos de neumáticos, alertas, inspecciones

#### 📡 Ingest TPMS / IoT
- Endpoint `POST /api/v1/integraciones/tpms` para recepción de lecturas de presión desde sensores
- Almacenamiento en tabla `lecturas_presion` con fuente (`MANUAL` / `SENSOR_IOT`)
- Disparo automático de alertas si la lectura está fuera de rango

#### 📄 Certificados PDF
- Emisión de Certificado de Operatividad Vehicular con:
  - **Folio secuencial único** por empresa (persistido en DB)
  - **Evaluación real** de estado operativo (APTO / CONDICIONAL / NO_APTO)
  - Cálculo basado en profundidad y presión de cada neumático instalado
  - **Snapshot inmutable** del estado al momento de emisión (audit trail)
  - Razones específicas para estados condicional/no apto
  - Descarga con nombre trazable: `certificado-{placa}-{folio}.pdf`

#### 🛡️ Sistema RBAC
- 3 roles operativos: **ADMIN, GESTOR, OPERADOR**
- Permisos granulares por recurso (lectura, creación, actualización, eliminación)
- Permisos específicos por tipo de evento de neumático
- Guards en todos los endpoints vía `requireRole()` / `hasPermission()`
- Soft delete en catálogos críticos

> **Nota técnica**: El enum `RolEnum` de Prisma incluye un cuarto rol `SUPERADMIN` que **no está activo en la fase single-tenant**. Solo se usará para administración cross-tenant en la activación multi-tenant futura. También existen tablas de RBAC dinámico (`Rol`, `Permiso`, `UsuarioRol`, `RolPermiso`) como infraestructura dormida para multi-tenant futuro — actualmente **no afectan la autenticación real**.

#### 🔍 Auditoría
- Log automático de creación, modificación y eliminación de entidades críticas
- Usuario, timestamp, operación, tabla y valores previos registrados
- Consultable vía endpoint `/api/v1/admin/audit` (solo ADMIN)

#### 📱 PWA (Progressive Web App)
- Manifest y service worker configurados
- Fallback offline
- Install prompt
- Modal de inspección manual operable offline
- Histórico de presión con gráficos de tendencia

---

## 6. Compromisos próximo trimestre (Q2 2026)

> **Alcance del compromiso**: cosas planificadas con fecha realista. Todo lo más allá de Q2 2026 va en [sección 9](#9-visión-futura-tentativa-sin-compromiso).

| Prioridad | Entregable | Criterio de aceptación | Dependencias |
|-----------|------------|------------------------|--------------|
| 🔴 Alta | **Pulir Certificado PDF (beta → GA)** | Folio trazable ✅, evaluación real ✅, migrar umbrales a `ParametroSistema`, agregar tests de integración, endpoint de re-descarga `GET /certificado/{folio}` | Ninguna |
| 🔴 Alta | **Consolidar baseline de migraciones Prisma** | Eliminar drift entre `schema.prisma` y `prisma/migrations/`. Crear migración de baseline consolidada que refleje el estado real de la DB | Coordinación con equipo para ventana de despliegue |
| 🔴 Alta | **Bloquear endpoints `/admin/roles/*`** | Deshabilitar o poner banner de advertencia porque actualmente no afectan permisos reales (bug de seguridad: falsa sensación de control de acceso) | Confirmación de que no hay usuarios dependiendo de ese flujo |
| 🔴 Alta | **Esconder `/admin/tenants` con feature flag** | El endpoint solo tiene sentido en multi-tenant. Bloquearlo con variable de entorno `MULTI_TENANT_ENABLED=false` | Ninguna |
| 🟡 Media | **Consolidar enums Postgres** | Eliminar valores deprecados de `EstadoNeumaticoEnum` (9 valores) y `TipoEventoNeumaticoEnum` (6 valores) con migración destructiva | Validar 0 uso en producción durante 1 mes previo |
| 🟡 Media | **Fix errores pre-existentes en `design-patterns.ts`** | 3 errores de TypeScript (template literal mal cerrado) | Ninguna |
| 🟡 Media | **Mover `OPERATIVIDAD_THRESHOLDS` a `ParametroSistema`** | Permitir configuración por empresa de los umbrales APTO/CONDICIONAL/NO_APTO | Discusión con cliente sobre umbrales correctos |
| 🟢 Baja | **Tests de integración para nuevos servicios** | Cobertura ≥ 80% en `certificado.service.ts`, `forecast.service.ts` (post-bugfix) | Ninguna |

---

## 7. Requerimientos no funcionales

### 7.1 Performance

| Requisito | Objetivo | Cómo se mide |
|-----------|----------|--------------|
| Tiempo de respuesta CRUD | < 500ms p95 | Logs de Vercel + APM |
| Tiempo de respuesta eventos | < 1s p95 | Incluye validaciones y triggers |
| Tiempo de generación reportes | < 3s p95 | Reportes complejos con agregaciones |
| Tiempo de generación PDF | < 4s p95 | Certificado de operatividad |
| Cold start serverless | < 2s | Característica de Vercel serverless |

### 7.2 Seguridad

- **Autenticación**: JWT Bearer tokens vía NextAuth.js v5. Tokens con expiración configurable.
- **Autorización**: RBAC basado en enum con guards en todos los endpoints productivos. Validación por rol + permiso específico según el recurso.
- **Transporte**: HTTPS obligatorio en producción (enforzado por Vercel).
- **Inyección SQL**: prevenida por el ORM Prisma (queries parametrizadas).
- **XSS**: mitigado por Next.js (escape automático en server components).
- **Secretos**: variables de entorno en Vercel, nunca commiteadas al repo.
- **Webhooks**: firma HMAC para validación de payload en recepción.
- **Audit trail**: todos los cambios críticos registrados en `AuditoriaLog` con usuario, timestamp y diff.

### 7.3 Disponibilidad

- **Target SLA**: 99.5% mensual (permite ~3.6h de downtime/mes).
- **Infraestructura**: Vercel (global CDN + serverless) + Supabase (managed Postgres con backups automáticos).
- **Recuperación ante fallos**: los backups de Supabase permiten point-in-time recovery.

### 7.4 Integridad de datos

- **Transacciones ACID** en operaciones compuestas (ej. registro de evento + actualización de estado del neumático deben ser atómicas).
- **Constraints en DB**: unique, foreign keys, not-null en campos críticos.
- **Soft delete** en entidades maestras (Neumático, Vehículo, Usuario, Proveedor, Modelo, Fabricante, Almacén, TipoVehículo) mediante campo `activo: bool`.
- **Snapshot inmutable** en certificados emitidos (audit trail legal).

### 7.5 Mantenibilidad

- **Arquitectura por capas**: Presentation (API Routes) → Services → Data Access (Prisma).
- **TypeScript strict** en todo el código.
- **Validación en boundaries** con Zod schemas.
- **Tests**: unitarios + integración + E2E con Jest.
- **Documentación**: OpenAPI/Swagger auto-generado + docs técnicas en `/docs`.

### 7.6 Retención de datos

- **Soft delete** para entidades operativas (conservación indefinida).
- **Logs de auditoría** conservados indefinidamente.
- **Logs de webhooks** purgables cuando excedan configuración retention (pendiente definir política).
- **Snapshots de certificados emitidos** conservados indefinidamente (requisito de trazabilidad).

### 7.7 Consistencia de unidades

- **Profundidad**: mm (milímetros)
- **Presión**: PSI (libras por pulgada cuadrada)
- **Kilometraje**: km (kilómetros)
- **Costos**: moneda configurable por neumático, default PEN (soles peruanos)
- **Fechas**: timestamps con zona horaria (`TIMESTAMPTZ` Postgres)

---

## 8. Out of scope

Lo que **GesNeu API explícitamente NO hace** (y no planea hacer en el horizonte del PRD):

### 8.1 Fuera por diseño

- ❌ **No es un ERP**: no gestiona compras generales, facturación, contabilidad o recursos humanos.
- ❌ **No gestiona talleres externos**: no administra agendas, personal ni inventario de proveedores de reparación o reencauche. Solo los trackea como entidades referenciables.
- ❌ **No maneja compraventa de neumáticos usados**: el flujo `VENTA` existía en el PDF original pero fue eliminado del modelo de dominio. Neumáticos usados que se venden a terceros (recicladores) se registran como `DESECHO` con motivo correspondiente.
- ❌ **No es un GPS / Telemática**: no gestiona ubicación GPS ni rutas en tiempo real. Solo recibe lecturas TPMS puntuales.
- ❌ **No gestiona conductores**: los conductores no son una entidad del sistema.
- ❌ **No factura al cliente final**: no emite comprobantes de venta ni notas de crédito.
- ❌ **No es un sistema de inventario general**: solo gestiona inventario de neumáticos, no otros repuestos ni herramientas.

### 8.2 Fuera en la fase actual (single-tenant)

- ❌ **Multi-tenant real**: el schema soporta `empresa_id` pero no está activado como feature operativa. Ver [sección 9](#9-visión-futura-tentativa-sin-compromiso).
- ❌ **Rol SUPERADMIN activo**: existe en el enum pero no se documenta ni se expone en la UI operativa.
- ❌ **Gestión de roles dinámicos**: los endpoints `/admin/roles/*` existen técnicamente pero no afectan autenticación real. Deuda técnica crítica — ver sección 6 (bloqueo de endpoints en Q2).
- ❌ **Certificado de Inspección separado**: solo existe el Certificado de Operatividad Vehicular. Si el cliente necesita un certificado específico de inspección como documento distinto, es una feature a evaluar.

---

## 9. Visión futura (tentativa, sin compromiso)

> ⚠️ **Esta sección es exploratoria**. Nada acá es un compromiso. Las ideas listadas pueden cambiar, postergarse o descartarse. Están documentadas para dar contexto a decisiones presentes.

### Q3 2026 (tentativo)
- Activación de **multi-tenant real**: gestión de múltiples empresas desde una instancia, con aislamiento completo de datos y roles cross-tenant (SUPERADMIN activo).
- **Integración con ERP interno del cliente** (a definir cuál).
- Exploración de **machine learning para predicción de vida útil** basado en datos históricos de la flota.

### Q4 2026 (tentativo)
- **Optimización de rutas de rotación** basada en patrones históricos.
- **App nativa** (React Native wrapper) si la PWA no cubre necesidades de los operadores.
- Expansión de analytics con dashboards personalizables por usuario.

### 2027+ (visión)
- Marketplace interno de intercambio de neumáticos entre sedes de la empresa.
- Integración con proveedores de reencauche para tracking en tiempo real del proceso.

---

## 10. Glosario y referencias

### 10.1 Glosario de dominio

| Término | Definición |
|---------|------------|
| **Neumático** | Entidad individual con número de serie único que representa un activo rotativo con ciclo de vida. |
| **Vida** | Período de uso operativo entre reencauches. Un neumático puede tener múltiples vidas (original + reencauches). |
| **CPK** | Costo por Kilómetro — métrica clave de eficiencia económica del neumático. |
| **DOT** | Department of Transportation code — 4 dígitos que indican semana y año de fabricación. |
| **Reencauche** | Proceso de renovación de la banda de rodadura de un neumático usado. Cada carcasa soporta un número limitado de reencauches. |
| **Posición de montaje** | Ubicación específica dentro de un vehículo donde se monta un neumático (ej. eje 1 lado izquierdo externo). |
| **CPK agregado** | Promedio ponderado de CPK a nivel modelo, marca o proveedor. |
| **Folio** | Número único secuencial por empresa asignado a cada certificado emitido. Garantiza trazabilidad legal. |
| **Snapshot** | Captura inmutable del estado del vehículo y neumáticos al momento exacto de emisión del certificado. |
| **Drift (schema)** | Diferencia entre el estado del schema declarado y el estado del historial de migraciones. |

### 10.2 Documentos relacionados

| Documento | Propósito |
|-----------|-----------|
| [`01_ARQUITECTURA.md`](./01_ARQUITECTURA.md) | Detalles técnicos del stack, capas, patrones y diagramas |
| [`02_MODELO_NEGOCIO.md`](./02_MODELO_NEGOCIO.md) | Reglas de negocio detalladas y transiciones de estado |
| [`03_API_REFERENCE.md`](./03_API_REFERENCE.md) | Especificación de endpoints REST |
| [`04_BASE_DATOS.md`](./04_BASE_DATOS.md) | Schema Prisma, diagrama ER, migraciones |
| [`05_SEGURIDAD.md`](./05_SEGURIDAD.md) | RBAC, auditoría, controles de seguridad |
| [`06_TESTING.md`](./06_TESTING.md) | Estrategia de pruebas y convenciones |
| [`07_DEPLOY.md`](./07_DEPLOY.md) | Guía de despliegue en Vercel + Supabase |
| [`08_INTEGRACIONES.md`](./08_INTEGRACIONES.md) | Webhooks y sistemas externos |
| [`10_TIPADO_PROFESIONAL.md`](./10_TIPADO_PROFESIONAL.md) | Guía de TypeScript avanzado |
| [`events/`](./events/) | Sistema de eventos (Event-Driven Architecture) |
| [`ROADMAP.md`](../ROADMAP.md) | **Cuándo** se entregan las cosas (complementa al PRD que dice **qué**) |

### 10.3 Historial de decisiones clave (persistidas en Engram)

| Fecha | Decisión | Justificación |
|-------|----------|---------------|
| 2026-04-10 | Single-tenant ahora, multi-tenant futuro | Priorizar estabilización antes de escalar complejidad |
| 2026-04-10 | Eliminar VENTA/VENDIDO del modelo | GesNeu gestiona flota propia, no es ERP de compraventa |
| 2026-04-10 | `ADMIN` canónico (no `ADMINISTRADOR`) | Coincide con enum RolEnum de Prisma (fuente de verdad en DB) |
| 2026-04-10 | Enum RBAC canónico, tablas dinámicas dormidas | Las tablas dinámicas no afectan autenticación real — bug de seguridad. Diferir hasta multi-tenant |
| 2026-04-10 | Eliminar rol `CONSULTOR` | Rol fantasma: existía en código pero no en enum Prisma — técnicamente inalcanzable |
| 2026-04-10 | Certificado PDF con folio secuencial + evaluación real | Reemplaza MVP con folio aleatorio y resultado hardcoded — requisito de trazabilidad legal |

---

## 📝 Metadata del documento

- **Autor**: Mikisbell (con asistencia de Claude Code)
- **Fecha de creación**: 2026-04-10
- **Próxima revisión sugerida**: 2026-07-10 (fin de Q2 2026)
- **Versionado**: este documento es vivo. Cambios materiales se registran en el historial de decisiones (sección 10.3) y en commits del repositorio.

---

*Este PRD consolida y reemplaza el documento histórico `Requerimientos de Sistema API Ges_Neu_Final.pdf v2.1`, que permanece archivado en la raíz del repositorio como referencia histórica del stack original (FastAPI + SQLModel) — ya no aplicable al estado actual del sistema.*
