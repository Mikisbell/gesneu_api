import { prisma } from '@/lib/prisma';
import { MontajeNeumaticoDTO, DesmontajeNeumaticoDTO, RotacionNeumaticoDTO } from '@/types/domain/operaciones.types';
import { EstadoNeumaticoEnum, TipoEventoNeumaticoEnum } from '@prisma/client';

export class OperacionesNeumaticosService {

    /**
     * Realiza el montaje de un neumático en un vehículo
     * Transaccional: Actualiza neumático y crea evento
     */
    async montarNeumatico(data: MontajeNeumaticoDTO) {
        return await prisma.$transaction(async (tx) => {
            // 1. Validaciones
            const neumatico = await tx.neumatico.findUnique({
                where: { id: data.neumatico_id }
            });

            if (!neumatico) throw new Error('Neumático no encontrado');
            if (neumatico.estado_actual === EstadoNeumaticoEnum.INSTALADO) {
                throw new Error('El neumático ya está montado en otro vehículo');
            }
            if (neumatico.estado_actual === EstadoNeumaticoEnum.DESECHADO) {
                throw new Error('No se puede montar un neumático desechado');
            }

            const vehiculo = await tx.vehiculo.findUnique({
                where: { id: data.vehiculo_id },
                include: { tipo_vehiculo: true }
            });

            if (!vehiculo) throw new Error('Vehículo no encontrado');

            // Validar que la posición pertenezca al tipo de vehículo
            // Esto requeriría una query compleja, por ahora confiamos en el ID o hacemos una validación simple
            const posicion = await tx.posicionNeumatico.findUnique({
                where: { id: data.posicion_id },
                include: { configuracion_eje: true }
            });

            if (!posicion) throw new Error('Posición no válida');
            if (posicion.configuracion_eje.tipo_vehiculo_id !== vehiculo.tipo_vehiculo_id) {
                throw new Error('La posición no corresponde al tipo de vehículo');
            }

            // Validar que la posición esté libre en este vehículo
            const ocupante = await tx.neumatico.findFirst({
                where: {
                    ubicacion_vehiculo_id: vehiculo.id,
                    ubicacion_posicion_id: posicion.id,
                    activo: true
                }
            });

            if (ocupante) {
                throw new Error(`La posición ya está ocupada por el neumático ${ocupante.numero_serie}`);
            }

            // 2. Actualizar Neumático
            const neumaticoActualizado = await tx.neumatico.update({
                where: { id: neumatico.id },
                data: {
                    estado_actual: EstadoNeumaticoEnum.INSTALADO,
                    ubicacion_vehiculo_id: vehiculo.id,
                    ubicacion_posicion_id: posicion.id,
                    ubicacion_almacen_id: null, // Sale del almacén
                    presion_actual_psi: data.presion_psi,
                    fecha_instalacion: data.fecha_evento || new Date(),
                    actualizado_en: new Date()
                }
            });

            // 3. Registrar Evento
            await tx.eventoNeumatico.create({
                data: {
                    tipo_evento: TipoEventoNeumaticoEnum.INSTALACION,
                    neumatico_id: neumatico.id,
                    vehiculo_id: vehiculo.id,
                    posicion_montaje_id: posicion.id,
                    fecha_evento: data.fecha_evento || new Date(),
                    kilometraje_vehiculo: data.kilometraje_vehiculo,
                    presion_psi: data.presion_psi,
                    profundidad_remanente: neumatico.profundidad_actual_mm || neumatico.profundidad_inicial_mm,
                    notas: data.observaciones
                }
            });

            // 4. Actualizar historial de estados
            await tx.historialEstadoNeumatico.create({
                data: {
                    neumatico_id: neumatico.id,
                    estado_anterior: neumatico.estado_actual,
                    estado_nuevo: EstadoNeumaticoEnum.INSTALADO,
                    fecha_cambio: new Date(),
                    motivo: `Montaje en vehículo ${vehiculo.placa}`
                }
            });

            return neumaticoActualizado;
        });
    }

    /**
     * Realiza el desmontaje de un neumático de un vehículo
     * Transaccional: Actualiza neumático, crea evento y maneja destino
     */
    async desmontarNeumatico(data: DesmontajeNeumaticoDTO) {
        return await prisma.$transaction(async (tx) => {
            // 1. Validaciones
            const neumatico = await tx.neumatico.findUnique({
                where: { id: data.neumatico_id },
                include: {
                    ubicacion_vehiculo: true,
                    ubicacion_posicion: true
                }
            });

            if (!neumatico) throw new Error('Neumático no encontrado');
            if (neumatico.estado_actual !== EstadoNeumaticoEnum.INSTALADO) {
                throw new Error('El neumático no está instalado en ningún vehículo');
            }
            if (!neumatico.ubicacion_vehiculo_id) {
                throw new Error('El neumático no tiene vehículo asignado');
            }

            // 2. Determinar estado destino según el motivo
            let nuevoEstado: EstadoNeumaticoEnum;
            let tipoEvento: TipoEventoNeumaticoEnum;

            switch (data.destino) {
                case 'STOCK':
                    nuevoEstado = EstadoNeumaticoEnum.EN_STOCK;
                    tipoEvento = TipoEventoNeumaticoEnum.DESMONTAJE;
                    if (!data.almacen_destino_id) {
                        throw new Error('Debe especificar un almacén destino para devolver a stock');
                    }
                    break;
                case 'REPARACION':
                    nuevoEstado = EstadoNeumaticoEnum.EN_REPARACION;
                    tipoEvento = TipoEventoNeumaticoEnum.DESMONTAJE;
                    break;
                case 'REENCAUCHE':
                    nuevoEstado = EstadoNeumaticoEnum.EN_REENCAUCHE;
                    tipoEvento = TipoEventoNeumaticoEnum.REENCAUCHE_ENTRADA;
                    break;
                case 'DESECHO':
                    nuevoEstado = EstadoNeumaticoEnum.DESECHADO;
                    tipoEvento = TipoEventoNeumaticoEnum.DESECHO;
                    if (!data.motivo_id) {
                        throw new Error('Debe especificar un motivo para el desecho');
                    }
                    break;
                default:
                    throw new Error('Destino de desmontaje no válido');
            }

            // 3. Actualizar Neumático
            const neumaticoActualizado = await tx.neumatico.update({
                where: { id: neumatico.id },
                data: {
                    estado_actual: nuevoEstado,
                    ubicacion_vehiculo_id: null,
                    ubicacion_posicion_id: null,
                    ubicacion_almacen_id: data.almacen_destino_id || null,
                    profundidad_actual_mm: data.profundidad_remanente_mm,
                    presion_actual_psi: data.presion_psi,
                    fecha_desecho: data.destino === 'DESECHO' ? (data.fecha_evento || new Date()) : null,
                    actualizado_en: new Date()
                }
            });

            // 4. Registrar Evento
            await tx.eventoNeumatico.create({
                data: {
                    tipo_evento: tipoEvento,
                    neumatico_id: neumatico.id,
                    vehiculo_id: neumatico.ubicacion_vehiculo_id,
                    posicion_montaje_id: neumatico.ubicacion_posicion_id,
                    almacen_destino_id: data.almacen_destino_id,
                    motivo_desecho_id: data.motivo_id,
                    fecha_evento: data.fecha_evento || new Date(),
                    kilometraje_vehiculo: data.kilometraje_vehiculo,
                    presion_psi: data.presion_psi,
                    profundidad_remanente: data.profundidad_remanente_mm,
                    notas: data.observaciones
                }
            });

            // 5. Actualizar historial de estados
            await tx.historialEstadoNeumatico.create({
                data: {
                    neumatico_id: neumatico.id,
                    estado_anterior: neumatico.estado_actual,
                    estado_nuevo: nuevoEstado,
                    fecha_cambio: new Date(),
                    motivo: `Desmontaje de vehículo ${neumatico.ubicacion_vehiculo?.placa} - Destino: ${data.destino}`
                }
            });

            return neumaticoActualizado;
        });
    }

    /**
     * Realiza la rotación de neumáticos en un vehículo
     * Transaccional: Mueve múltiples neumáticos entre posiciones
     */
    async rotarNeumaticos(data: RotacionNeumaticoDTO) {
        return await prisma.$transaction(async (tx) => {
            // 1. Validar vehículo
            const vehiculo = await tx.vehiculo.findUnique({
                where: { id: data.vehiculo_id }
            });

            if (!vehiculo) throw new Error('Vehículo no encontrado');

            // 2. Validar que todos los neumáticos existen y están instalados en el vehículo
            const neumaticosIds = data.movimientos.map(m => m.neumatico_id);
            const neumaticos = await tx.neumatico.findMany({
                where: {
                    id: { in: neumaticosIds },
                    ubicacion_vehiculo_id: vehiculo.id,
                    estado_actual: EstadoNeumaticoEnum.INSTALADO
                }
            });

            if (neumaticos.length !== neumaticosIds.length) {
                throw new Error('Algunos neumáticos no están instalados en este vehículo');
            }

            // 3. Validar que no hay conflictos en posiciones destino
            const posicionesDestino = data.movimientos.map(m => m.posicion_destino_id);
            const posicionesSet = new Set(posicionesDestino);
            if (posicionesSet.size !== posicionesDestino.length) {
                throw new Error('Hay posiciones destino duplicadas');
            }

            // 4. Realizar los movimientos (primero liberamos, luego asignamos para evitar conflictos)
            // Paso 4a: Liberar todas las posiciones (temporal a null)
            for (const movimiento of data.movimientos) {
                await tx.neumatico.update({
                    where: { id: movimiento.neumatico_id },
                    data: { ubicacion_posicion_id: null }
                });
            }

            // Paso 4b: Asignar nuevas posiciones
            const resultados = [];
            for (const movimiento of data.movimientos) {
                const neumaticoActualizado = await tx.neumatico.update({
                    where: { id: movimiento.neumatico_id },
                    data: {
                        ubicacion_posicion_id: movimiento.posicion_destino_id,
                        actualizado_en: new Date()
                    }
                });

                // 5. Registrar evento de rotación para cada neumático
                await tx.eventoNeumatico.create({
                    data: {
                        tipo_evento: TipoEventoNeumaticoEnum.ROTACION,
                        neumatico_id: movimiento.neumatico_id,
                        vehiculo_id: vehiculo.id,
                        posicion_montaje_id: movimiento.posicion_destino_id,
                        fecha_evento: new Date(),
                        kilometraje_vehiculo: data.kilometraje_vehiculo,
                        notas: data.observaciones || 'Rotación de neumáticos'
                    }
                });

                resultados.push(neumaticoActualizado);
            }

            return resultados;
        });
    }
}
