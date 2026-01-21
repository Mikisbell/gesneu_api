
import { NextRequest } from 'next/server';
import { prisma } from '@/lib/prisma';
import { requireAuth, isAdmin } from '@/lib/auth/authorization';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { AdminUserSearchSchema } from '@/lib/validators/admin.validator';

export const runtime = 'nodejs';

export async function GET(request: NextRequest) {
    try {
        const session = await requireAuth();

        if (!isAdmin(session)) {
            return ApiResponseHelper.forbidden('Solo administradores pueden ver usuarios');
        }

        // Parse query params
        const { searchParams } = new URL(request.url);
        const search = searchParams.get('search') || '';
        const empresaId = searchParams.get('empresa_id') || undefined;
        const rol = searchParams.get('rol') || undefined;
        const activo = searchParams.get('activo');
        const limit = parseInt(searchParams.get('limit') || '50');
        const offset = parseInt(searchParams.get('offset') || '0');

        // Build where clause
        const where: any = {};

        if (search) {
            where.OR = [
                { username: { contains: search, mode: 'insensitive' } },
                { email: { contains: search, mode: 'insensitive' } },
                { nombre_completo: { contains: search, mode: 'insensitive' } }
            ];
        }

        if (empresaId) where.empresa_id = empresaId;
        if (rol) where.rol = rol;
        if (activo !== null && activo !== undefined) {
            where.activo = activo === 'true';
        }

        // Fetch users with count
        const [users, total] = await Promise.all([
            prisma.usuario.findMany({
                where,
                take: limit,
                skip: offset,
                orderBy: { creado_en: 'desc' },
                select: {
                    id: true,
                    username: true,
                    email: true,
                    nombre_completo: true,
                    rol: true,
                    activo: true,
                    creado_en: true,
                    empresa: {
                        select: { id: true, nombre: true }
                    }
                }
            }),
            prisma.usuario.count({ where })
        ]);

        return ApiResponseHelper.success({
            users,
            pagination: {
                total,
                limit,
                offset,
                hasMore: offset + users.length < total
            }
        });
    } catch (error) {
        console.error('[Admin Users] Error:', error);
        return ApiResponseHelper.handleError(error);
    }
}
