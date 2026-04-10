import { NextRequest, NextResponse } from 'next/server';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { prisma } from '@/lib/prisma';

/**
 * @swagger
 * /api/v1/vehiculos/{id}/desactivar:
 *   patch:
 *     summary: Desactivar Vehículo
 *     description: >
 *       Deactivates a vehicle by setting fecha_baja to today and activo to false.
 *       BEFORE deactivating, validates that the vehicle has no INSTALADO tires.
 *       If mounted tires exist, returns 409 Conflict with the list of mounted tires.
 *     tags:
 *       - Vehículos
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *           format: uuid
 *         description: ID del vehículo a desactivar
 *     responses:
 *       200:
 *         description: Vehículo desactivado exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                 data:
 *                   type: object
 *                   properties:
 *                     id:
 *                       type: string
 *                     placa:
 *                       type: string
 *                     numero_economico:
 *                       type: string
 *                     fecha_baja:
 *                       type: string
 *                       format: date
 *                     activo:
 *                       type: boolean
 *                 message:
 *                   type: string
 *       404:
 *         description: Vehículo no encontrado
 *       409:
 *         description: Conflicto - El vehículo tiene neumáticos instalados
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 error:
 *                   type: string
 *                 neumáticos_instalados:
 *                   type: array
 *                   items:
 *                     type: object
 *                     properties:
 *                       neumatico_id:
 *                         type: string
 *                       numero_serie:
 *                         type: string
 *                       modelo:
 *                         type: string
 *                       posicion:
 *                         type: string
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Permisos insuficientes
 *       500:
 *         description: Error interno del servidor
 */
export async function PATCH(
    request: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.VEHICULOS_UPDATE);

        const empresaId = session.user.empresa_id;
        if (!empresaId) {
            return NextResponse.json(
                { error: 'Usuario no tiene empresa asignada' },
                { status: 403 }
            );
        }

        const { id } = await params;

        // 1. Verify vehicle exists and belongs to this company
        const vehiculo = await prisma.vehiculo.findUnique({
            where: {
                id,
                empresa_id: empresaId,
            },
        });

        if (!vehiculo) {
            return NextResponse.json(
                { error: 'Vehículo no encontrado' },
                { status: 404 }
            );
        }

        // 2. Check if already deactivated
        if (!vehiculo.activo) {
            return NextResponse.json(
                {
                    success: true,
                    data: {
                        id: vehiculo.id,
                        placa: vehiculo.placa,
                        numero_economico: vehiculo.numero_economico,
                        fecha_baja: vehiculo.fecha_baja,
                        activo: vehiculo.activo,
                    },
                    message: 'El vehículo ya está desactivado',
                },
                { status: 200 }
            );
        }

        // 3. Check for mounted tires (estado_actual = 'INSTALADO')
        const neumáticosInstalados = await prisma.neumatico.findMany({
            where: {
                ubicacion_vehiculo_id: id,
                estado_actual: 'INSTALADO',
                activo: true,
            },
            include: {
                modelo: {
                    select: {
                        nombre_modelo: true,
                        medida: true,
                    },
                },
                ubicacion_posicion: {
                    select: {
                        codigo_posicion: true,
                        etiqueta_posicion: true,
                    },
                },
            },
        });

        if (neumáticosInstalados.length > 0) {
            return NextResponse.json(
                {
                    error: 'No se puede desactivar el vehículo porque tiene neumáticos instalados',
                    neumáticos_instalados: neumáticosInstalados.map((n) => ({
                        neumatico_id: n.id,
                        numero_serie: n.numero_serie,
                        modelo: n.modelo ? `${n.modelo.nombre_modelo} ${n.modelo.medida}` : null,
                        posicion: n.ubicacion_posicion
                            ? n.ubicacion_posicion.etiqueta_posicion || n.ubicacion_posicion.codigo_posicion
                            : null,
                    })),
                },
                { status: 409 }
            );
        }

        // 4. Deactivate the vehicle
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const vehiculoActualizado = await prisma.vehiculo.update({
            where: { id },
            data: {
                fecha_baja: today,
                activo: false,
            },
            select: {
                id: true,
                placa: true,
                numero_economico: true,
                fecha_baja: true,
                activo: true,
            },
        });

        return NextResponse.json({
            success: true,
            data: vehiculoActualizado,
            message: 'Vehículo desactivado exitosamente',
        });
    } catch (error: any) {
        if (error.message === 'UNAUTHORIZED') {
            return NextResponse.json({ error: 'No autenticado' }, { status: 401 });
        }
        if (error.message === 'FORBIDDEN') {
            return NextResponse.json({ error: 'Permisos insuficientes' }, { status: 403 });
        }
        console.error('[VEHICULO-DESACTIVAR] Error:', error);
        return NextResponse.json(
            { error: 'Error interno del servidor' },
            { status: 500 }
        );
    }
}
