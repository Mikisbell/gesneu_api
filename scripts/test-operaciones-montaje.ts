import { OperacionesNeumaticosService } from '../src/lib/services/operaciones-neumaticos.service';
import { prisma } from '../src/lib/prisma';
import { EstadoNeumaticoEnum } from '@prisma/client';

async function main() {
    console.log('🚀 Iniciando prueba de Operaciones: Montaje...');

    const service = new OperacionesNeumaticosService();

    try {
        // 1. PREPARACIÓN DE DATOS
        console.log('🛠️ Preparando datos de prueba...');

        // a) Obtener un Tipo de Vehículo y su configuración de ejes
        const tipoVehiculo = await prisma.tipoVehiculo.findFirst({
            include: { configuraciones: true }
        });

        if (!tipoVehiculo || tipoVehiculo.configuraciones.length === 0) {
            // Si no hay configuración, la creamos (esto pasa si el seed no creó configs de eje)
            console.log('⚠️ Creando configuración de ejes faltante...');
            // Asumimos que existe el tipo, si no el script fallará antes
            if (tipoVehiculo) {
                const config = await prisma.configuracionEje.create({
                    data: {
                        tipo_vehiculo_id: tipoVehiculo.id,
                        numero_eje: 1,
                        posiciones_neumatico: 2,
                        tipo_eje: 'DIRECCION'
                    }
                });
                // Crear posiciones para ese eje
                await prisma.posicionNeumatico.create({
                    data: { configuracion_eje_id: config.id, numero_posicion: 1, lado_vehiculo: 'IZQUIERDO' }
                });
                await prisma.posicionNeumatico.create({
                    data: { configuracion_eje_id: config.id, numero_posicion: 2, lado_vehiculo: 'DERECHO' }
                });
            }
        }

        // Recargar con posiciones
        const tipoConPosiciones = await prisma.tipoVehiculo.findFirst({
            where: { id: tipoVehiculo?.id },
            include: {
                configuraciones: {
                    include: { posiciones: true }
                }
            }
        });

        const posicion = tipoConPosiciones?.configuraciones[0].posiciones[0];
        if (!posicion) throw new Error('No se encontraron posiciones de neumático disponibles');

        // b) Crear Vehículo
        const vehiculo = await prisma.vehiculo.create({
            data: {
                placa: `T-OP-${Math.floor(Math.random() * 1000)}`,
                tipo_vehiculo_id: tipoConPosiciones!.id,
                marca: 'Test Ops',
                modelo: 'X1',
                anio: 2024,
                kilometraje_actual: 1000
            }
        });

        // c) Crear Neumático (en Stock)
        const modeloNeumatico = await prisma.modeloNeumatico.findFirst();
        const neumatico = await prisma.neumatico.create({
            data: {
                numero_serie: `NEU-OP-${Math.floor(Math.random() * 1000)}`,
                modelo_id: modeloNeumatico!.id,
                dot: '2024',
                profundidad_inicial_mm: 18,
                estado_actual: EstadoNeumaticoEnum.EN_STOCK
            }
        });

        console.log(`📝 Datos listos: Vehículo ${vehiculo.placa}, Neumático ${neumatico.numero_serie}`);

        // 2. EJECUTAR MONTAJE
        console.log('🔧 Ejecutando montaje...');
        const resultado = await service.montarNeumatico({
            neumatico_id: neumatico.id,
            vehiculo_id: vehiculo.id,
            posicion_id: posicion.id,
            kilometraje_vehiculo: 1050,
            presion_psi: 110,
            observaciones: 'Montaje de prueba script'
        });

        // 3. VERIFICACIÓN
        console.log('🔍 Verificando resultados...');

        if (resultado.estado_actual === EstadoNeumaticoEnum.INSTALADO &&
            resultado.ubicacion_vehiculo_id === vehiculo.id &&
            resultado.ubicacion_posicion_id === posicion.id) {
            console.log('✅ Neumático actualizado correctamente (Estado y Ubicación)');
        } else {
            console.error('❌ Error: El neumático no se actualizó correctamente');
        }

        const evento = await prisma.eventoNeumatico.findFirst({
            where: { neumatico_id: neumatico.id, tipo_evento: 'INSTALACION' }
        });

        if (evento) {
            console.log('✅ Evento de montaje registrado correctamente');
        } else {
            console.error('❌ Error: No se registró el evento');
        }

        // 4. LIMPIEZA
        console.log('🧹 Limpiando...');
        await prisma.eventoNeumatico.deleteMany({ where: { neumatico_id: neumatico.id } });
        await prisma.historialEstadoNeumatico.deleteMany({ where: { neumatico_id: neumatico.id } });
        await prisma.neumatico.delete({ where: { id: neumatico.id } });
        await prisma.vehiculo.delete({ where: { id: vehiculo.id } });
        // No borramos tipos/posiciones para no afectar otros tests

        console.log('✅ Prueba finalizada con éxito');

    } catch (error) {
        console.error('❌ Error en la prueba:', error);
    } finally {
        await prisma.$disconnect();
    }
}

main();
