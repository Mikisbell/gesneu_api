import { prisma } from '@/lib/prisma';
import { EventBus } from '../events/core';
import { InspeccionEvents } from '../events/inspeccion.events';
import { FuenteLectura } from '@prisma/client';

export class InspeccionService {

    /**
     * Registra una lectura de presión.
     * Side Effects (handled by observers): Alertas, Actualización de Neumático.
     */
    async registrarPresion(data: {
        neumaticoId: string;
        presionPsi: number;
        empresaId: string; // Contexto Single Tenant (opcional pero bueno mantenerlo)
        usuarioId?: string;
        fuente?: FuenteLectura;
        temperatura?: number;
    }) {
        // 1. Persistir Lectura (Fast Write)
        const lectura = await prisma.lecturaPresion.create({
            data: {
                neumatico_id: data.neumaticoId,
                presion_psi: data.presionPsi,
                fuente: data.fuente || 'MANUAL',
                temperatura_c: data.temperatura,
                creado_por: data.usuarioId,
            }
        });

        // 2. Emitir Evento
        await EventBus.publish(InspeccionEvents.PRESSURE_READ, {
            lecturaId: lectura.id,
            neumaticoId: data.neumaticoId,
            empresaId: data.empresaId,
            presionPsi: Number(data.presionPsi),
            fuente: lectura.fuente,
            usuarioId: data.usuarioId
        });

        return lectura;
    }

    /**
     * Registra una medición de profundidad (Desgaste).
     */
    async registrarProfundidad(data: {
        neumaticoId: string;
        profundidades: { int: number; cen: number; ext: number };
        empresaId: string;
        kilometraje?: number;
        usuarioId?: string;
        observaciones?: string;
    }) {
        const { int, cen, ext } = data.profundidades;
        const promedio = (int + cen + ext) / 3;

        // 1. Persistir Medición
        const medicion = await prisma.medicionProfundidad.create({
            data: {
                neumatico_id: data.neumaticoId,
                fecha_medicion: new Date(),
                profundidad_int: int,
                profundidad_cen: cen,
                profundidad_ext: ext,
                profundidad_prom: promedio,
                kilometraje: data.kilometraje,
                observaciones: data.observaciones,
                creado_por: data.usuarioId
            }
        });

        // 2. Emitir Evento
        await EventBus.publish(InspeccionEvents.DEPTH_READ, {
            medicionId: medicion.id,
            neumaticoId: data.neumaticoId,
            empresaId: data.empresaId,
            profundidadPromedio: promedio,
            profunidades: { int, cen, ext },
            kilometraje: data.kilometraje,
            usuarioId: data.usuarioId
        });

        return medicion;
    }
}
