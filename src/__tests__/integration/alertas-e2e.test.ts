import { InspeccionService } from '@/lib/services/inspeccion.service';
import { AlertasService } from '@/lib/services/alertas.service';
import { cleanTestData, createTestUser, createTestNeumatico, createTestVehiculo } from '@/../src/__tests__/helpers/database-helpers';
import { prisma } from '@/lib/prisma';
import { TipoAlertaEnum, SeveridadAlertaEnum } from '@prisma/client';

describe('Alertas E2E Flow', () => {
    let inspeccionService: InspeccionService;
    let alertasService: AlertasService;
    let userId: string;
    let neumaticoId: string;
    let vehiculoId: string;

    beforeAll(async () => {
        inspeccionService = new InspeccionService();
        alertasService = new AlertasService();
    });

    beforeEach(async () => {
        // Skip global cleanup to avoid RLS errors
        const user = await createTestUser();
        userId = user.id;

        // Crear vehículo y neumático montado
        const vehiculo = await createTestVehiculo();
        vehiculoId = vehiculo.id;

        const neumatico = await createTestNeumatico({
            profundidad_remanente_actual_mm: 15,
            profundidad_inicial_mm: 18,
            ubicacion_vehiculo_id: vehiculoId, // Montado
            estado_actual: 'INSTALADO'
        });
        neumaticoId = neumatico.id;
    });

    afterAll(async () => {
        // Targeted cleanup
        try {
            if (neumaticoId) {
                await prisma.alerta.deleteMany({ where: { neumatico_id: neumaticoId } });
                await prisma.eventoNeumatico.deleteMany({ where: { neumatico_id: neumaticoId } });
                await prisma.historialEstadoNeumatico.deleteMany({ where: { neumatico_id: neumaticoId } });
                await prisma.neumatico.delete({ where: { id: neumaticoId } });
            }
            if (vehiculoId) await prisma.vehiculo.delete({ where: { id: vehiculoId } });
            if (userId) await prisma.usuario.delete({ where: { id: userId } });
        } catch (error) {
            console.error('Cleanup failed:', error);
        }
        await prisma.$disconnect();
    });

    it('should generate LOW PRESSURE alert automatically when inspection reports low psi', async () => {
        // 1. Registrar Inspección con presión crítica (e.g. 50 PSI vs 80 min)
        // 1. Registrar Inspección con presión crítica (e.g. 50 PSI vs 80 min)
        // Usamos NeumaticoService ya que InspeccionService está deprecado
        const neumaticoService = new (require('@/lib/services/neumatico.service').NeumaticoService)();

        // Obtener usuario completo para empresaId
        const userFull = await prisma.usuario.findUnique({ where: { id: userId } });

        const inspeccion = await neumaticoService.registrarEvento({
            tipo_evento: 'INSPECCION', // TipoEventoNeumaticoEnum.INSPECCION
            neumatico_id: neumaticoId,
            presion_psi: 50, // Critically low
            // temperatura_c: 25, // TODO: Add support in Event Service
            observaciones: 'Prueba E2E Alerta',
            fecha_evento: new Date().toISOString()
        }, userId, userFull?.empresa_id!);

        expect(inspeccion).toBeDefined();

        // 2. Verificar que se creó la alerta en BD
        const alertas = await prisma.alerta.findMany({
            where: { neumatico_id: neumaticoId }
        });

        expect(alertas).toHaveLength(1);
        expect(alertas[0].tipo).toBe(TipoAlertaEnum.PRESION_BAJA);
        expect(alertas[0].severidad).toBe(SeveridadAlertaEnum.CRITICAL); // < 56 PSI (70% de 80) es Critical
        expect(alertas[0].leida).toBe(false);
        expect(alertas[0].mensaje).toContain('presión 50.0 PSI');

        // 3. Verificar que el servicio de alertas la devuelve
        const resultadoGet = await alertasService.getAlertas({ leida: false });
        // Puede haber otras alertas de otros tests si corren en paralelo, pero la nuestra debe estar
        const miAlerta = resultadoGet.find(a => a.id === alertas[0].id);
        expect(miAlerta).toBeDefined();

        // 4. Marcar como leída
        await alertasService.marcarComoLeida(alertas[0].id);

        const alertaActualizada = await prisma.alerta.findUnique({
            where: { id: alertas[0].id }
        });
        expect(alertaActualizada?.leida).toBe(true);
    });

    it('should NOT generate alert if pressure is normal', async () => {
        await inspeccionService.registrarManual({
            neumatico_id: neumaticoId,
            presion_psi: 100, // Normal
            temperatura_c: 25
        }, userId);

        const alertas = await prisma.alerta.findMany({
            where: { neumatico_id: neumaticoId }
        });

        expect(alertas).toHaveLength(0);
    });
});
