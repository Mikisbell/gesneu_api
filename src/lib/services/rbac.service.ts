import { prisma } from '@/lib/prisma';
import { Result, ok, err, BusinessError, NotFoundError, ConflictError } from '@/types/result.types';
import { CreateRolInput, UpdateRolInput, AssignPermisoInput, AssignRolToUserInput } from '@/lib/validators/rbac.validator';

export class RbacService {
    async createRol(
        empresa_id: string,
        userId: string,
        input: CreateRolInput
    ): Promise<Result<any, BusinessError>> {
        try {
            const existing = await prisma.rol.findUnique({
                where: { nombre: input.nombre },
            });

            if (existing) {
                return err(new ConflictError(`Ya existe un rol con el nombre ${input.nombre}`));
            }

            const rol = await prisma.rol.create({
                data: {
                    nombre: input.nombre,
                    descripcion: input.descripcion || null,
                    es_sistema: input.es_sistema,
                    activo: input.activo,
                },
            });

            return ok(rol);
        } catch (error: any) {
            console.error('[RbacService.createRol] Error:', error);
            if (error.code === 'P2002') {
                return err(new ConflictError('Ya existe un rol con este nombre'));
            }
            return err(new BusinessError('Error al crear el rol', 'CREATE_ERROR', 500));
        }
    }

    async deleteRol(
        empresa_id: string,
        rolId: string
    ): Promise<Result<void, BusinessError>> {
        try {
            const rol = await prisma.rol.findUnique({
                where: { id: rolId },
            });

            if (!rol) {
                return err(new NotFoundError('Rol'));
            }

            if (rol.es_sistema) {
                return err(new BusinessError(
                    'No se pueden eliminar roles del sistema',
                    'SYSTEM_ROLE',
                    400
                ));
            }

            const usuariosConRol = await prisma.usuarioRol.count({
                where: { rol_id: rolId },
            });

            if (usuariosConRol > 0) {
                return err(new BusinessError(
                    `No se puede eliminar el rol porque tiene ${usuariosConRol} usuario(s) asignado(s)`,
                    'HAS_USERS',
                    400
                ));
            }

            await prisma.rol.update({
                where: { id: rolId },
                data: { activo: false },
            });

            return ok(undefined);
        } catch (error: any) {
            console.error('[RbacService.deleteRol] Error:', error);
            if (error.code === 'P2025') {
                return err(new NotFoundError('Rol'));
            }
            return err(new BusinessError('Error al eliminar el rol', 'DELETE_ERROR', 500));
        }
    }

    async addPermisoToRol(
        empresa_id: string,
        userId: string,
        rolId: string,
        input: AssignPermisoInput
    ): Promise<Result<any, BusinessError>> {
        try {
            const rol = await prisma.rol.findUnique({
                where: { id: rolId, activo: true },
            });

            if (!rol) {
                return err(new NotFoundError('Rol'));
            }

            const permiso = await prisma.permiso.findUnique({
                where: { id: input.permiso_id, activo: true },
            });

            if (!permiso) {
                return err(new NotFoundError('Permiso'));
            }

            const existing = await prisma.rolPermiso.findUnique({
                where: {
                    rol_id_permiso_id: {
                        rol_id: rolId,
                        permiso_id: input.permiso_id,
                    },
                },
            });

            if (existing) {
                return err(new ConflictError('El permiso ya está asignado a este rol'));
            }

            const rolPermiso = await prisma.rolPermiso.create({
                data: {
                    rol_id: rolId,
                    permiso_id: input.permiso_id,
                    creado_por: userId,
                },
                include: {
                    rol: true,
                    permiso: true,
                },
            });

            return ok(rolPermiso);
        } catch (error: any) {
            console.error('[RbacService.addPermisoToRol] Error:', error);
            if (error.code === 'P2002') {
                return err(new ConflictError('El permiso ya está asignado a este rol'));
            }
            if (error.code === 'P2025') {
                return err(new NotFoundError('Rol o permiso no encontrado'));
            }
            return err(new BusinessError('Error al asignar permiso al rol', 'ASSIGN_ERROR', 500));
        }
    }

    async removePermisoFromRol(
        empresa_id: string,
        rolId: string,
        permisoId: string
    ): Promise<Result<void, BusinessError>> {
        try {
            const rol = await prisma.rol.findUnique({
                where: { id: rolId },
            });

            if (!rol) {
                return err(new NotFoundError('Rol'));
            }

            const existing = await prisma.rolPermiso.findUnique({
                where: {
                    rol_id_permiso_id: {
                        rol_id: rolId,
                        permiso_id: permisoId,
                    },
                },
            });

            if (!existing) {
                return err(new NotFoundError('La asignación de permiso no existe'));
            }

            await prisma.rolPermiso.delete({
                where: {
                    rol_id_permiso_id: {
                        rol_id: rolId,
                        permiso_id: permisoId,
                    },
                },
            });

            return ok(undefined);
        } catch (error: any) {
            console.error('[RbacService.removePermisoFromRol] Error:', error);
            if (error.code === 'P2025') {
                return err(new NotFoundError('Rol o permiso no encontrado'));
            }
            return err(new BusinessError('Error al remover permiso del rol', 'REMOVE_ERROR', 500));
        }
    }

    async assignRolToUser(
        empresa_id: string,
        adminUserId: string,
        targetUserId: string,
        input: AssignRolToUserInput
    ): Promise<Result<any, BusinessError>> {
        try {
            const rol = await prisma.rol.findUnique({
                where: { id: input.rol_id, activo: true },
            });

            if (!rol) {
                return err(new NotFoundError('Rol'));
            }

            const targetUser = await prisma.usuario.findUnique({
                where: { id: targetUserId },
            });

            if (!targetUser) {
                return err(new NotFoundError('Usuario'));
            }

            const existing = await prisma.usuarioRol.findUnique({
                where: {
                    usuario_id_rol_id: {
                        usuario_id: targetUserId,
                        rol_id: input.rol_id,
                    },
                },
            });

            if (existing) {
                return err(new ConflictError('El usuario ya tiene este rol asignado'));
            }

            const usuarioRol = await prisma.usuarioRol.create({
                data: {
                    usuario_id: targetUserId,
                    rol_id: input.rol_id,
                    es_principal: input.es_principal,
                    valido_desde: input.valido_desde || new Date(),
                    valido_hasta: input.valido_hasta || null,
                    creado_por: adminUserId,
                },
                include: {
                    rol: true,
                },
            });

            return ok(usuarioRol);
        } catch (error: any) {
            console.error('[RbacService.assignRolToUser] Error:', error);
            if (error.code === 'P2002') {
                return err(new ConflictError('El usuario ya tiene este rol asignado'));
            }
            if (error.code === 'P2025') {
                return err(new NotFoundError('Rol o usuario no encontrado'));
            }
            return err(new BusinessError('Error al asignar rol al usuario', 'ASSIGN_ERROR', 500));
        }
    }

    async removeRolFromUser(
        empresa_id: string,
        targetUserId: string,
        rolId: string
    ): Promise<Result<void, BusinessError>> {
        try {
            const targetUser = await prisma.usuario.findUnique({
                where: { id: targetUserId },
            });

            if (!targetUser) {
                return err(new NotFoundError('Usuario'));
            }

            const existing = await prisma.usuarioRol.findUnique({
                where: {
                    usuario_id_rol_id: {
                        usuario_id: targetUserId,
                        rol_id: rolId,
                    },
                },
            });

            if (!existing) {
                return err(new NotFoundError('La asignación de rol no existe'));
            }

            await prisma.usuarioRol.delete({
                where: {
                    usuario_id_rol_id: {
                        usuario_id: targetUserId,
                        rol_id: rolId,
                    },
                },
            });

            return ok(undefined);
        } catch (error: any) {
            console.error('[RbacService.removeRolFromUser] Error:', error);
            if (error.code === 'P2025') {
                return err(new NotFoundError('Rol o usuario no encontrado'));
            }
            return err(new BusinessError('Error al remover rol del usuario', 'REMOVE_ERROR', 500));
        }
    }

    async getRoles(
        empresa_id: string,
        filters?: { activo?: boolean; includePermisos?: boolean }
    ): Promise<Result<any[], BusinessError>> {
        try {
            const where: any = {};

            if (filters?.activo !== undefined) {
                where.activo = filters.activo;
            }

            const include: any = {
                _count: {
                    select: { usuarios: true, permisos: true },
                },
            };

            if (filters?.includePermisos) {
                include.permisos = {
                    include: {
                        permiso: true,
                    },
                };
            }

            const roles = await prisma.rol.findMany({
                where,
                include,
                orderBy: { nombre: 'asc' },
            });

            return ok(roles);
        } catch (error) {
            console.error('[RbacService.getRoles] Error:', error);
            return err(new BusinessError('Error al obtener roles', 'QUERY_ERROR', 500));
        }
    }

    async getPermisos(
        empresa_id: string,
        filters?: { modulo?: string; activo?: boolean }
    ): Promise<Result<any[], BusinessError>> {
        try {
            const where: any = {};

            if (filters?.modulo) {
                where.modulo = filters.modulo;
            }
            if (filters?.activo !== undefined) {
                where.activo = filters.activo;
            }

            const permisos = await prisma.permiso.findMany({
                where,
                orderBy: [{ modulo: 'asc' }, { codigo: 'asc' }],
            });

            return ok(permisos);
        } catch (error) {
            console.error('[RbacService.getPermisos] Error:', error);
            return err(new BusinessError('Error al obtener permisos', 'QUERY_ERROR', 500));
        }
    }

    async getRolById(
        empresa_id: string,
        rolId: string
    ): Promise<Result<any, BusinessError>> {
        try {
            const rol = await prisma.rol.findUnique({
                where: { id: rolId },
                include: {
                    permisos: {
                        include: {
                            permiso: true,
                        },
                    },
                    _count: {
                        select: { usuarios: true },
                    },
                },
            });

            if (!rol) {
                return err(new NotFoundError('Rol'));
            }

            return ok(rol);
        } catch (error) {
            console.error('[RbacService.getRolById] Error:', error);
            return err(new BusinessError('Error al obtener el rol', 'QUERY_ERROR', 500));
        }
    }

    async updateRol(
        empresa_id: string,
        userId: string,
        rolId: string,
        input: UpdateRolInput
    ): Promise<Result<any, BusinessError>> {
        try {
            const rol = await prisma.rol.findUnique({
                where: { id: rolId },
            });

            if (!rol) {
                return err(new NotFoundError('Rol'));
            }

            if (rol.es_sistema && input.nombre && input.nombre !== rol.nombre) {
                return err(new BusinessError(
                    'No se puede modificar el nombre de un rol del sistema',
                    'SYSTEM_ROLE',
                    400
                ));
            }

            if (input.nombre && input.nombre !== rol.nombre) {
                const existing = await prisma.rol.findUnique({
                    where: { nombre: input.nombre },
                });
                if (existing) {
                    return err(new ConflictError(`Ya existe un rol con el nombre ${input.nombre}`));
                }
            }

            const updated = await prisma.rol.update({
                where: { id: rolId },
                data: {
                    ...input,
                    actualizado_en: new Date(),
                },
            });

            return ok(updated);
        } catch (error: any) {
            console.error('[RbacService.updateRol] Error:', error);
            if (error.code === 'P2002') {
                return err(new ConflictError('Ya existe un rol con este nombre'));
            }
            if (error.code === 'P2025') {
                return err(new NotFoundError('Rol'));
            }
            return err(new BusinessError('Error al actualizar el rol', 'UPDATE_ERROR', 500));
        }
    }
}

export const rbacService = new RbacService();
