import { prisma } from '@/lib/prisma';
import {
    CreateParametroSistemaInput,
    UpdateParametroSistemaInput,
    SetByKeyInput
} from '@/lib/validators/parametro-sistema.validator';
import {
    Result,
    ok,
    err,
    BusinessError,
    NotFoundError,
    ConflictError
} from '@/types/result.types';

export class ParametroSistemaService {
    async create(data: CreateParametroSistemaInput, actualizado_por?: string): Promise<Result<any>> {
        try {
            // Check if key already exists
            const existing = await prisma.parametroSistema.findUnique({
                where: { clave: data.clave }
            });

            if (existing) {
                return err(new ConflictError(`Ya existe un parametro con la clave "${data.clave}"`));
            }

            const parametro = await prisma.parametroSistema.create({
                data: {
                    clave: data.clave,
                    valor: data.valor,
                    tipo_dato: data.tipo_dato,
                    categoria: data.categoria || null,
                    descripcion: data.descripcion || null,
                    valor_default: data.valor_default || null,
                    editable: data.editable,
                    requiere_reinicio: data.requiere_reinicio,
                    actualizado_por: actualizado_por || null
                }
            });

            return ok(parametro);
        } catch (error) {
            console.error('[ParametroSistemaService.create] Error:', error);
            return err(new BusinessError('Error al crear parametro del sistema', 'CREATE_ERROR', 500));
        }
    }

    async getAll(): Promise<Result<any>> {
        try {
            const parametros = await prisma.parametroSistema.findMany({
                orderBy: [
                    { categoria: 'asc' },
                    { clave: 'asc' }
                ]
            });

            // Group by category
            const grouped: Record<string, any[]> = {};

            for (const param of parametros) {
                const cat = param.categoria || 'GENERAL';
                if (!grouped[cat]) {
                    grouped[cat] = [];
                }
                grouped[cat].push({
                    id: param.id,
                    clave: param.clave,
                    valor: param.valor,
                    tipo_dato: param.tipo_dato,
                    descripcion: param.descripcion,
                    valor_default: param.valor_default,
                    editable: param.editable,
                    requiere_reinicio: param.requiere_reinicio,
                    actualizado_en: param.actualizado_en.toISOString()
                });
            }

            return ok({
                grouped,
                flat: parametros.map(p => ({
                    id: p.id,
                    clave: p.clave,
                    valor: p.valor,
                    tipo_dato: p.tipo_dato,
                    categoria: p.categoria,
                    descripcion: p.descripcion,
                    valor_default: p.valor_default,
                    editable: p.editable,
                    requiere_reinicio: p.requiere_reinicio,
                    actualizado_en: p.actualizado_en.toISOString()
                }))
            });
        } catch (error) {
            console.error('[ParametroSistemaService.getAll] Error:', error);
            return err(new BusinessError('Error al obtener parametros del sistema', 'QUERY_ERROR', 500));
        }
    }

    async getById(id: string): Promise<Result<any>> {
        try {
            const parametro = await prisma.parametroSistema.findUnique({
                where: { id }
            });

            if (!parametro) {
                return err(new NotFoundError('Parametro del sistema'));
            }

            return ok(parametro);
        } catch (error) {
            console.error('[ParametroSistemaService.getById] Error:', error);
            return err(new BusinessError('Error al obtener parametro del sistema', 'QUERY_ERROR', 500));
        }
    }

    async update(id: string, data: UpdateParametroSistemaInput): Promise<Result<any>> {
        try {
            const existing = await prisma.parametroSistema.findUnique({
                where: { id }
            });

            if (!existing) {
                return err(new NotFoundError('Parametro del sistema'));
            }

            if (!existing.editable) {
                return err(new BusinessError('Este parametro del sistema no es editable', 'SYSTEM_PARAMETER', 403));
            }

            const updated = await prisma.parametroSistema.update({
                where: { id },
                data: {
                    valor: data.valor,
                    tipo_dato: data.tipo_dato,
                    categoria: data.categoria,
                    descripcion: data.descripcion,
                    valor_default: data.valor_default,
                    editable: data.editable,
                    requiere_reinicio: data.requiere_reinicio
                }
            });

            return ok(updated);
        } catch (error) {
            console.error('[ParametroSistemaService.update] Error:', error);
            return err(new BusinessError('Error al actualizar parametro del sistema', 'UPDATE_ERROR', 500));
        }
    }

    async delete(id: string): Promise<Result<void>> {
        try {
            const existing = await prisma.parametroSistema.findUnique({
                where: { id }
            });

            if (!existing) {
                return err(new NotFoundError('Parametro del sistema'));
            }

            if (existing.es_sistema) {
                return err(new BusinessError('No se puede eliminar un parametro del sistema', 'SYSTEM_PARAMETER', 403));
            }

            await prisma.parametroSistema.delete({
                where: { id }
            });

            return ok(undefined);
        } catch (error) {
            console.error('[ParametroSistemaService.delete] Error:', error);
            return err(new BusinessError('Error al eliminar parametro del sistema', 'DELETE_ERROR', 500));
        }
    }

    async getByKey(key: string): Promise<Result<any>> {
        try {
            const parametro = await prisma.parametroSistema.findUnique({
                where: { clave: key }
            });

            if (!parametro) {
                return err(new NotFoundError(`Parametro con clave "${key}"`));
            }

            return ok({
                id: parametro.id,
                clave: parametro.clave,
                valor: parametro.valor,
                tipo_dato: parametro.tipo_dato,
                categoria: parametro.categoria,
                descripcion: parametro.descripcion,
                valor_default: parametro.valor_default,
                editable: parametro.editable,
                requiere_reinicio: parametro.requiere_reinicio,
                actualizado_en: parametro.actualizado_en.toISOString()
            });
        } catch (error) {
            console.error('[ParametroSistemaService.getByKey] Error:', error);
            return err(new BusinessError('Error al obtener parametro por clave', 'QUERY_ERROR', 500));
        }
    }

    async setByKey(key: string, data: SetByKeyInput, actualizado_por?: string): Promise<Result<any>> {
        try {
            const existing = await prisma.parametroSistema.findUnique({
                where: { clave: key }
            });

            if (!existing) {
                return err(new NotFoundError(`Parametro con clave "${key}"`));
            }

            if (!existing.editable) {
                return err(new BusinessError('Este parametro del sistema no es editable', 'SYSTEM_PARAMETER', 403));
            }

            const updateData: any = {
                valor: data.valor
            };

            if (data.tipo_dato !== undefined) updateData.tipo_dato = data.tipo_dato;
            if (data.descripcion !== undefined) updateData.descripcion = data.descripcion;
            if (data.editable !== undefined) updateData.editable = data.editable;
            if (data.requiere_reinicio !== undefined) updateData.requiere_reinicio = data.requiere_reinicio;
            if (actualizado_por) updateData.actualizado_por = actualizado_por;

            const updated = await prisma.parametroSistema.update({
                where: { clave: key },
                data: updateData
            });

            return ok(updated);
        } catch (error) {
            console.error('[ParametroSistemaService.setByKey] Error:', error);
            return err(new BusinessError('Error al actualizar parametro por clave', 'UPDATE_ERROR', 500));
        }
    }

    async getAllGrouped(): Promise<Result<Record<string, any[]>>> {
        try {
            const parametros = await prisma.parametroSistema.findMany({
                orderBy: [
                    { categoria: 'asc' },
                    { clave: 'asc' }
                ]
            });

            const grouped: Record<string, any[]> = {};

            for (const param of parametros) {
                const cat = param.categoria || 'GENERAL';
                if (!grouped[cat]) {
                    grouped[cat] = [];
                }
                grouped[cat].push({
                    id: param.id,
                    clave: param.clave,
                    valor: param.valor,
                    tipo_dato: param.tipo_dato,
                    descripcion: param.descripcion,
                    valor_default: param.valor_default,
                    editable: param.editable,
                    requiere_reinicio: param.requiere_reinicio,
                    actualizado_en: param.actualizado_en.toISOString()
                });
            }

            return ok(grouped);
        } catch (error) {
            console.error('[ParametroSistemaService.getAllGrouped] Error:', error);
            return err(new BusinessError('Error al obtener parametros agrupados', 'QUERY_ERROR', 500));
        }
    }
}

export const parametroSistemaService = new ParametroSistemaService();
