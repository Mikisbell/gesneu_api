import { describe, it, expect, beforeAll } from 'vitest'
import { NeumaticoFormSchema, CreateNeumaticoSchema } from '@/lib/validators/neumatico.shared'

describe('Neumatico Shared Schema Validation', () => {
    describe('NeumaticoFormSchema', () => {
        it('should validate valid form data with z.coerce', () => {
            const validData = {
                numero_serie: 'NT-001',
                modelo_id: '123e4567-e89b-12d3-a456-426614174000',
                dot: '2423', // Semana 24, año 2023
                profundidad_inicial_mm: '12.5', // String que será convertido
                costo_compra: '250.00', // String que será convertido
                sensor_id: 'SENSOR-123',
                ubicacion_almacen_id: '123e4567-e89b-12d3-a456-426614174001'
            }

            const result = NeumaticoFormSchema.safeParse(validData)
            expect(result.success).toBe(true)
            if (result.success) {
                // Verificar que z.coerce convirtió los strings a numbers
                expect(typeof result.data.profundidad_inicial_mm).toBe('number')
                expect(result.data.profundidad_inicial_mm).toBe(12.5)
            }
        })

        it('should reject invalid DOT format', () => {
            const invalidData = {
                modelo_id: '123e4567-e89b-12d3-a456-426614174000',
                dot: '5499', // Semana 54 es inválida (max 53)
                profundidad_inicial_mm: 12
            }

            const result = NeumaticoFormSchema.safeParse(invalidData)
            expect(result.success).toBe(false)
            if (!result.success) {
                expect(result.error.issues[0].message).toContain('DOT inválido')
            }
        })

        it('should reject negative profundidad', () => {
            const invalidData = {
                modelo_id: '123e4567-e89b-12d3-a456-426614174000',
                profundidad_inicial_mm: -5
            }

            const result = NeumaticoFormSchema.safeParse(invalidData)
            expect(result.success).toBe(false)
            if (!result.success) {
                expect(result.error.issues[0].message).toContain('no puede ser negativa')
            }
        })

        it('should validate numero_serie with correct pattern', () => {
            const validData = {
                numero_serie: 'ABC-123-XYZ',
                modelo_id: '123e4567-e89b-12d3-a456-426614174000',
                profundidad_inicial_mm: 10
            }

            const result = NeumaticoFormSchema.safeParse(validData)
            expect(result.success).toBe(true)
        })

        it('should reject numero_serie with invalid characters', () => {
            const invalidData = {
                numero_serie: 'NT#001@', // Caracteres no permitidos
                modelo_id: '123e4567-e89b-12d3-a456-426614174000',
                profundidad_inicial_mm: 10
            }

            const result = NeumaticoFormSchema.safeParse(invalidData)
            expect(result.success).toBe(false)
        })
    })

    describe('CreateNeumaticoSchema', () => {
        it('should validate complete create payload', () => {
            const validData = {
                numero_serie: 'NT-001',
                modelo_id: '123e4567-e89b-12d3-a456-426614174000',
                dot: '2423',
                profundidad_inicial_mm: 12.5,
                costo_compra: 250.00,
                fecha_compra: new Date().toISOString(),
                moneda_compra: 'PEN',
                es_reencauchado: false
            }

            const result = CreateNeumaticoSchema.safeParse(validData)
            expect(result.success).toBe(true)
        })

        it('should reject future fecha_compra', () => {
            const futureDate = new Date()
            futureDate.setFullYear(futureDate.getFullYear() + 1)

            const invalidData = {
                modelo_id: '123e4567-e89b-12d3-a456-426614174000',
                profundidad_inicial_mm: 12,
                fecha_compra: futureDate.toISOString()
            }

            const result = CreateNeumaticoSchema.safeParse(invalidData)
            expect(result.success).toBe(false)
            if (!result.success) {
                expect(result.error.issues.some(i => i.message.includes('futura'))).toBe(true)
            }
        })

        it('should reject very old fecha_compra', () => {
            const invalidData = {
                modelo_id: '123e4567-e89b-12d3-a456-426614174000',
                profundidad_inicial_mm: 12,
                fecha_compra: '1999-01-01T00:00:00Z'
            }

            const result = CreateNeumaticoSchema.safeParse(invalidData)
            expect(result.success).toBe(false)
        })
    })
})
