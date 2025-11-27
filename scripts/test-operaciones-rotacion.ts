import { OperacionesNeumaticosService } from '../src/lib/services/operaciones-neumaticos.service';
import { prisma } from '../src/lib/prisma';
import { EstadoNeumaticoEnum } from '@prisma/client';

async function main() {
    console.log('🚀 Iniciando prueba de Operaciones: Rotación...');

    const service = new OperacionesNeumaticosService();

    try {
        // 1. SETUP
        const tipoVehiculo = await prisma.tipoVehiculo.findFirst({
            include: { configuraciones: { include: { posiciones: true } } }
        });

        const posiciones = tipoVehiculo?.configuraciones[0]?.posiciones;
        if (!posiciones || posiciones.length < 2) {
            throw new Error('Se necesitan al menos 2 posiciones configuradas');
        }

        const vehiculo = await prisma.vehiculo.create({
            data: {
                placa: `T-ROT-${Math.floor(Math.random() * 1000)}`,
                tipo_vehiculo_id: tipoVehiculo!.id,
                marca: 'Test Ops',
                modelo: 'X3',
                anio: 2024,
                kilometraje_actual: 3000
            }
        });

        const modeloNeumatico = await prisma.modeloNeumatico.findFirst();

        // Crear 2 neumáticos y montarlos
        const neumatico1 = await prisma.neumatico.create({
            data: {
                numero_serie: `NEU-ROT1-${Math.floor(Math.random() * 1000)}`,
                modelo_id: modeloNeumatico!.id,
                dot: '2024',
                profundidad_inicial_mm: 18,
                estado_actual: EstadoNeumaticoEnum.EN_STOCK
            }
        });

        const neumatico2 = await prisma.neumatico.create({
            data: {
                numero_serie: `NEU-ROT2-${Math.floor(Math.random() * 1000)}`,
                modelo_id: modeloNeumatico!.id,
                dot: '2024',
                profundidad_inicial_mm: 18,
                estado_actual: EstadoNeumaticoEnum.EN_STOCK
            }
        });

        console.log(`📝 Datos listos: Vehículo ${vehiculo.placa}, Neumáticos ${neumatico1.numero_serie} y ${neumatico2.numero_serie}`);

        // 2. MONTAR ambos neumáticos
        console.log('🔧 Montando neumáticos en posiciones iniciales...');
        await service.montarNeumatico({
            neumatico_id: neumatico1.id,
            vehiculo_id: vehiculo.id,
            posicion_id: posiciones[0].id,
            kilometraje_vehiculo: 3000,
            presion_psi: 110
        });

        await service.montarNeumatico({
            neumatico_id: neumatico2.id,
            vehiculo_id: vehiculo.id,
            posicion_id: posiciones[1].id,
            kilometraje_vehiculo: 3000,
            presion_psi: 110
        });

        console.log(`   Neumático 1 en posición ${posiciones[0].numero_posicion}`);
        console.log(`   Neumático 2 en posición ${posiciones[1].numero_posicion}`);

        // 3. ROTAR (intercambiar posiciones)
        console.log('🔄 Rotando neumáticos...');
        const resultado = await service.rotarNeumaticos({
            vehiculo_id: vehiculo.id,
            kilometraje_vehiculo: 3500,
            movimientos: [
                { neumatico_id: neumatico1.id, posicion_destino_id: posiciones[1].id },
                { neumatico_id: neumatico2.id, posicion_destino_id: posiciones[0].id }
            ],
            observaciones: 'Rotación de prueba'
        });

        // 4. VERIFICACIÓN
        console.log('🔍 Verificando resultados...');

        const neumaticoActualizado1 = await prisma.neumatico.findUnique({
            where: { id: neumatico1.id }
        });

        const neumaticoActualizado2 = await prisma.neumatico.findUnique({
            where: { id: neumatico2.id }
        });

        if (neumaticoActualizado1?.ubicacion_posicion_id === posiciones[1].id &&
            neumaticoActualizado2?.ubicacion_posicion_id === posiciones[0].id) {
            console.log('✅ Neumáticos rotados correctamente (Posiciones intercambiadas)');
        } else {
            console.error('❌ Error: Las posiciones no se actualizaron correctamente');
        }

        const eventos = await prisma.eventoNeumatico.findMany({
            where: {
                neumatico_id: { in: [neumatico1.id, neumatico2.id] },
                tipo_evento: 'ROTACION'
            }
        });

        if (eventos.length === 2) {
            console.log('✅ Eventos de rotación registrados correctamente');
        } else {
            console.error(`❌ Error: Se esperaban 2 eventos, se encontraron ${eventos.length}`);
        }

        // 5. LIMPIEZA
        console.log('🧹 Limpiando...');
        await prisma.eventoNeumatico.deleteMany({
            where: { neumatico_id: { in: [neumatico1.id, neumatico2.id] } }
        });
        await prisma.historialEstadoNeumatico.deleteMany({
            where: { neumatico_id: { in: [neumatico1.id, neumatico2.id] } }
        });
        await prisma.neumatico.delete({ where: { id: neumatico1.id } });
        await prisma.neumatico.delete({ where: { id: neumatico2.id } });
        await prisma.vehiculo.delete({ where: { id: vehiculo.id } });

        console.log('✅ Prueba finalizada con éxito');

    } catch (error) {
        console.error('❌ Error en la prueba:', error);
    } finally {
        await prisma.$disconnect();
    }
}

main();
