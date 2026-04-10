import { prisma } from '@/lib/prisma';
import { VehiculoService } from '@/lib/services/vehiculo.service';
import { NeumaticoService } from '@/lib/services/neumatico.service';
import { UsuarioService } from '@/lib/services/usuario.service';
import { VehiculoId, EmpresaId, UsuarioId } from '@/types/branded.types';
import { CreateVehiculoDTO } from '@/types/domain/vehiculo.types';
import { randomUUID } from 'crypto';

describe('Multi-tenant Isolation', () => {
    const vehiculoService = new VehiculoService();
    const neumaticoService = new NeumaticoService();
    const usuarioService = new UsuarioService();

    const tenantA = randomUUID() as EmpresaId;
    const tenantB = randomUUID() as EmpresaId;

    let userAId: UsuarioId;
    let userBId: UsuarioId;

    beforeAll(async () => {
        // Seed Prerequisites: Empresas
        await prisma.empresa.create({
            data: {
                id: tenantA,
                nombre: 'Empresa Tenant A',
                ruc: '20' + Date.now() + '1',
                activo: true
            }
        });
        await prisma.empresa.create({
            data: {
                id: tenantB,
                nombre: 'Empresa Tenant B',
                ruc: '20' + Date.now() + '2',
                activo: true
            }
        });

        // Initialize User IDs (Mocked)
        userAId = randomUUID() as UsuarioId;
        userBId = randomUUID() as UsuarioId;
    });

    afterAll(async () => {
        // Clean up
        // Delete dependent records first
        await prisma.vehiculo.deleteMany({ where: { empresa_id: { in: [tenantA, tenantB] } } });
        await prisma.neumatico.deleteMany({ where: { empresa_id: { in: [tenantA, tenantB] } } });
        await prisma.empresa.deleteMany({ where: { id: { in: [tenantA, tenantB] } } });
    });

    describe('VehiculoService Isolation', () => {
        let vehiculoAId: VehiculoId;

        it('Tenant A should create a vehicle', async () => {
            const dto: CreateVehiculoDTO = {
                placa: 'AAA-111',
                marca: 'TestBrand',
                modelo: 'TestModel',
                tipo_vehiculo_id: 'uuid-dummy-tipo', // Will be replaced
                anio: 2020,
                configuracion_ejes: '2S'
            };

            // Using valid schema fields for TipoVehiculo
            const tipo = await prisma.tipoVehiculo.create({
                data: { nombre: 'Truck ' + randomUUID().substring(0, 8) }
            });
            dto.tipo_vehiculo_id = tipo.id;

            const result = await vehiculoService.create(dto, tenantA);

            if (!result.success) {
                console.error('Create failed:', JSON.stringify(result.error, null, 2));
            }

            expect(result.success).toBe(true);
            if (result.success) {
                vehiculoAId = result.data.id;
                expect(result.data.id).toBeDefined();
            }
        });

        it('Tenant A should see the vehicle', async () => {
            const result = await vehiculoService.getById(tenantA, vehiculoAId);
            expect(result.success).toBe(true);
            if (result.success) {
                // Response does not include empresaId (security)
                expect(result.data.id).toBe(vehiculoAId);
                expect(result.data.placa).toBe('AAA-111');
            }
        });

        it('Tenant B should NOT see the vehicle (NotFound)', async () => {
            const result = await vehiculoService.getById(tenantB, vehiculoAId);
            expect(result.success).toBe(false);
            if (!result.success) {
                expect(result.error.statusCode).toBe(404);
            }
        });

        it('Tenant B should NOT be able to update the vehicle', async () => {
            const result = await vehiculoService.update(tenantB, vehiculoAId, { kilometers: 2000 });
            expect(result.success).toBe(false); // Should be NotFound or Forbidden
        });

        it('Tenant B should NOT see vehicle in getAll', async () => {
            const result = await vehiculoService.getAll(tenantB);
            expect(result.success).toBe(true);
            if (result.success) {
                const found = result.data.find(v => v.id === vehiculoAId);
                expect(found).toBeUndefined();
            }
        });
    });

    describe('NeumaticoService Isolation', () => {
        // Similar tests for Neumatico
        // ...
    });
});
