/**
 * Unit tests for Zod validation schemas
 */
import {
    MontajeNeumaticoSchema,
    DesmontajeNeumaticoSchema,
    RotacionNeumaticoSchema
} from '@/lib/validators/operaciones';

describe('Operations Validation Schemas', () => {
    describe('MontajeNeumaticoSchema', () => {
        it('should validate correct montaje data', () => {
            const validData = {
                neumatico_id: '550e8400-e29b-41d4-a716-446655440000',
                vehiculo_id: '550e8400-e29b-41d4-a716-446655440001',
                posicion_id: '550e8400-e29b-41d4-a716-446655440002',
                kilometraje_vehiculo: 50000,
                presion_psi: 110
            };

            const result = MontajeNeumaticoSchema.safeParse(validData);
            expect(result.success).toBe(true);
        });

        it('should reject invalid UUIDs', () => {
            const invalidData = {
                neumatico_id: 'not-a-uuid',
                vehiculo_id: '550e8400-e29b-41d4-a716-446655440001',
                posicion_id: '550e8400-e29b-41d4-a716-446655440002',
                kilometraje_vehiculo: 50000
            };

            const result = MontajeNeumaticoSchema.safeParse(invalidData);
            expect(result.success).toBe(false);
        });

        it('should reject negative kilometraje', () => {
            const invalidData = {
                neumatico_id: '550e8400-e29b-41d4-a716-446655440000',
                vehiculo_id: '550e8400-e29b-41d4-a716-446655440001',
                posicion_id: '550e8400-e29b-41d4-a716-446655440002',
                kilometraje_vehiculo: -100
            };

            const result = MontajeNeumaticoSchema.safeParse(invalidData);
            expect(result.success).toBe(false);
        });

        it('should reject PSI above 150', () => {
            const invalidData = {
                neumatico_id: '550e8400-e29b-41d4-a716-446655440000',
                vehiculo_id: '550e8400-e29b-41d4-a716-446655440001',
                posicion_id: '550e8400-e29b-41d4-a716-446655440002',
                kilometraje_vehiculo: 50000,
                presion_psi: 200
            };

            const result = MontajeNeumaticoSchema.safeParse(invalidData);
            expect(result.success).toBe(false);
        });
    });

    describe('DesmontajeNeumaticoSchema', () => {
        it('should validate correct desmontaje data with STOCK destino', () => {
            const validData = {
                neumatico_id: '550e8400-e29b-41d4-a716-446655440000',
                destino: 'STOCK',
                kilometraje_vehiculo: 60000,
                almacen_destino_id: '550e8400-e29b-41d4-a716-446655440003'
            };

            const result = DesmontajeNeumaticoSchema.safeParse(validData);
            expect(result.success).toBe(true);
        });

        it('should validate correct desmontaje data with DESECHO destino', () => {
            const validData = {
                neumatico_id: '550e8400-e29b-41d4-a716-446655440000',
                destino: 'DESECHO',
                kilometraje_vehiculo: 60000,
                motivo_id: '550e8400-e29b-41d4-a716-446655440003'
            };

            const result = DesmontajeNeumaticoSchema.safeParse(validData);
            expect(result.success).toBe(true);
        });

        it('should reject STOCK destino without almacen_destino_id', () => {
            const invalidData = {
                neumatico_id: '550e8400-e29b-41d4-a716-446655440000',
                destino: 'STOCK',
                kilometraje_vehiculo: 60000
            };

            const result = DesmontajeNeumaticoSchema.safeParse(invalidData);
            expect(result.success).toBe(false);
        });

        it('should reject DESECHO destino without motivo_id', () => {
            const invalidData = {
                neumatico_id: '550e8400-e29b-41d4-a716-446655440000',
                destino: 'DESECHO',
                kilometraje_vehiculo: 60000
            };

            const result = DesmontajeNeumaticoSchema.safeParse(invalidData);
            expect(result.success).toBe(false);
        });

        it('should reject invalid destino value', () => {
            const invalidData = {
                neumatico_id: '550e8400-e29b-41d4-a716-446655440000',
                destino: 'INVALID_DESTINO',
                kilometraje_vehiculo: 60000
            };

            const result = DesmontajeNeumaticoSchema.safeParse(invalidData);
            expect(result.success).toBe(false);
        });
    });

    describe('RotacionNeumaticoSchema', () => {
        it('should validate correct rotacion data', () => {
            const validData = {
                vehiculo_id: '550e8400-e29b-41d4-a716-446655440001',
                kilometraje_vehiculo: 70000,
                movimientos: [
                    {
                        neumatico_id: '550e8400-e29b-41d4-a716-446655440000',
                        posicion_destino_id: '550e8400-e29b-41d4-a716-446655440002'
                    },
                    {
                        neumatico_id: '550e8400-e29b-41d4-a716-446655440003',
                        posicion_destino_id: '550e8400-e29b-41d4-a716-446655440004'
                    }
                ]
            };

            const result = RotacionNeumaticoSchema.safeParse(validData);
            expect(result.success).toBe(true);
        });

        it('should reject less than 2 movimientos', () => {
            const invalidData = {
                vehiculo_id: '550e8400-e29b-41d4-a716-446655440001',
                kilometraje_vehiculo: 70000,
                movimientos: [
                    {
                        neumatico_id: '550e8400-e29b-41d4-a716-446655440000',
                        posicion_destino_id: '550e8400-e29b-41d4-a716-446655440002'
                    }
                ]
            };

            const result = RotacionNeumaticoSchema.safeParse(invalidData);
            expect(result.success).toBe(false);
        });

        it('should reject duplicate neumatico IDs', () => {
            const invalidData = {
                vehiculo_id: '550e8400-e29b-41d4-a716-446655440001',
                kilometraje_vehiculo: 70000,
                movimientos: [
                    {
                        neumatico_id: '550e8400-e29b-41d4-a716-446655440000',
                        posicion_destino_id: '550e8400-e29b-41d4-a716-446655440002'
                    },
                    {
                        neumatico_id: '550e8400-e29b-41d4-a716-446655440000', // Duplicate
                        posicion_destino_id: '550e8400-e29b-41d4-a716-446655440003'
                    }
                ]
            };

            const result = RotacionNeumaticoSchema.safeParse(invalidData);
            expect(result.success).toBe(false);
        });

        it('should reject duplicate posicion_destino IDs', () => {
            const invalidData = {
                vehiculo_id: '550e8400-e29b-41d4-a716-446655440001',
                kilometraje_vehiculo: 70000,
                movimientos: [
                    {
                        neumatico_id: '550e8400-e29b-41d4-a716-446655440000',
                        posicion_destino_id: '550e8400-e29b-41d4-a716-446655440002'
                    },
                    {
                        neumatico_id: '550e8400-e29b-41d4-a716-446655440003',
                        posicion_destino_id: '550e8400-e29b-41d4-a716-446655440002' // Duplicate
                    }
                ]
            };

            const result = RotacionNeumaticoSchema.safeParse(invalidData);
            expect(result.success).toBe(false);
        });
    });
});
