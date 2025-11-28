import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { createUsuarioSchema } from '@/lib/validators/usuarios';
import { hash } from 'bcryptjs';

/**
 * @swagger
 * /api/v1/usuarios:
 *   get:
 *     summary: Listar usuarios
 *     description: Obtiene una lista paginada de usuarios activos.
 *     tags: [Usuarios]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: page
 *         schema:
 *           type: integer
 *           default: 1
 *         description: Número de página
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           default: 10
 *         description: Cantidad de registros por página
 *       - in: query
 *         name: search
 *         schema:
 *           type: string
 *         description: Término de búsqueda (username, nombre, email)
 *     responses:
 *       200:
 *         description: Lista de usuarios recuperada exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 data:
 *                   type: array
 *                   items:
 *                     $ref: '#/components/schemas/Usuario'
 *                 meta:
 *                   type: object
 *                   properties:
 *                     total:
 *                       type: integer
 *                     page:
 *                       type: integer
 *                     limit:
 *                       type: integer
 *                     totalPages:
 *                       type: integer
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Permisos insuficientes (Requiere USUARIOS_READ)
 *   post:
 *     summary: Crear usuario
 *     description: Crea un nuevo usuario en el sistema.
 *     tags: [Usuarios]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/CreateUsuarioDTO'
 *     responses:
 *       201:
 *         description: Usuario creado exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 data:
 *                   $ref: '#/components/schemas/Usuario'
 *       400:
 *         description: Datos inválidos
 *       409:
 *         description: Usuario o email ya existe
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Permisos insuficientes (Requiere USUARIOS_CREATE)
 */
export async function GET(req: NextRequest) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.USUARIOS_READ);

        const { searchParams } = new URL(req.url);
        const page = parseInt(searchParams.get('page') || '1');
        const limit = parseInt(searchParams.get('limit') || '10');
        const search = searchParams.get('search') || '';
        const skip = (page - 1) * limit;

        const where = {
            activo: true,
            OR: search ? [
                { username: { contains: search, mode: 'insensitive' as const } },
                { nombre_completo: { contains: search, mode: 'insensitive' as const } },
                { email: { contains: search, mode: 'insensitive' as const } },
            ] : undefined,
        };

        const [usuarios, total] = await Promise.all([
            prisma.usuario.findMany({
                where,
                skip,
                take: limit,
                include: {
                    roles: {
                        include: {
                            rol: true,
                        },
                    },
                },
                orderBy: { creado_en: 'desc' },
            }),
            prisma.usuario.count({ where }),
        ]);

        // Remove password_hash from response
        const sanitizedUsuarios = usuarios.map(({ password_hash, ...user }) => user);

        return ApiResponseHelper.paginated(sanitizedUsuarios, {
            total,
            page,
            limit,
            totalPages: Math.ceil(total / limit),
            hasNext: page < Math.ceil(total / limit),
            hasPrev: page > 1,
        });
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}

export async function POST(req: NextRequest) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.USUARIOS_CREATE);

        const body = await req.json();
        const validation = createUsuarioSchema.safeParse(body);

        if (!validation.success) {
            return ApiResponseHelper.validationError(validation.error);
        }

        const { roles, password, ...userData } = validation.data;

        // Check if username or email exists
        const existingUser = await prisma.usuario.findFirst({
            where: {
                OR: [
                    { username: userData.username },
                    { email: userData.email },
                ],
            },
        });

        if (existingUser) {
            return NextResponse.json(
                { error: 'El nombre de usuario o email ya existe' },
                { status: 409 }
            );
        }

        const passwordHash = await hash(password, 10);

        const newUser = await prisma.usuario.create({
            data: {
                ...userData,
                password_hash: passwordHash,
                creado_por: session.user.id,
                roles: {
                    create: roles.map((rolId) => ({
                        rol_id: rolId,
                        asignado_por: session.user.id,
                    })),
                },
            },
            include: {
                roles: {
                    include: {
                        rol: true,
                    },
                },
            },
        });

        const { password_hash, ...sanitizedUser } = newUser;

        return ApiResponseHelper.created(sanitizedUser);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
