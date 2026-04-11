import { prisma } from '@/lib/prisma';
import {
    CreateTareaProgramadaInput,
    UpdateTareaProgramadaInput
} from '@/lib/validators/tarea-programada.validator';
import {
    Result,
    ok,
    err,
    BusinessError,
    NotFoundError
} from '@/types/result.types';
import { Prisma } from '@prisma/client';

export class TareaProgramadaService {
    async create(data: CreateTareaProgramadaInput): Promise<Result<any>> {
        try {
            const tarea = await prisma.tareaProgramada.create({
                data: {
                    nombre: data.nombre,
                    tipo: data.tipo as any,
                    cron_expresion: data.cron_expresion || null,
                    intervalo_minutos: data.intervalo_minutos || null,
                    proxima_ejecucion: data.proxima_ejecucion || null,
                    parametros: data.parametros ? (data.parametros as Prisma.InputJsonValue) : Prisma.JsonNull,
                    max_reintentos: data.max_reintentos,
                    activo: data.activo
                }
            });

            return ok(tarea);
        } catch (error) {
            console.error('[TareaProgramadaService.create] Error:', error);
            const message = error instanceof Error ? error.message : 'unknown';
            return err(new BusinessError(`Error al crear tarea programada: ${message}`, 'CREATE_ERROR', 500));
        }
    }

    async getAll(): Promise<Result<any[]>> {
        try {
            const tareas = await prisma.tareaProgramada.findMany({
                orderBy: {
                    creado_en: 'desc'
                }
            });

            return ok(tareas);
        } catch (error) {
            console.error('[TareaProgramadaService.getAll] Error:', error);
            return err(new BusinessError('Error al obtener tareas programadas', 'QUERY_ERROR', 500));
        }
    }

    async getById(id: string): Promise<Result<any>> {
        try {
            const tarea = await prisma.tareaProgramada.findUnique({
                where: { id },
                include: {
                    ejecuciones: {
                        orderBy: { inicio: 'desc' },
                        take: 10
                    }
                }
            });

            if (!tarea) {
                return err(new NotFoundError('Tarea programada'));
            }

            return ok(tarea);
        } catch (error) {
            console.error('[TareaProgramadaService.getById] Error:', error);
            return err(new BusinessError('Error al obtener tarea programada', 'QUERY_ERROR', 500));
        }
    }

    async update(id: string, data: UpdateTareaProgramadaInput): Promise<Result<any>> {
        try {
            const existing = await prisma.tareaProgramada.findUnique({
                where: { id }
            });

            if (!existing) {
                return err(new NotFoundError('Tarea programada'));
            }

            const updateData: any = {};

            if (data.nombre !== undefined) updateData.nombre = data.nombre;
            if (data.tipo !== undefined) updateData.tipo = data.tipo;
            if (data.cron_expresion !== undefined) updateData.cron_expresion = data.cron_expresion;
            if (data.intervalo_minutos !== undefined) updateData.intervalo_minutos = data.intervalo_minutos;
            if (data.proxima_ejecucion !== undefined) updateData.proxima_ejecucion = data.proxima_ejecucion;
            if (data.parametros !== undefined) updateData.parametros = data.parametros as Prisma.InputJsonValue;
            if (data.max_reintentos !== undefined) updateData.max_reintentos = data.max_reintentos;
            if (data.activo !== undefined) updateData.activo = data.activo;

            const updated = await prisma.tareaProgramada.update({
                where: { id },
                data: updateData
            });

            return ok(updated);
        } catch (error) {
            console.error('[TareaProgramadaService.update] Error:', error);
            return err(new BusinessError('Error al actualizar tarea programada', 'UPDATE_ERROR', 500));
        }
    }

    async delete(id: string): Promise<Result<void>> {
        try {
            const existing = await prisma.tareaProgramada.findUnique({
                where: { id }
            });

            if (!existing) {
                return err(new NotFoundError('Tarea programada'));
            }

            await prisma.tareaProgramada.delete({
                where: { id }
            });

            return ok(undefined);
        } catch (error) {
            console.error('[TareaProgramadaService.delete] Error:', error);
            return err(new BusinessError('Error al eliminar tarea programada', 'DELETE_ERROR', 500));
        }
    }

    async executeNow(id: string): Promise<Result<any>> {
        try {
            const tarea = await prisma.tareaProgramada.findUnique({
                where: { id }
            });

            if (!tarea) {
                return err(new NotFoundError('Tarea programada'));
            }

            if (!tarea.activo) {
                return err(new BusinessError('La tarea no esta activa', 'INACTIVE_TASK', 400));
            }

            // Create an execution record
            const ejecucion = await prisma.ejecucionTarea.create({
                data: {
                    tarea_id: id,
                    estado: 'EN_EJECUCION' as any
                }
            });

            // Update task's last execution and next execution
            const nextExec = tarea.intervalo_minutos
                ? new Date(Date.now() + tarea.intervalo_minutos * 60 * 1000)
                : null;

            const updatedTask = await prisma.tareaProgramada.update({
                where: { id },
                data: {
                    ultima_ejecucion: new Date(),
                    proxima_ejecucion: nextExec,
                    estado: 'EN_EJECUCION' as any
                }
            });

            // Mark execution as completed (simulated immediate completion)
            await prisma.ejecucionTarea.update({
                where: { id: ejecucion.id },
                data: {
                    fin: new Date(),
                    duracion_ms: 0,
                    estado: 'COMPLETADA' as any,
                    resultado: { triggered: 'manual', message: 'Ejecucion manual iniciada exitosamente' } as Prisma.InputJsonValue
                }
            });

            // Reset task status to pending after execution
            await prisma.tareaProgramada.update({
                where: { id },
                data: {
                    estado: 'PENDIENTE' as any
                }
            });

            return ok({
                tarea: updatedTask,
                ejecucion: {
                    id: ejecucion.id,
                    inicio: ejecucion.inicio,
                    estado: 'COMPLETADA'
                }
            });
        } catch (error) {
            console.error('[TareaProgramadaService.executeNow] Error:', error);
            return err(new BusinessError('Error al ejecutar tarea', 'EXECUTE_ERROR', 500));
        }
    }

    async getExecutionHistory(id: string, limit: number = 50): Promise<Result<any[]>> {
        try {
            const tarea = await prisma.tareaProgramada.findUnique({
                where: { id }
            });

            if (!tarea) {
                return err(new NotFoundError('Tarea programada'));
            }

            const ejecuciones = await prisma.ejecucionTarea.findMany({
                where: { tarea_id: id },
                orderBy: { inicio: 'desc' },
                take: limit
            });

            return ok(ejecuciones);
        } catch (error) {
            console.error('[TareaProgramadaService.getExecutionHistory] Error:', error);
            return err(new BusinessError('Error al obtener historial de ejecuciones', 'QUERY_ERROR', 500));
        }
    }
}

export const tareaProgramadaService = new TareaProgramadaService();
