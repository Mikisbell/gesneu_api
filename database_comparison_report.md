# Reporte de Comparación de Esquema de Base de Datos

**Fecha del Reporte:** 26 de Diciembre de 2025
**Base de Datos Analizada:** `pooler.supabase.com` (Credenciales provistas)
**Esquema de Referencia:** `ges_neu_bd` (Snapshot: 2025-08-31)

## 1. Resumen Ejecutivo

Existe una **divergencia significativa** entre la base de datos actual (Live DB) y el esquema de referencia proporcionado.
*   **Referencia:** 37 tablas (Arquitectura estilo Enterprise/SQL-Legacy, posiblemente Python/Alembic).
*   **Actual:** 22 tablas (Arquitectura modernizada para Next.js + Prisma).
*   **Estado:** La base de datos actual parece ser una versión simplificada o refactorizada, perdiendo varias tablas de auditoría granular, bitácoras y configuraciones específicas, pero ganando tablas para Webhooks y Centros de Costo.

## 2. Tablas Faltantes en Base de Datos Actual
Las siguientes tablas existen en el esquema de referencia pero **no existen** en la base de datos conectada:

| Categoría | Tablas Faltantes | Impacto Potencial |
|-----------|------------------|-------------------|
| **Auditoría Avanzada** | `auditoria_roles_usuarios`<br>`configuracion_auditoria` | Pérdida de trazabilidad granular de cambios en roles y configuración dinámica de auditoría. |
| **Operaciones/Bitácoras** | `bitacora_mantenimiento`<br>`bitacora_operaciones`<br>`bitacora_operaciones_neumaticos` | No hay registro histórico detallado de operaciones de mantenimiento separadas de los eventos. |
| **Gestión de Errores** | `errores_aplicacion` | Falta de tabla centralizada para logs de errores de aplicación (probablemente movido a soluciones externas como Sentry). |
| **Catálogos Técnicos** | `especificaciones_desgaste`<br>`modelos_posiciones_permitidas` | Menor control estricto sobre dónde se puede montar cada modelo de neumático. |
| **Inventario/Garantías** | `garantias_neumaticos`<br>`parametros_inventario` | No se encontró módulo de gestión de garantías ni parámetros de inventario complejos. |
| **Configuración Sistema** | `parametros_rendimiento_esperado_modelo`<br>`parametros_sistema` | Configuraciones globales y expectativas de rendimiento ahora parecen estar hardcodeadas o simplificadas. |
| **Seguridad/RBAC** | `permisos`<br>`roles`<br>`roles_permisos`<br>`usuarios_roles` | El sistema RBAC complejo (Tablas N:M) ha sido reemplazado por un Enum simple (`RolEnum`) en usuarios. |
| **Rutas/Logística** | `rutas`<br>`tipos_ruta`<br>`registros_odometro` | Se ha eliminado el módulo de rutas. `registros_odometro` parece haber sido reemplazado por `registros_contador`. |
| **Sistema** | `tareas_programadas`<br>`alembic_version` | Tareas programadas DB-side eliminadas y control de versiones por Alembic obsoleto. |
| **Mediciones** | `mediciones_profundidad` | Reemplazado o simplificado. |

## 3. Nuevas Tablas en Base de Datos Actual
Tablas encontradas en la conexión actual que no estaban en la referencia:

*   `centros_costo`: Nueva entidad para agrupación financiera.
*   `webhook_configs`: Sistema de webhooks para integraciones.
*   `webhook_jobs`: Cola de trabajos para webhooks.
*   `webhook_logs`: Logs de ejecución de webhooks.

## 4. Análisis de Discrepancias en Tablas Clave

### Neumáticos (`neumaticos`)
*   **Faltante en Live:** `tasa_desgaste_actual_mm_km`, `vida_util_restante_km`, `proxima_inspeccion_fecha`, `proxima_inspeccion_km`, `sensor_id`, `motivo_desecho_id`.
*   **Diferencias de Tipo:** 
    *   `kilometraje_acumulado`: `Integer` (Ref) vs `Float` (Live).
    *   `reencauches_realizados`: `SmallInt` (Ref) vs `Int` (Live).
*   **Cambio de Lógica:** La tabla actual incluye campos para snapshots directos de profundidad (`profundidad_int`, `cen`, `ext`) que no estaban en la tabla maestra de referencia.

### Usuarios (`usuarios`)
*   **Cambio Crítico de Seguridad:**
    *   **Ref:** Relación con tablas `roles`, `usuarios_roles` para permisos granulares.
    *   **Live:** Columna simple `rol` (Enum: ADMIN, GESTOR, OPERADOR). Modelo de seguridad simplificado.

### Eventos (`eventos_neumaticos`)
*   **Faltantes:** `moneda_costo`, `tipo_ruta_id`, `destino_desmontaje`.
*   **Nuevos:** `profundidad_int`, `profundidad_cen`, `profundidad_ext` (ahora parte del evento).

## 5. Conclusión
La base de datos actual (`pooler.supabase.com`) representa una **iteración diferente** del proyecto GesNeu, probablemente una reescritura en Next.js/Prisma que optó por:
1.  **Simplificar el modelo de permisos** (RBAC vs Roles Enums).
2.  **Eliminar lógica de negocio compleja en DB** (Triggers, bitácoras complejas) a favor de lógica en aplicación o simplificación.
3.  **Añadir capacidades modernas** como Webhooks y Centros de Costo.
4.  **Soportar Línea Amarilla:** Uso de `Float` para contadores (Horas/Km) y tabla `centros_costo`.

**Acción Recomendada:**
Si el objetivo es restaurar la funcionalidad del esquema de referencia (Agosto 2025), se requerirá una migración masiva pues el esquema actual es incompatible en estructura y filosofía. Si el objetivo es validar el estado actual, el esquema Live es funcional pero más "ligero" que el diseño original.
