/**
 * Branded Types - IDs Tipados y Seguros
 * 
 * Este módulo provee "Branded Types" que previenen mezclar IDs de diferentes
 * entidades por error. El compilador TypeScript los tratará como tipos distintos.
 * 
 * @example
 * // Esto generará un error de compilación:
 * function getVehiculo(id: VehiculoId) { ... }
 * getVehiculo(neumatico.id); // ❌ Error: NeumaticoId no es asignable a VehiculoId
 * 
 * // Uso correcto:
 * const id = asVehiculoId(params.id);
 * getVehiculo(id); // ✅ OK
 */

// Symbol único para el branding (no se exporta)
declare const __brand: unique symbol;

/**
 * Tipo utilitario para crear branded types.
 * T es el tipo base (usualmente string), TBrand es el identificador único.
 */
export type Brand<T, TBrand extends string> = T & {
    readonly [__brand]: TBrand;
};

// ============================================
// IDs de Entidades Principales
// ============================================

/** ID único de Vehículo */
export type VehiculoId = Brand<string, 'VehiculoId'>;

/** ID único de Neumático */
export type NeumaticoId = Brand<string, 'NeumaticoId'>;

/** ID único de Almacén */
export type AlmacenId = Brand<string, 'AlmacenId'>;

/** ID único de Tipo de Vehículo (catálogo) */
export type TipoVehiculoId = Brand<string, 'TipoVehiculoId'>;

/** ID único de Modelo de Neumático (catálogo) */
export type ModeloNeumaticoId = Brand<string, 'ModeloNeumaticoId'>;

/** ID único de Fabricante (catálogo) */
export type FabricanteId = Brand<string, 'FabricanteId'>;

/** ID único de Usuario */
export type UsuarioId = Brand<string, 'UsuarioId'>;

/** ID único de Empresa (tenant) */
export type EmpresaId = Brand<string, 'EmpresaId'>;

/** ID único de Evento de Neumático */
export type EventoNeumaticoId = Brand<string, 'EventoNeumaticoId'>;

/** ID único de Lectura de Presión */
export type LecturaPresionId = Brand<string, 'LecturaPresionId'>;

/** ID único de Alerta */
export type AlertaId = Brand<string, 'AlertaId'>;

/** ID único de Posición de Neumático */
export type PosicionNeumaticoId = Brand<string, 'PosicionNeumaticoId'>;

// ...

/**
 * Convierte un string a PosicionNeumaticoId.
 */
const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

function validateUUID(id: string, typeName: string): string {
    // Permitir "temp" solo en entornos de test/dev si es estrictamente necesario,
    // pero idealmente deberíamos ser estrictos.
    // Por ahora validamos UUID estándar.
    if (!UUID_REGEX.test(id)) {
        throw new Error(`Invalid ${typeName}: ${id} is not a valid UUID`);
    }
    return id;
}

/**
 * Valida que un string sea un UUID y lo convierte al tipo Branded.
 * Úsalo en los límites del sistema (API Inputs, Params).
 * @throws Error si el formato no es válido.
 */
export const parsePosicionNeumaticoId = (id: string): PosicionNeumaticoId => validateUUID(id, 'PosicionNeumaticoId') as PosicionNeumaticoId;
export const parseVehiculoId = (id: string): VehiculoId => validateUUID(id, 'VehiculoId') as VehiculoId;
export const parseNeumaticoId = (id: string): NeumaticoId => validateUUID(id, 'NeumaticoId') as NeumaticoId;
export const parseAlmacenId = (id: string): AlmacenId => validateUUID(id, 'AlmacenId') as AlmacenId;
export const parseUsuarioId = (id: string): UsuarioId => validateUUID(id, 'UsuarioId') as UsuarioId;
export const parseEmpresaId = (id: string): EmpresaId => validateUUID(id, 'EmpresaId') as EmpresaId;
export const parseEventoNeumaticoId = (id: string): EventoNeumaticoId => validateUUID(id, 'EventoNeumaticoId') as EventoNeumaticoId;

/**
 * Convierte un string al tipo Branded SIN VALIDAR.
 * Úsalo SOLO cuando confías en el origen del dato (e.g. viene de la BD).
    * Costo: O(1).
    */
export const asPosicionNeumaticoId = (id: string): PosicionNeumaticoId => id as PosicionNeumaticoId;
export const asVehiculoId = (id: string): VehiculoId => id as VehiculoId;
export const asNeumaticoId = (id: string): NeumaticoId => id as NeumaticoId;
export const asAlmacenId = (id: string): AlmacenId => id as AlmacenId;
export const asUsuarioId = (id: string): UsuarioId => id as UsuarioId;
export const asEmpresaId = (id: string): EmpresaId => id as EmpresaId;
export const asEventoNeumaticoId = (id: string): EventoNeumaticoId => id as EventoNeumaticoId;
