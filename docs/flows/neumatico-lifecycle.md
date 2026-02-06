# Ciclo de Vida de Neumáticos

Este diagrama muestra el flujo completo del ciclo de vida de un neumático en GesNeu desde su registro hasta su baja.

## Flujo Completo

```mermaid
flowchart TD
    Start([Nuevo neumático]) --> Registro[Registrar Neumático]
    Registro --> SetEstado1[Estado: DISPONIBLE]
    SetEstado1 --> EnAlmacen{Almacenado}
    
    EnAlmacen --> |Espera| EnAlmacen
    EnAlmacen --> |Asignar| Montaje[Montaje en Vehículo]
    
    Montaje --> SetEstado2[Estado: MONTADO]
    SetEstado2 --> EnUso[En uso en vehículo]
    
    EnUso --> Inspecciones[Inspecciones periódicas]
    Inspecciones --> CheckStatus{Condición<br/>neumático}
    
    CheckStatus --> |Bueno| ContinuarUso[Continuar en uso]
    ContinuarUso --> EnUso
    
    CheckStatus --> |Desgaste| AlertaLimite[Alerta: Profundidad límite]
    AlertaLimite --> Desmontaje1[Desmontaje]
    
    CheckStatus --> |Daño| Desmontaje2[Desmontaje]
    
    EnUso --> |Rotación| Rotacion[Rotación de posición]
    Rotacion --> EnUso
    
    EnUso --> |Cambio| Desmontaje3[Desmontaje]
    
    Desmontaje1 --> SetEstado3[Estado: DISPONIBLE]
    Desmontaje2 --> EvaluarDanio{Evaluación<br/>daño}
    Desmontaje3 --> SetEstado3
    
    EvaluarDanio --> |Reparable| Reparacion[Reparación]
    Reparacion --> SetEstado3
    
    EvaluarDanio --> |No reparable| SetEstadoBaja[Estado: BAJA]
    
    SetEstado3 --> NuevoMontaje[Disponible para montaje]
    NuevoMontaje --> Montaje
    
    SetEstado3 --> |Fin de vida útil| SetEstadoBaja
    
    SetEstadoBaja --> Desecho[Desecho/Reciclaje]
    Desecho --> End([Fin del ciclo])
    
    style Start fill:#e1f5e1
    style SetEstado1 fill:#d4edff
    style SetEstado2 fill:#fff3cd
    style SetEstado3 fill:#d4edff
    style SetEstadoBaja fill:#ffe1e1
    style End fill:#e1e1e1
    style AlertaLimite fill:#ffcccc
```

## Estados del Neumático

```mermaid
stateDiagram-v2
    [*] --> DISPONIBLE: Registro
    DISPONIBLE --> MONTADO: Montaje
    MONTADO --> EN_REPARACION: Daño detectado
    EN_REPARACION --> DISPONIBLE: Reparación exitosa
    EN_REPARACION --> BAJA: No reparable
    MONTADO --> DISPONIBLE: Desmontaje
    DISPONIBLE --> BAJA: Fin vida útil
    MONTADO --> BAJA: Desgaste crítico
    BAJA --> [*]: Desecho
```

## Operaciones Principales

### 1. Registro

```mermaid
flowchart LR
    Input[Datos del neumático] --> Validate{Validación<br/>Zod}
    Validate -->|Error| ShowErrors[Mostrar errores]
    Validate -->|OK| CreateRecord[Crear registro]
    CreateRecord --> AssignAlmacen[Asignar almacén]
    AssignAlmacen --> Success[Neumático registrado]
    
    style Success fill:#e1f5e1
    style ShowErrors fill:#ffe1e1
```

### 2. Montaje

```mermaid
flowchart LR
    SelectNeum[Seleccionar neumático] --> CheckAvailable{Estado<br/>DISPONIBLE?}
    CheckAvailable -->|No| Error1[Error: No disponible]
    CheckAvailable -->|Sí| SelectVeh[Seleccionar vehículo]
    SelectVeh --> SelectPos[Seleccionar posición]
    SelectPos --> CheckPosOccupied{Posición<br/>ocupada?}
    CheckPosOccupied -->|Sí| Error2[Error: Posición ocupada]
    CheckPosOccupied -->|No| InputKM[Ingresar km_vehiculo]
    InputKM --> CreateMontaje[Crear montaje]
    CreateMontaje --> UpdateStatus[Estado: MONTADO]
    UpdateStatus --> Success[Montaje exitoso]
    
    style Success fill:#e1f5e1
    style Error1 fill:#ffe1e1
    style Error2 fill:#ffe1e1
```

### 3. Inspección

```mermaid
flowchart LR
    SelectNeum[Seleccionar neumático<br/>MONTADO] --> MeasureProf[Medir profundidad]
    MeasureProf --> MeasurePres[Medir presión]
    MeasurePres --> CheckProf{Profundidad <br/> límite?}
    
    CheckProf -->|Sí| AlertProf[⚠️ Alerta: Cambiar neumático]
    CheckProf -->|No| CheckPres{Presión<br/>correcta?}
    
    CheckPres -->|Baja| AlertPres[⚠️ Alerta: Inflar]
    CheckPres -->|Alta| AlertPres2[⚠️ Alerta: Desinflar]
    CheckPres -->|OK| RecordObs[Registrar observaciones]
    
    AlertProf --> RecordInsp[Guardar inspección]
    AlertPres --> RecordInsp
    AlertPres2 --> RecordInsp
    RecordObs --> RecordInsp
    RecordInsp --> Success[Inspección registrada]
    
    style Success fill:#e1f5e1
    style AlertProf fill:#ffcccc
    style AlertPres fill:#fff3cd
    style AlertPres2 fill:#fff3cd
```

### 4. Desmontaje

```mermaid
flowchart LR
    SelectMontaje[Seleccionar montaje<br/>activo] --> InputKM[Ingresar km_vehiculo]
    InputKM --> ValidateKM{KM > KM<br/>montaje?}
    ValidateKM -->|No| Error[Error: KM inválido]
    ValidateKM -->|Sí| SelectMotivo[Seleccionar motivo]
    SelectMotivo --> CreateDesmontaje[Crear desmontaje]
    CreateDesmontaje --> UpdateStatus[Estado: DISPONIBLE]
    UpdateStatus --> FreePosition[Liberar posición]
    FreePosition --> Success[Desmontaje exitoso]
    
    style Success fill:#e1f5e1
    style Error fill:#ffe1e1
```

## Alertas y Validaciones

### Alertas de Profundidad

```mermaid
flowchart TD
    Inspeccion[Nueva inspección] --> CheckProf{Profundidad}
    
    CheckProf -->|>= 4mm| StatusBueno[✅ Estado: BUENO]
    CheckProf -->|2-4mm| StatusAdvertencia[⚠️ ADVERTENCIA:<br/>Profundidad baja]
    CheckProf -->|< 2mm| StatusCritico[🚨 CRÍTICO:<br/>Cambiar inmediatamente]
    
    StatusBueno --> NoAlert[Sin alerta]
    StatusAdvertencia --> CreateAlertWarn[Crear alerta MEDIA]
    StatusCritico --> CreateAlertCrit[Crear alerta ALTA]
    
    style StatusBueno fill:#e1f5e1
    style StatusAdvertencia fill:#fff3cd
    style StatusCritico fill:#ffcccc
```

### Alertas de Presión

```mermaid
flowchart TD
    Inspeccion[Nueva inspección] --> CheckPres{Presión}
    
    CheckPres -->|28-35 PSI| StatusOK[✅ Presión correcta]
    CheckPres -->|< 28 PSI| StatusBaja[⚠️ Presión baja]
    CheckPres -->|> 35 PSI| StatusAlta[⚠️ Presión alta]
    
    StatusOK --> NoAlert[Sin alerta]
    StatusBaja --> CreateAlertBaja[Crear alerta:<br/>Inflar neumático]
    StatusAlta --> CreateAlertAlta[Crear alerta:<br/>Desinflar neumático]
    
    style StatusOK fill:#e1f5e1
    style StatusBaja fill:#fff3cd
    style StatusAlta fill:#fff3cd
```

## Archivos Relacionados

### Backend
- **`src/lib/services/neumatico.service.ts`**: Lógica de negocio
- **`src/lib/services/evento-neumatico.service.ts`**: Montaje, desmontaje, inspección
- **`src/lib/repositories/neumatico.repository.ts`**: Data access
- **`src/lib/validators/neumatico.validator.ts`**: Validaciones Zod

### Frontend
- **`src/app/(dashboard)/dashboard/neumaticos/`**: CRUD neumáticos
- **`src/app/(dashboard)/dashboard/operaciones/`**: Montaje, inspección, desmontaje

### Database
```prisma
model Neumatico {
  id                String   @id @default(uuid())
  numero_serie      String   @unique
  estado            EstadoNeumatico
  profundidad_actual Float
  // ... más campos
}

enum EstadoNeumatico {
  DISPONIBLE
  MONTADO
  EN_REPARACION
  BAJA
}
```

## Métricas Clave

- **Vida útil promedio**: Calculada en km recorridos
- **Tasa de inspecciones**: Inspecciones/mes por neumático
- **Alertas activas**: Neumáticos que requieren atención
- **Rotación**: Tiempo promedio entre montaje y desmontaje
