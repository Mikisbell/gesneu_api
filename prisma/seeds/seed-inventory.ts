
import { PrismaClient, EstadoNeumaticoEnum, TipoEventoNeumaticoEnum } from '@prisma/client';
import { addMonths, subMonths, addDays } from 'date-fns';

export async function seedInventory(
    prisma: PrismaClient,
    empresaId: string,
    catalogs: any,
    fleet: any,
    infrastructure: any
) {
    console.log('📦 Seeding Inventory & Simulating History...');

    const { modKmaxS, modMultiZ, modXWorks } = catalogs;
    const { t1, v1 } = fleet;
    const { almacenPrincipal } = infrastructure;

    // FECHA BASE: Hace 6 meses
    const baseDate = subMonths(new Date(), 6);

    // --- 1. NEUMÁTICOS EN STOCK (NUEVOS) ---
    // 5 Goodyear KMAX
    for (let i = 1; i <= 5; i++) {
        await prisma.neumatico.create({
            data: {
                numero_serie: `GY-NEW-${100 + i}`,
                modelo_id: modKmaxS.id,
                dot: '4524',
                estado_actual: EstadoNeumaticoEnum.EN_STOCK,
                profundidad_inicial_mm: 15.8,
                profundidad_remanente_actual_mm: 15.8,
                ubicacion_almacen_id: almacenPrincipal.id,
                costo_compra: 450.00,
                fecha_compra: addDays(baseDate, 10),
                empresa_id: empresaId,
                version: 0
            }
        });
    }

    // --- 2. NEUMÁTICOS MONTADOS CON HISTORIA (VOLQUETE V8-001) ---
    // Volquete 8x4 tiene 12 llantas. Simularemos montaje hace 3 meses.

    // Obtener posiciones del volquete
    const configVolquete = await prisma.configuracionEje.findMany({
        where: { tipo_vehiculo_id: v1.tipo_vehiculo_id },
        include: { posiciones: true }
    });

    // Aplanar posiciones
    const posiciones = configVolquete.flatMap(c => c.posiciones);

    let tireCount = 0;
    for (const pos of posiciones) {
        tireCount++;
        const serie = `MI-V8-${100 + tireCount}`;
        const esDireccion = pos.es_direccion;
        const modeloId = esDireccion ? modMultiZ.id : modXWorks.id; // Multi Z adelante, X Works atrás
        const profundidadInicial = esDireccion ? 16.0 : 22.0;

        // Crear Neumático (Inicialmente Stock hace 4 meses)
        const fechaCompra = addDays(baseDate, 60);
        const neumatico = await prisma.neumatico.create({
            data: {
                numero_serie: serie,
                modelo_id: modeloId,
                dot: '2224',
                estado_actual: EstadoNeumaticoEnum.EN_STOCK, // Se actualizará
                profundidad_inicial_mm: profundidadInicial,
                profundidad_remanente_actual_mm: profundidadInicial,
                ubicacion_almacen_id: almacenPrincipal.id, // Temporal
                costo_compra: 550.00,
                fecha_compra: fechaCompra,
                empresa_id: empresaId,
                version: 0
            }
        });

        // EVENTO 1: MONTAJE (Hace 3 meses)
        const montDate = addMonths(fechaCompra, 1);
        await prisma.eventoNeumatico.create({
            data: {
                tipo_evento: TipoEventoNeumaticoEnum.INSTALACION,
                neumatico_id: neumatico.id,
                fecha_evento: montDate,
                vehiculo_id: v1.id,
                posicion_montaje_id: pos.id,
                profundidad_remanente: profundidadInicial,
                presion_psi: 110,
                contador_vehiculo: 100000, // KM al montar
                creado_por: 'seed-admin' // Simplificar ID
            }
        });

        // Actualizar estado Actual
        await prisma.neumatico.update({
            where: { id: neumatico.id },
            data: {
                estado_actual: EstadoNeumaticoEnum.INSTALADO,
                ubicacion_vehiculo_id: v1.id,
                ubicacion_posicion_id: pos.id,
                ubicacion_almacen_id: null,
                profundidad_remanente_actual_mm: profundidadInicial,
                fecha_ultimo_evento: montDate
            }
        });

        // EVENTO 2: INSPECCION (Hace 1 mes) - Simulamos desgaste
        const inspDate = addMonths(montDate, 2);
        const desgaste = esDireccion ? 2.0 : 3.5; // Más desgaste atrás
        const remanente = profundidadInicial - desgaste;

        await prisma.eventoNeumatico.create({
            data: {
                tipo_evento: TipoEventoNeumaticoEnum.INSPECCION,
                neumatico_id: neumatico.id,
                fecha_evento: inspDate,
                profundidad_remanente: remanente,
                presion_psi: 108, // Ligera pérdida
                contador_vehiculo: 115000, // +15k km
                notas: 'Desgaste normal',
                creado_por: 'seed-admin'
            }
        });

        // Actualizar estado final
        await prisma.neumatico.update({
            where: { id: neumatico.id },
            data: {
                profundidad_remanente_actual_mm: remanente,
                presion_actual_psi: 108,
                kilometraje_acumulado: 15000,
                fecha_ultimo_evento: inspDate
            }
        });
    }

    console.log(`✅ Inventory Seeded: 5 Stock, ${tireCount} Mounted with History.`);
}
