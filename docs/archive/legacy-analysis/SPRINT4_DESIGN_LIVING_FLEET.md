# Sprint 4: Living Fleet Interface - Design Document

## 1. Visión: "Living Fleet"

Transformar la gestión de neumáticos de formularios estáticos a una experiencia visual, interactiva y en tiempo real. El usuario debe sentir que está manipulando los neumáticos físicamente sobre los vehículos.

## 2. Arquitectura Frontend

### 2.1. Optimistic UI (La clave de la velocidad)

Usaremos `useOptimistic` de React 19 (disponible en Next.js 15/16) para que todas las operaciones se sientan instantáneas.

**Flujo:**

1. Usuario arrastra neumático al eje.
2. UI se actualiza inmediatamente (el neumático "aparece" en el eje).
3. Server Action / API Call se dispara en segundo plano.
4. Si falla, la UI revierte automáticamente y muestra un Toast de error.

### 2.2. Gestión de Estado (Zustand)

Para manejar el Drag & Drop complejo entre componentes distantes (Sidebar de Inventario -> Esquema de Vehículo), usaremos Zustand.

```typescript
interface DragState {
  isDragging: boolean;
  draggedItem: Neumatico | null;
  source: 'INVENTORY' | 'AXLE';
  setDragging: (item: Neumatico | null, source: 'INVENTORY' | 'AXLE') => void;
}
```

## 3. Componentes Core

### 3.1. `VehicleSchematic` (Interactivo)

Evolución del componente actual.

- **Props:** `vehiculo`, `onDrop`, `onNeumaticoClick`.
- **Comportamiento:**
  - Detecta si se está arrastrando un neumático compatible.
  - Ilumina posiciones válidas (Drop Zones).
  - Muestra tooltips con presión/profundidad al hover.

### 3.2. `InventorySidebar` (Draggable Source)

Panel lateral colapsable con lista de neumáticos en STOCK.

- **Filtros:** Medida, Marca, Diseño.
- **Items:** Cada tarjeta de neumático es "arrastrable".

### 3.3. `TireDragLayer`

Capa visual que sigue al cursor mientras se arrastra, mostrando una "fantasía" del neumático semitransparente.

## 4. Integración Backend

### 4.1. Hook `useNeumaticoOperaciones`

Encapsula la lógica de negocio frontend y la comunicación con la API.

```typescript
const { montarNeumatico, desmontarNeumatico, rotarNeumatico } = useNeumaticoOperaciones();
```

Este hook usará internamente el endpoint `/api/v1/neumaticos/eventos` que ya hemos robustecido.

## 5. Plan de Implementación

1. **Setup:** Instalar `dnd-kit` (o `react-dnd`) y `zustand`.
2. **Hook:** Crear `useNeumaticoOperaciones` con lógica optimista.
3. **Componentes:** Refactorizar `VehicleSchematic` para aceptar Drop.
4. **Integración:** Conectar Sidebar -> Schematic.
5. **Polish:** Animaciones (Framer Motion) y Feedback visual.

## 6. KPIs y Dashboard (Fase 2 del Sprint)

Una vez la operación visual funcione, alimentaremos los gráficos:

- **CPK (Costo por Kilómetro):** Calculado en tiempo real.
- **Proyección de Vida:** Basada en desgaste actual vs histórico.
