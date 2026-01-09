# 🏗️ Guía de Tipado Profesional - GesNeu 2026

> **Objetivo:** Establecer estándares de tipado TypeScript de nivel Enterprise para asegurar mantenibilidad, seguridad y escalabilidad del sistema.  
> **Aplica a:** Todo el codebase de GesNeu API  
> **Versión:** 1.0  
> **Fecha:** Enero 2026

---

## 📋 Tabla de Contenidos

1. [Principios Fundamentales](#1-principios-fundamentales)
2. [Arquitectura de Tipos por Capas](#2-arquitectura-de-tipos-por-capas)
3. [Branded Types (IDs Seguros)](#3-branded-types-ids-seguros)
4. [Result Types (Manejo de Errores)](#4-result-types-manejo-de-errores)
5. [Validación con Zod](#5-validación-con-zod)
6. [Mapper Functions](#6-mapper-functions)
7. [Estructura de Directorios](#7-estructura-de-directorios)
8. [Checklist de Migración](#8-checklist-de-migración)

---

## 1. Principios Fundamentales

### ❌ Lo que NO hacer (Anti-patrones 2025)

```typescript
// MALO: Una interfaz para todo
interface Vehiculo {
  id: string;
  placa: string;
  modelo: string;
  tipo_vehiculo?: { nombre: string };
  // Mezcla de campos de BD, API y UI
}

// MALO: Pasar objetos directamente entre capas
const vehiculo = await prisma.vehiculo.findUnique(...);
return NextResponse.json(vehiculo); // ⚠️ Expone estructura interna de BD

// MALO: IDs genéricos intercambiables
function getVehiculo(id: string) { ... }
getVehiculo(neumatico.id); // Compila pero es un bug silencioso
```

### ✅ Lo que SÍ hacer (Patrones 2026)

```typescript
// BUENO: Tipos separados por capa
type VehiculoEntity = Prisma.VehiculoGetPayload<{ include: { tipo_vehiculo: true }}>;
interface CreateVehiculoDTO { placa: string; modelo: string; ... }
interface VehiculoResponse { id: string; displayName: string; ... }

// BUENO: Mapeo explícito entre capas
const entity = await prisma.vehiculo.findUnique(...);
const response = mapEntityToResponse(entity);
return NextResponse.json(response);

// BUENO: Branded Types para IDs
type VehiculoId = string & { readonly __brand: 'VehiculoId' };
function getVehiculo(id: VehiculoId) { ... }
```

---

## 2. Arquitectura de Tipos por Capas

Cada entidad del sistema se clasifica en una de dos categorías, determinando la complejidad de sus tipos:

### A. Entidades Core (Negocio Principal)
*Ej: Vehiculo, Neumatico, User*
Requieren **4 tipos distintos** para máxima flexibilidad y desacople.

### B. Catálogos Simples (Tablas Auxiliares)
*Ej: TipoVehiculo, Marca, Pais*
Requieren solo **2 tipos** (Entity + Response) ya que la API suele ser un espejo de la BD.

---

### Mapeo de Entidades Core (4 Tipos)

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                      │
│  VehiculoViewModel: { displayName, statusBadge, actions }   │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ mapResponseToViewModel()
                              │
┌─────────────────────────────────────────────────────────────┐
│                      API RESPONSE                            │
│  VehiculoResponse: { id, placa, marca, tipoVehiculo }       │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ mapEntityToResponse()
                              │
┌─────────────────────────────────────────────────────────────┐
│                      DATABASE (Prisma)                       │
│  VehiculoEntity: Prisma.VehiculoGetPayload<...>             │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ mapDtoToPrismaInput()
                              │
┌─────────────────────────────────────────────────────────────┐
│                      API REQUEST                             │
│  CreateVehiculoDTO / UpdateVehiculoDTO (validado por Zod)   │
└─────────────────────────────────────────────────────────────┘
```

### Ejemplo Completo: Vehiculo

```typescript
// src/types/domain/vehiculo.types.ts

import { Prisma } from '@prisma/client';

// ============================================
// 1. ENTITY (Lo que viene de Prisma/BD)
// ============================================
export type VehiculoEntity = Prisma.VehiculoGetPayload<{
  include: {
    tipo_vehiculo: true;
    neumaticos_instalados: {
      include: {
        modelo: { include: { fabricante: true } };
      };
    };
  };
}>;

// ============================================
// 2. DTOs (Lo que recibe la API del cliente)
// ============================================
export interface CreateVehiculoDTO {
  placa: string;
  marca: string;
  modelo: string;              // Frontend usa "modelo"
  anio: number;                // Frontend usa "anio"
  tipo_vehiculo_id: string;
  kilometraje_actual?: number; // Frontend puede enviar esto
  activo?: boolean;
}

export interface UpdateVehiculoDTO {
  placa?: string;
  marca?: string;
  modelo?: string;
  anio?: number;
  tipo_vehiculo_id?: string;
  kilometraje_actual?: number;
  activo?: boolean;
}

// ============================================
// 3. RESPONSE (Lo que devuelve la API)
// ============================================
export interface VehiculoResponse {
  id: string;
  placa: string;
  marca: string;
  modelo: string;           // Renombrado de modelo_vehiculo
  anio: number;             // Renombrado de anio_fabricacion
  vin: string | null;
  kilometraje: number;      // Renombrado de odometro_actual
  activo: boolean;
  tipoVehiculo: {
    id: string;
    nombre: string;
    cantidadEjes: number;
    cantidadNeumaticos: number;
  };
  neumaticosInstalados: NeumaticoResumenResponse[];
  createdAt: string;        // ISO string
  updatedAt: string;
}

export interface NeumaticoResumenResponse {
  id: string;
  numeroSerie: string;
  posicion: string;
  marca: string;
  modelo: string;
}

// ============================================
// 4. VIEWMODEL (Lo que usa React/UI)
// ============================================
export interface VehiculoCardViewModel {
  id: string;
  displayName: string;          // "Toyota Hilux 2024 - ABC-123"
  statusColor: 'green' | 'yellow' | 'red';
  alertCount: number;
  neumaticosCount: string;      // "8/8" o "6/8"
  lastUpdate: string;           // "Hace 2 días"
}

export interface VehiculoFilters {
  placa?: string;
  marca?: string;
  tipo_vehiculo_id?: string;
  activo?: boolean;
}
```

---

## 3. Branded Types (IDs Seguros)

Evitan que se mezclen IDs de diferentes entidades por error.

```typescript
// src/types/branded.types.ts

declare const __brand: unique symbol;

export type Brand<T, TBrand extends string> = T & {
  readonly [__brand]: TBrand;
};

// IDs tipados
export type VehiculoId = Brand<string, 'VehiculoId'>;
export type NeumaticoId = Brand<string, 'NeumaticoId'>;
export type AlmacenId = Brand<string, 'AlmacenId'>;
export type TipoVehiculoId = Brand<string, 'TipoVehiculoId'>;
export type UsuarioId = Brand<string, 'UsuarioId'>;
export type EmpresaId = Brand<string, 'EmpresaId'>;

// Helpers para crear IDs tipados
export const asVehiculoId = (id: string): VehiculoId => id as VehiculoId;
export const asNeumaticoId = (id: string): NeumaticoId => id as NeumaticoId;
// ... etc

// Uso:
// const vehiculoId = asVehiculoId(params.id);
// await service.getById(vehiculoId); // ✅ Type-safe
```

---

## 4. Result Types (Manejo de Errores)

Fuerza al desarrollador a manejar explícitamente los casos de éxito y error.

### Política: Result vs Exceptions
*   **Result<T, E>**: Úsalo para **errores de negocio esperados** (e.g. validación, duplicados, no encontrado). El consumidor *debe* saber que esto puede fallar.
*   **Exceptions**: Úsalas para **errores de infraestructura inesperados** (e.g. DB caída, fallo de red). Estos deben ser capturados por un `GlobalErrorHandler` o el middleware de API, retornando 500.

No "wrappees" cada llamada de Prisma en un Result. Si Prisma falla, es usualmente un 500.

```typescript
// src/types/result.types.ts

export type Result<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E };

// Helpers
export const ok = <T>(data: T): Result<T, never> => ({
  success: true,
  data,
});

export const err = <E>(error: E): Result<never, E> => ({
  success: false,
  error,
});

// Errores de negocio tipados
export class BusinessError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly statusCode: number = 400
  ) {
    super(message);
    this.name = 'BusinessError';
  }
}

export class NotFoundError extends BusinessError {
  constructor(entity: string) {
    super(`${entity} no encontrado`, 'NOT_FOUND', 404);
  }
}

export class ValidationError extends BusinessError {
  constructor(message: string, public readonly fields?: Record<string, string[]>) {
    super(message, 'VALIDATION_ERROR', 400);
  }
}

export class ConflictError extends BusinessError {
  constructor(message: string) {
    super(message, 'CONFLICT', 409);
  }
}

export class ForbiddenError extends BusinessError {
  constructor(message: string = 'Acceso denegado') {
    super(message, 'FORBIDDEN', 403);
  }
}
```

### Uso en Service

```typescript
// src/lib/services/vehiculo.service.ts

import { Result, ok, err, NotFoundError, ConflictError } from '@/types/result.types';

export class VehiculoService {
  async create(dto: CreateVehiculoDTO): Promise<Result<VehiculoResponse, BusinessError>> {
    // Validación de negocio
    const existing = await this.repository.findByPlaca(dto.placa);
    if (existing) {
      return err(new ConflictError(`Ya existe un vehículo con placa ${dto.placa}`));
    }

    // Mapeo y creación
    const prismaInput = mapDtoToPrismaCreate(dto);
    const entity = await this.repository.create(prismaInput);
    const response = mapEntityToResponse(entity);

    return ok(response);
  }

  async getById(id: VehiculoId): Promise<Result<VehiculoResponse, NotFoundError>> {
    const entity = await this.repository.findById(id);
    if (!entity) {
      return err(new NotFoundError('Vehículo'));
    }
    return ok(mapEntityToResponse(entity));
  }
}
```

### Uso en API Route

```typescript
// src/app/api/v1/vehiculos/[id]/route.ts

export async function GET(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const id = asVehiculoId((await params).id);
  const result = await service.getById(id);

  if (!result.success) {
    return ApiResponseHelper.error(result.error.message, result.error.statusCode);
  }

  return ApiResponseHelper.success(result.data);
}
```

---

### 5. Validación con Zod (Enfoque Híbrido - PROFESIONAL)

**ESTÁNDAR 2026**: Utilizamos un **Enfoque Híbrido** para maximizar seguridad y velocidad.

1.  **INPUTS (DTOs)**: Se definen con Zod y se infiere el tipo TypeScript.
    *   *Ventaja*: Un solo origen de verdad. Si cambia la validación, cambia el tipo.
2.  **OUTPUTS (Responses)**: Se definen como interfaces TypeScript puras.
    *   *Ventaja*: Mayor performance y claridad para el consumidor (Frontend).

> [!WARNING]
> **Estado de Cumplimiento (Enero 2026)**
> - `Neumatico`: ❌ No cumple. Usa interfaces manuales (`CreateNeumaticoDTO`) duplicadas. Requiere refactor.
> - `Vehiculo`: ❌ No cumple. Usa interfaces manuales duplicadas. Requiere refactor.
> - `EventoNeumatico`: ✅ Cumple (En proceso). Usará inferencia directa de Zod.

```typescript
// src/lib/validators/vehiculo.validator.ts

import { z } from 'zod';

// 1. Definir Schema (Única fuente de verdad para INPUTS)
export const CreateVehiculoSchema = z.object({
  placa: z
    .string()
    .min(6, 'La placa debe tener al menos 6 caracteres')
    .max(10, 'La placa no puede exceder 10 caracteres')
    .regex(/^[A-Z0-9-]+$/, 'La placa solo puede contener letras, números y guiones'),
  // ...
});

// 2. Inferir Tipo (No escribir interface manual)
export type CreateVehiculoInput = z.infer<typeof CreateVehiculoSchema>;

// Helper de validación
export function validateCreateVehiculo(data: unknown) {
  return CreateVehiculoSchema.safeParse(data);
}
```

### Uso en API

```typescript
export async function POST(request: NextRequest) {
  const body = await request.json();
  const validation = validateCreateVehiculo(body);

  if (!validation.success) {
    return ApiResponseHelper.validationError(validation.error.flatten());
  }

  // validation.data está 100% tipado y validado
  const result = await service.create(validation.data);
  // ...
}
```

### 5.5. Validación de Dominio vs Validación de Entrada

Es crucial separar estos dos conceptos:

1.  **Validación de Entrada (Payload Check)**:
    *   **Responsable**: Zod (`validators/`)
    *   **Qué valida**: Formatos, tipos, rangos simples, regex.
    *   *Ejemplo*: "Placa debe tener 6 caracteres", "Año debe ser número".

2.  **Validación de Dominio (Business Rules)**:
    *   **Responsable**: Servicio o Domain Helper (`services/` o `validators/domain/`)
    *   **Qué valida**: Estado actual, coherencia con BD, reglas complejas.
    *   *Ejemplo*: "No se puede dar de baja un vehículo con neumáticos instalados".

### Patrón Recomendado
```typescript
// src/lib/validators/domain/vehiculo-rules.ts (Nuevo)
export function canDeactivateVehiculo(vehiculo: VehiculoEntity): Result<true, BusinessError> {
  if (vehiculo.neumaticos_instalados.length > 0) {
    return err(new ConflictError('El vehículo tiene neumáticos instalados'));
  }
  return ok(true);
}
```

---

## 6. Mapper Functions

Funciones puras que transforman objetos entre capas. **Nunca** se pasa un objeto directamente de una capa a otra.

```typescript
// src/lib/mappers/vehiculo.mapper.ts

import { Prisma } from '@prisma/client';
import { VehiculoEntity, VehiculoResponse, CreateVehiculoDTO } from '@/types/domain/vehiculo.types';

/**
 * Transforma un DTO de creación al formato esperado por Prisma
 */
export function mapDtoToPrismaCreate(dto: CreateVehiculoDTO): Prisma.VehiculoCreateInput {
  return {
    placa: dto.placa,
    marca: dto.marca,
    modelo_vehiculo: dto.modelo,              // ← Mapeo de nombre
    anio_fabricacion: dto.anio,               // ← Mapeo de nombre
    odometro_actual: dto.kilometraje_actual ?? 0,
    activo: dto.activo ?? true,
    tipo_vehiculo: {
      connect: { id: dto.tipo_vehiculo_id },  // ← Relación via connect
    },
  };
}

/**
 * Transforma un DTO de actualización al formato esperado por Prisma
 */
export function mapDtoToPrismaUpdate(dto: UpdateVehiculoDTO): Prisma.VehiculoUpdateInput {
  const updateData: Prisma.VehiculoUpdateInput = {};

  if (dto.placa !== undefined) updateData.placa = dto.placa;
  if (dto.marca !== undefined) updateData.marca = dto.marca;
  if (dto.modelo !== undefined) updateData.modelo_vehiculo = dto.modelo;
  if (dto.anio !== undefined) updateData.anio_fabricacion = dto.anio;
  if (dto.kilometraje_actual !== undefined) updateData.odometro_actual = dto.kilometraje_actual;
  if (dto.activo !== undefined) updateData.activo = dto.activo;

  if (dto.tipo_vehiculo_id !== undefined) {
    updateData.tipo_vehiculo = { connect: { id: dto.tipo_vehiculo_id } };
  }

  return updateData;
}

/**
 * Transforma una Entity de Prisma al formato de respuesta de la API.
 * Usa `satisfies` para validación en compile-time sin tipos explícitos de retorno redundantes.
 */
 */
export function mapEntityToResponse(entity: VehiculoEntity) {
  return {
    id: entity.id,
    placa: entity.placa,
    marca: entity.marca,
    modelo: entity.modelo_vehiculo,
    anio: entity.anio_fabricacion,
    vin: entity.vin,
    kilometraje: entity.odometro_actual ?? 0,
    activo: entity.activo,
    tipoVehiculo: {
      id: entity.tipo_vehiculo.id,
      nombre: entity.tipo_vehiculo.nombre,
      cantidadEjes: entity.tipo_vehiculo.cantidad_ejes ?? 0,
      cantidadNeumaticos: entity.tipo_vehiculo.cantidad_neumaticos ?? 0,
    },
    neumaticosInstalados: entity.neumaticos_instalados?.map(n => ({
      id: n.id,
      numeroSerie: n.numero_serie ?? '',
      posicion: n.ubicacion_posicion?.codigo_posicion ?? 'N/A',
      marca: n.modelo?.fabricante?.nombre ?? 'N/A',
      modelo: n.modelo?.nombre ?? 'N/A',
    })) ?? [],
    createdAt: entity.creado_en?.toISOString() ?? new Date().toISOString(),
    updatedAt: entity.actualizado_en?.toISOString() ?? new Date().toISOString(),
  } satisfies VehiculoResponse;
}

/**
 * Transforma una Response al formato optimizado para cards de UI
 */
export function mapResponseToCardViewModel(
  response: VehiculoResponse,
  alertCount: number = 0
): VehiculoCardViewModel {
  const instalados = response.neumaticosInstalados.length;
  const esperados = response.tipoVehiculo.cantidadNeumaticos;

  return {
    id: response.id,
    displayName: `${response.marca} ${response.modelo} ${response.anio} - ${response.placa}`,
    statusColor: alertCount > 0 ? 'red' : instalados < esperados ? 'yellow' : 'green',
    alertCount,
    neumaticosCount: `${instalados}/${esperados}`,
    lastUpdate: formatRelativeDate(response.updatedAt),
  };
}
```

---

## 7. Estructura de Directorios

```
src/
├── types/
│   ├── branded.types.ts         # Branded IDs (VehiculoId, NeumaticoId)
│   ├── result.types.ts          # Result<T,E>, BusinessError, etc.
│   └── domain/
│       ├── vehiculo.types.ts    # Entity, DTOs, Response, ViewModel
│       ├── neumatico.types.ts
│       ├── almacen.types.ts
│       └── index.ts             # Re-exports
├── lib/
│   ├── validators/
│   │   ├── vehiculo.validator.ts  # Zod schemas
│   │   ├── neumatico.validator.ts
│   │   └── index.ts
│   ├── mappers/
│   │   ├── vehiculo.mapper.ts   # Funciones de mapeo
│   │   ├── neumatico.mapper.ts
│   │   └── index.ts
│   ├── services/
│   │   ├── vehiculo.service.ts  # Usa Result<T,E>
│   │   └── ...
│   └── repositories/
│       └── ...
└── app/
    └── api/
        └── v1/
            └── vehiculos/
                └── route.ts     # Usa validators + mappers
```

---

## 8. Checklist de Migración

Para cada entidad del sistema, seguir este orden:

### Fase 1: Tipos Base
- [ ] Crear `src/types/domain/{entidad}.types.ts`
- [ ] Definir `{Entidad}Entity` usando `Prisma.{Entidad}GetPayload<...>`
- [ ] Definir `Create{Entidad}DTO` y `Update{Entidad}DTO`
- [ ] Definir `{Entidad}Response`
- [ ] Definir `{Entidad}ViewModel` (si aplica para UI)

### Fase 2: Validación
- [ ] Crear `src/lib/validators/{entidad}.validator.ts`
- [ ] Definir `Create{Entidad}Schema` con Zod
- [ ] Definir `Update{Entidad}Schema` (usualmente `.partial()`)
- [ ] Crear helpers `validateCreate{Entidad}()` y `validateUpdate{Entidad}()`

### Fase 3: Mappers
- [ ] Crear `src/lib/mappers/{entidad}.mapper.ts`
- [ ] Implementar `mapDtoToPrismaCreate()`
- [ ] Implementar `mapDtoToPrismaUpdate()`
- [ ] Implementar `mapEntityToResponse()`
- [ ] Implementar `mapResponseToViewModel()` (si aplica)

### Fase 4: Service
- [ ] Refactorizar service para usar `Result<T, E>`
- [ ] Usar mappers en lugar de spread directo
- [ ] Usar Branded IDs para parámetros

### Fase 5: API Route
- [ ] Usar validators al inicio del handler
- [ ] Manejar `result.success` explícitamente
- [ ] Devolver respuestas mapeadas, no entities

---

## 📌 Entidades a Migrar (Orden de Prioridad)

1. **Vehiculo** ← Empezar aquí (ya tiene estructura base)
2. **Neumatico**
3. **Almacen**
4. **TipoVehiculo** (catálogo)
5. **ModeloNeumatico** (catálogo)
6. **EventoNeumatico**
7. **LecturaPresion**
8. **Alerta**
9. **Usuario**

---

*Documento creado como parte del Roadmap 2026 de GesNeu.*
*Última actualización: Enero 2026*
