# Análisis de Migración: Excel vs GesNeu System

**Archivo Analizado**: `CONTROL DE MANTENIMIENTO NEUMÁTICOS_Rev. A.xlsx`
**Fecha**: 2026-02-05
**Objetivo**: Alinear los datos estáticos del Excel con el "Corazón" del sistema (`EventoNeumaticoService`).

---

## 1. Resumen de Contenido

El archivo Excel actúa como una **"Foto Estática"** del estado actual de la flota y los neumáticos. Contiene dos hojas principales de información:

### A. Hoja de Inventario Detallado (Hoja Principal)
Esta hoja contiene la relación completa `Vehículo -> Neumático`.

**Columnas Identificadas & Mapeo al Sistema:**

| Columna Excel (Ejemplo) | Entidad GesNeu | Campo GesNeu | Notas |
|-------------------------|----------------|--------------|-------|
| `TC-126` (Cod Equipo) | `Vehiculo` | `codigo_interno` | Identificador único de flota |
| `F8U-786` (Placa) | `Vehiculo` | `placa` | ID legal del vehículo |
| `TRACTO` (Tipo) | `TipoVehiculo` | `nombre` | Categorización de flota |
| `VOLVO` (Marca Veh) | `MarcaVehiculo` | `nombre` | Datos maestros vehículo |
| `BRIDGESTONE` (Marca N) | `Fabricante` | `nombre` | Fabricante del neumático |
| `295/80R22.5` (Medida) | `Modelo` | `medida` | Especificación técnica |
| `R269` (Modelo N) | `Modelo` | `nombre_modelo` | Catálogo de neumáticos |
| `16` (Profundidad) | `Neumatico` | `profundidad_actual_mm` | Estado de desgaste actual |
| `110` (Presión) | `LecturaPresion` | `presion_psi` | Última lectura conocida |
| `BGR269` (Serie?) | `Neumatico` | `numero_serie` | ID único del neumático (crítico) |

### B. Hoja "Hoja1" (Resumen de Flota)
Contiene una matriz de asignación rápida (`PLACA` vs `COD EQUIPO`).
- **Uso**: Validación cruzada para asegurar que cada vehículo en el sistema tenga su código interno correcto.
- **Estado**: Muestra equipos "DISPONIBLES" e "INSTALADOS", lo que sugiere un control de disponibilidad de flota.

---

## 2. El "Corazón" vs El Excel

### Diferencia Fundamental

| Característica | Excel (Control Manual) | GesNeu (EventoNeumaticoService) |
|----------------|------------------------|---------------------------------|
| **Naturaleza** | **Estado Actual (Snapshot)** | **Flujo Histórico (Event Log)** |
| **Cambios** | Sobreescritura (se borra lo anterior) | Eventos inmutables (`ROTACION`, `DESMONTAJE`) |
| **Historia** | Se pierde el rastro previo | Trazabilidad total de por vida |
| **Validación** | Confianza en el usuario | Reglas estrictas (Zod + Database Constraints) |

### Cómo "Alimentar" al Corazón

Para que el sistema cobre vida, necesitamos transformar este Excel en una serie de **Eventos Iniciales**. No basta con insertar datos en la tabla `Neumatico`; debemos simular que ocurrieron eventos para respetar la arquitectura.

**Estrategia de Carga (Seeding):**

1.  **Carga de Maestros**:
    - Crear `Fabricante`, `Modelo`, `TipoVehiculo`, `MarcaVehiculo` basados en las columnas únicas del Excel.
    
2.  **Carga de Flota**:
    - Crear `Vehiculo` usando Placa y Código Interno.
    
3.  **Carga de Inventario (El Truco)**:
    - Para cada fila del Excel, el sistema debe ejecutar internamente:
        1.  **Evento `COMPRA` (Simulado)**: Para dar de alta el neumático en el sistema con sus características iniciales (Marca, Modelo, Medida).
        2.  **Evento `INSTALACION` (Simulado)**: Para "montar" el neumático en el vehículo correspondiente (`TC-126`) en la posición indicada (si la columna de posición existe, o asignación inicial).
        3.  **Actualización de Estado**: Fijar `profundidad_actual` y `presion_actual` según el Excel.

---

## 3. Conclusión y Recomendación

Este archivo Excel es la **Semilla de Datos**.

- **No es el proceso**: El Excel no gestiona el mantenimiento, solo lo *registra* estáticamente.
- **Es el punto de partida**: Contiene la verdad actual de la operación.

**Acción Recomendada**:
Desarrollar un script de migración (`scripts/seed_from_excel.ts`) que lea este archivo y ejecute la carga masiva utilizando `EventoNeumaticoService` para garantizar que, desde el día 1, el sistema tenga integridad referencial y un estado inicial coherente con la realidad física.
