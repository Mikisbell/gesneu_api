# 🛞 Modelo de Negocio - GesNeu API

> **Última actualización**: Diciembre 2025

## Dominio: Gestión de Neumáticos de Flota

GesNeu gestiona el ciclo de vida completo de neumáticos en flotas vehiculares, desde la compra hasta el desecho.

---

## Estados del Neumático

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

---

## Eventos del Sistema

| Evento | Descripción | Transición | Campos Requeridos |
|--------|-------------|------------|-------------------|
| `COMPRA` | Ingreso de neumático nuevo | → EN_STOCK | numero_serie, modelo_id, dot, profundidad_inicial |
| `INSTALACION` | Montaje en vehículo | EN_STOCK → INSTALADO | vehiculo_id, posicion_id, kilometraje_vehiculo |
| `DESMONTAJE` | Retiro de vehículo | INSTALADO → EN_STOCK | kilometraje_vehiculo, almacen_destino_id |
| `ROTACION` | Cambio de posición | INSTALADO → INSTALADO | posicion_destino_id |
| `INSPECCION` | Registro de medición | Sin cambio | presion_psi, profundidad_mm (opcional) |
| `REPARACION_ENTRADA` | Envío a reparar | → EN_REPARACION | proveedor_id |
| `REPARACION_SALIDA` | Retorno de reparación | → EN_STOCK | costo_reparacion |
| `REENCAUCHE_ENTRADA` | Envío a reencauchar | → EN_REENCAUCHE | proveedor_id |
| `REENCAUCHE_SALIDA` | Retorno reencauchado | → EN_STOCK | profundidad_nueva, costo_reencauche |
| `DESECHO` | Baja definitiva | → DESECHADO | motivo_desecho_id |

---

## Lógica de Procesamiento de Eventos

### Instalación
```typescript
// Campos actualizados al instalar
estado_actual = 'INSTALADO'
ubicacion_vehiculo_id = vehiculo_id
ubicacion_posicion_id = posicion_id
ubicacion_almacen_id = null
fecha_instalacion = now()
km_instalacion = kilometraje_vehiculo
```

### Desmontaje
```typescript
// Cálculo de kilometraje acumulado
km_recorridos = kilometraje_vehiculo - km_instalacion
kilometraje_acumulado += km_recorridos

// Campos actualizados
estado_actual = estado_destino || 'EN_STOCK'
ubicacion_vehiculo_id = null
ubicacion_posicion_id = null
ubicacion_almacen_id = almacen_destino_id
```

### Reencauche Salida
```typescript
// Reset de vida
estado_actual = 'EN_STOCK'
profundidad_actual_mm = profundidad_nueva
profundidad_inicial_mm = profundidad_nueva  // Reset para nueva vida
vida_actual += 1
reencauches_realizados += 1
es_reencauchado = true
kilometraje_acumulado = 0  // Reset para nueva vida
```

---

## Reglas de Validación de Negocio

### Validación DOT
```typescript
// DOT = 4 dígitos (semana + año de fabricación)
// Ejemplo: "2524" = semana 25 de 2024
const dotYear = parseInt(dot.substring(2, 4))
const currentYear = new Date().getFullYear() % 100
const yearDiff = currentYear - dotYear

// Máximo 10 años de antigüedad
if (yearDiff > 10 || yearDiff < 0) {
  throw new Error('DOT indica año de fabricación no válido')
}
```

### Compatibilidad Posición-Modelo
```typescript
// Verificar que el modelo puede ir en la posición
const permitido = await prisma.modelosPosicionesPermitidas.findFirst({
  where: {
    modelo_id: neumatico.modelo_id,
    tipo_vehiculo_id: vehiculo.tipo_vehiculo_id,
    tipo_eje: posicion.configuracion_eje.tipo_eje
  }
})

if (!permitido) {
  throw new Error('Modelo no compatible con esta posición')
}
```

### Restricción de Reencauchados
```typescript
// Ejes de dirección generalmente no permiten reencauchados
if (neumatico.es_reencauchado && !posicion.permite_reencauchado) {
  throw new Error('No se permiten reencauchados en esta posición')
}

// Límite de reencauches por modelo
if (neumatico.reencauches_realizados >= modelo.reencauches_maximos) {
  throw new Error('Neumático ha alcanzado límite de reencauches')
}
```

---

## Métricas Clave

### CPK (Costo por Kilómetro)
```
CPK = (Costo_Compra + Σ Costo_Reencauches + Σ Costo_Reparaciones) / Km_Total
```

### Tasa de Desgaste
```
Desgaste_mm_por_km = (Profundidad_Inicial - Profundidad_Actual) / Km_Recorridos
```

### Vida Útil Estimada
```
Km_Restantes = (Profundidad_Actual - Profundidad_Minima) / Tasa_Desgaste
```

---

## Alertas Automáticas

| Condición | Severidad | Acción |
|-----------|-----------|--------|
| `profundidad_actual < 4mm` | CRITICAL | Notificar + Email |
| `reencauches >= max - 1` | WARNING | Planificar reemplazo |
| `presion < umbral_minimo` | WARNING | Inspección requerida |
| `tiempo_en_stock > 6 meses` | INFO | Revisar rotación |

---

*Ver también: `04_BASE_DATOS.md` para schema Prisma.*
