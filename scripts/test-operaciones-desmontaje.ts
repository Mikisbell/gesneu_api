import { OperacionesNeumaticosService } from '../src/lib/services/operaciones-neumaticos.service';
import { prisma } from '../src/lib/prisma';
import { EstadoNeumaticoEnum } from '@prisma/client';

async function main() {
    console.log('🚀 Iniciando prueba de Operaciones: Desmontaje...');

    const service = new OperacionesNeumaticosService();

    try {
        // 1. SETUP: Usar el mismo setup del montaje para crear un neumatico instalado
        const tipoVehiculo = await prisma.tipoVehiculo.findFirst({
            include: { configuraciones: { include: { posiciones: true } } }
        });

        const posicion = tipoVehiculo?.configuraciones[0]?.posiciones[0];
        if (!posicion) throw new Error('No hay posiciones configuradas');

        const vehiculo = await prisma.vehiculo.create({
            data: {
                placa: `T-DES-${Math.floor(Math.random() * 1000)}`,
                tipo_vehiculo_id: tipoVehiculo!.id,
                marca: 'Test Ops',
                modelo: 'X2',
                anio: 2024,
                kilometraje_actual: 2000
            }
        });

        const modeloNeumatico = await prisma.modeloNeumatico.findFirst();
        const fabricante = await prisma.fabricanteNeumatico.findFirst();

        // Crear almacén si no existe
        let almacen = await prisma.almacen.findFirst();
        if (!almacen) {
            almacen = await prisma.almacen.create({
                data: { nombre: 'Almacén Test', codigo: 'ALM-TST', ubicacion: 'Test' }
            });
        }

        const neumatico = await prisma.neumatico.create({
            data: {
                numero_serie: `NEU-DES-${Math.floor(Math.random() * 1000)}`,
                modelo_id: modeloNeumatico!.id,
                dot: '2024',
                profundidad_inicial_mm: 18,
                profundidad_actual_mm: 15,
                estado_actual: EstadoNeumaticoEnum.EN_STOCK,
                ubicacion_almacen_id: almacen.id
            }
        });

        console.log(`📝 Datos listos: Vehículo ${vehiculo.placa}, Neumático ${neumatico.numero_serie}`);

        // 2. MONTAR el neumático primero
        console.log('🔧 Montando neumático...');
        await service.montarNeumatico({
            neumatico_id: neumatico.id,
            vehiculo_id: vehiculo.id,
            posicion_id: posicion.id,
            kilometraje_vehiculo: 2000,
            presion_psi: 110
        });

        // 3. DESMONTAR el neumático
        console.log('🔧 Desmontando neumático a STOCK...');
        const resultado = await service.desmontarNeumatico({
            neumatico_id: neumatico.id,
            destino: 'STOCK',
            kilometraje_vehiculo: 2500,
            almacen_destino_id: almacen.id,
            profundidad_remanente_mm: 14,
            presion_psi: 105,
            observaciones: 'Desmontaje de prueba'
        });

        // 4. VERIFICACIÓN
        console.log('🔍 Verificando resultados...');

        if (resultado.estado_actual === EstadoNeumaticoEnum.EN_STOCK &&
            resultado.ubicacion_almacen_id === almacen.id &&
            resultado.ubicacion_vehiculo_id === null &&
            resultado.ubicacion_posicion_id === null) {
            console.log('✅ Neumático desmontado correctamente (Estado: EN_STOCK, Sin Vehículo)');
        } else {
            console.error('❌ Error: El neumático no se actualizó correctamente');
        }

        const evento = await prisma.eventoNeumatico.findFirst({
            where: { neumatico_id: neumatico.id, tipo_evento: 'DESMONTAJE' }
        });

        if (evento) {
            console.log('✅ Evento de desmontaje registrado correctamente');
        } else {
            console.error('❌ Error: No se registró el evento de desmontaje');
        }

        // 5. LIMPIEZA
        console.log('🧹 Limpiando...');
        await prisma.eventoNeumatico.deleteMany({ where: { neumatico_id: neumatico.id } });
        await prisma.historialEstadoNeumatico.deleteMany({ where: { neumatico_id: neumatico.id } });
        await prisma.neumatico.delete({ where: { id: neumatico.id } });
        await prisma.vehiculo.delete({ where: { id: vehiculo.id } });

        console.log('✅ Prueba finalizada con éxito');

    } catch (error) {
        console.error('❌ Error en la prueba:', error);
    } finally {
        await prisma.$disconnect();
    }
}

main();
