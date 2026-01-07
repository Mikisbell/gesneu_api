# 🧠 Análisis Experto de Micro-Arquitectura de Base de Datos
**Objetivo:** Comparativa Técnica para Escalabilidad API & Integridad de Datos
**Sujetos:** `ges_neu_bd` (Reference SQL) vs. `schema.prisma` (Current Production)

## 1. Integridad de Datos y Restricciones (Data Integrity & Constraints)

El esquema actual confía peligrosamente en la capa de aplicación (Node.js) para la validación de datos. En un entorno empresarial de alto volumen (y más con futura ingesta IoT), esto es inaceptable.

### 🔴 Deficiencias Críticas (Missing Constraints)

| Riesgo | Constraint Original (SQL) | Estado Actual (Prisma) | Consecuencia API |
|--------|---------------------------|------------------------|------------------|
| **Datos Físicos Imposibles** | `CHECK (presion_psi > 0)`<br>`CHECK (profundidad_mm BETWEEN 0 AND 100)` | ❌ Inexistente (`Float`) | La API puede recibir `-50 PSI` o `999 mm` y persistirlo, corrompiendo reportes estadísticos. |
| **Bilocación Cuántica** | `CHECK chk_ubicacion_mutuamente_exclusiva` | ❌ Inexistente | Un neumático puede estar asignado a un almacén y a un vehículo simultáneamente si falla la lógica del resolver. |
| **Incoherencia Temporal** | `CHECK (fecha_baja >= fecha_alta)` | ❌ Inexistente | Se pueden registrar vehículos que se dieron de baja antes de comprarse. |
| **Lógica de Negocio** | `CHECK (reencauches_realizados <= reencauches_maximos)` | ❌ Inexistente | Se pueden enviar a reencauche neumáticos que ya excedieron su vida útil legal/técnica. |

**Solución Experta:** No confiar en Zod/Prisma para esto. Implementar `Raw SQL Migration` para inyectar estos `CHECK` constraints a nivel de base de datos.

## 2. Tipos de Datos y Precisión Financiera (Type Safety)

### ⚠️ Precisión Numérica
*   **Referencia:** Utilizaba `NUMERIC(5,2)` o `NUMERIC(10,8)` para tasas de desgaste.
*   **Actual:** Abuso de `Float` (IEEE 754).
*   **Impacto API:**
    *   Cálculo de CPK: `Float` introduce errores de redondeo en operaciones monetarias acumulativas. `Decimal` está presente en `costo_compra` (bien), pero `kilometraje_acumulado` es `Float`.
    *   **Tasa de Desgaste:** `(Profundidad Inicial - Actual) / Km` produce decimales periódicos. Al usarse para proyectar vida útil (millones de km en flotas grandes), el error del `Float` se magnifica.

### ⚠️ El Anti-Patrón EAV (`parametros_config`)
*   **Diseño Actual:** Tabla Entity-Attribute-Value donde `valor` es `String`.
*   **Deficiencia:**
    *   Query: `SELECT * FROM neumaticos WHERE presion < (SELECT valor FROM parametros WHERE tipo='MIN_PSI')`.
    *   **Problema:** El motor DB no puede optimizar esta comparación (Cast String -> Float en tiempo de ejecución). Rompe el uso de índices.
    *   **Escalabilidad:** Inservible para endpoints de monitoreo masivo/"Alertas en tiempo real".

## 3. Modelo de Rutas y Contexto Operativo (Missing Context)

El esquema actual es "plano" geográficamente.
*   **Referencia:** Tablas `rutas`, `tipos_ruta` (`distancia_trocha`, `distancia_asfalto`).
*   **Actual:** Eliminado.
*   **Impacto Negocio:** El sistema asume que 100km en autopista pesan lo mismo que 100km en cantera. Esto invalida el `CPK` comparativo entre marcas, que es el core value proposition para una flota minera/industrial.

## 4. Concurrencia y Bloqueos (Concurrency)

*   **Referencia:** Diseño transaccional implícito.
*   **Actual:** Prisma no implementa Optimistic Concurrency Control (`version` field) por defecto.
*   **Escenario de Carrera:**
    1.  Operador A lee neumático (Estado: STOCK).
    2.  Operador B lee neumático (Estado: STOCK).
    3.  A monta en Vehículo 1.
    4.  B monta en Vehículo 2.
    5.  **Resultado:** `Last Write Wins`. El neumático termina en Vehículo 2, pero el historial puede quedar inconsistente o el Vehículo 1 cree que tiene llanta.
*   **Solución:** Agregar campo `@version` y manejar `P2025` (Record not found/changed) en la API.

## 5. Estrategia de Índices (Indexing Strategy)

El esquema Prisma actual tiene índices básicos, pero faltan índices compuestos para los patrones de acceso de un Dashboard de Flotas:

| Query Frecuente (Dashboard) | Índice Necesario | Estado Actual | Penalidad |
|-----------------------------|------------------|---------------|-----------|
| Status de Flota | `(estado_actual, ubicacion_vehiculo_id)` | ❌ Parcial | `Sequential Scan` en tablas grandes para contar estados. |
| Alertas por Severidad | `(leida, severidad, creada_en)` | ❌ Solo PK | Dashboard de alertas lento al crecer histórico |
| Búsqueda de Neumático | `(numero_serie)` | ✅ Unique | Correcto |
| Historial por Neumático | `(neumatico_id, fecha_cambio DESC)` | ❌ Solo FK | Paginación de historial lenta ("Dame los últimos 5 eventos") |

## 6. Recomendación de Arquitecto

La base de datos actual es un prototipo funcional ("MVP"), no una base de datos Enterprise. Para soportar el Roadmap 2026 (IoT, Alertas, Multi-tenant):

1.  **Hardening (Prioridad 1):** Inyectar `CHECK constraints` vía SQL manual.
2.  **Refactor Numerics (Prioridad 2):** Migrar `Float` críticos a `Decimal`.
3.  **Restore Context (Prioridad 3):** Reimplementar tabla `Rutas` y `CondicionesOperacion`.
4.  **Fix Parameters (Prioridad 1):** Eliminar `ParametroConfig` para valores críticos; usar columnas tipadas en `ModeloNeumatico` o `ConfiguracionFlota`.

---
*Este análisis asume un objetivo de soportar >10,000 activos y >1M eventos/año sin degradación.*
