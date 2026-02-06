import { prisma } from '@/lib/prisma';
import { Usuario } from '@prisma/client';
import { hash } from 'bcryptjs';
import { BusinessError } from '@/lib/errors/business.error';

export class UsuarioService {

    async getAll(empresaId: string, filters?: { activo?: boolean, busqueda?: string }) {
        const where: any = { empresa_id: empresaId };

        if (filters?.activo !== undefined) {
            where.activo = filters.activo;
        }

        if (filters?.busqueda) {
            where.OR = [
                { nombre_completo: { contains: filters.busqueda, mode: 'insensitive' } },
                { username: { contains: filters.busqueda, mode: 'insensitive' } },
                { email: { contains: filters.busqueda, mode: 'insensitive' } }
            ];
        }

        const usuarios = await prisma.usuario.findMany({
            where,
            orderBy: { nombre_completo: 'asc' }
        });

        // Retornar sin hash
        return usuarios.map(u => this._sanitize(u));
    }

    async getPaginated(empresaId: string, params: { page: number, limit: number, search?: string }) {
        const skip = (params.page - 1) * params.limit;
        const where: any = { empresa_id: empresaId };

        if (params.search) {
            where.OR = [
                { username: { contains: params.search, mode: 'insensitive' } },
                { nombre_completo: { contains: params.search, mode: 'insensitive' } },
                { email: { contains: params.search, mode: 'insensitive' } },
            ];
        }

        const [usuarios, total] = await Promise.all([
            prisma.usuario.findMany({
                where,
                skip,
                take: params.limit,
                orderBy: { creado_en: 'desc' },
            }),
            prisma.usuario.count({ where }),
        ]);

        return {
            data: usuarios.map(u => this._sanitize(u)),
            meta: {
                total,
                page: params.page,
                limit: params.limit,
                totalPages: Math.ceil(total / params.limit)
            }
        };
    }

    async getById(empresaId: string, id: string) {
        const usuario = await prisma.usuario.findUnique({ where: { id } });
        // Verificación de tenant
        if (!usuario || usuario.empresa_id !== empresaId) throw BusinessError.notFound('Usuario', id);
        return this._sanitize(usuario);
    }

    async create(empresaId: string, data: any) {
        // Verificar único dentro de la misma empresa o globalmente?
        // Email y Username suelen ser globally unique en muchos sistemas SaaS simples,
        // pero idealmente email es unico por sistema, username puede ser por tenant si es un subdomain app,
        // pero aquí parece una SPA unificada. Mantengamos unicidad global de email/username por simplicidad de login.

        const existing = await prisma.usuario.findFirst({
            where: {
                OR: [{ username: data.username }, { email: data.email }]
            }
        });

        if (existing) throw BusinessError.conflict('Usuario o email ya existe');

        const passwordHash = await hash(data.password, 10);

        const { password, ...userData } = data;

        const newUser = await prisma.usuario.create({
            data: {
                ...userData,
                empresa_id: empresaId,
                password_hash: passwordHash,
                activo: true
            }
        });

        return this._sanitize(newUser);
    }

    async update(empresaId: string, id: string, data: any) {
        const usuario = await prisma.usuario.findUnique({ where: { id } });
        if (!usuario || usuario.empresa_id !== empresaId) throw BusinessError.notFound('Usuario', id);

        const { password, ...updateData } = data;
        let passwordData = {};

        if (password) {
            passwordData = { password_hash: await hash(password, 10) };
        }

        // Prevent updating critical fields like empresa_id via spread
        // Zod validation should handle this, but for safety:
        delete (updateData as any).empresa_id;

        const updated = await prisma.usuario.update({
            where: { id },
            data: {
                ...updateData,
                ...passwordData
            }
        });

        return this._sanitize(updated);
    }

    async delete(empresaId: string, id: string) {
        const usuario = await prisma.usuario.findUnique({ where: { id } });
        if (!usuario || usuario.empresa_id !== empresaId) throw BusinessError.notFound('Usuario', id);

        // Soft Delete
        await prisma.usuario.update({
            where: { id },
            data: { activo: false }
        });

        return { message: 'Usuario desactivado exitosamente' };
    }

    // Helper para quitar campos sensibles
    private _sanitize(usuario: Usuario) {
        const { password_hash, ...rest } = usuario;
        return rest;
    }
}
