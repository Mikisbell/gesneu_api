# Plan de Implementación: Alertas Automáticas de Presión y Refactor de Configuración

**Objetivo:** Implementar el sistema de detección automática de anomalías de presión en tiempo real y refactorizar la configuración de límites para abandonar el patrón EAV (Entity-Attribute-Value) ineficiente.

## User Review Required

> [!IMPORTANT]
> **Refactor de Arquitectura:**
> Se eliminará el uso de `ParametroConfig` (string) para definir presiones.
> Se agregarán columnas **Decimales explicitas** en `ModeloNeumatico` para `presion_recomendada`, `minima` y `maxima`.
> Esto permite que la base de datos (y la API) validen rangos nativamente sin conversiones costosas.

## Proposed Changes

### 1. Database Schema (`schema.prisma`)
Migrar configuración crítica a columnas tipadas.

#### [MODIFY] `model ModeloNeumatico`
*   `[NEW] presion_recomendada_psi`: `Decimal(5, 2)`
*   `[NEW] tolerancia_psi`: `Decimal(5, 2)` (Defaults to 10% or similar logic, or use explicit min/max)
*   **Decisión Arquitectónica:** Usaremos `presion_minima_psi` y `presion_maxima_psi` explícitos para flexibilidad total.
    *   `[NEW] presion_minima_psi`: `Decimal(5, 2)`
    *   `[NEW] presion_maxima_psi`: `Decimal(5, 2)`

### 2. Backend Logic (Server Actions)
Endpoint centralizado para ingesta de lecturas.

#### [NEW] `src/actions/lecturas-actions.ts`
*   `registrarLectura(neumaticoId, presion, ...)`:
    1.  Inserta en `LecturaPresion`.
    2.  Obtiene `ModeloNeumatico` (con sus límites).
    3.  **Evaluación de Reglas:**
        *   Si `presion < minima` -> Generar Alerta `CRITICAL` (Peligro).
        *   Si `presion > maxima` -> Generar Alerta `WARNING` (Sobrezona).
    4.  Si hay alerta: Crear registro en `Alerta` y devolver flag `alertaGenerada: true` al cliente.

### 3. Frontend Implementation
Feedback inmediato al operador.

#### [MODIFY] `src/components/operaciones/LecturaPresionForm.tsx` (o similar)
*   Integrar con `registrarLectura`.
*   Mostrar **Toast/Modal de Alerta** inmediato si la respuesta indica anomalía. "⚠️ PRESIÓN CRÍTICA DETECTADA".

## Verification Plan

### Automated Tests
*   `scripts/verify-alerts.ts`:
    1.  Configurar un Modelo con Min 90 PSI.
    2.  Registrar lectura de 80 PSI.
    3.  Verificar que se creó una fila en tabla `Alertas`.
    4.  Verificar que el `tipo` es `PRESION_BAJA`.
