import { NextRequest, NextResponse } from 'next/server';
import React from 'react';
import ReactPDF from '@react-pdf/renderer';
import { CertificadoOperatividadDocument } from '@/components/reports/CertificadoDocument';
import { prisma } from '@/lib/prisma';
import { toNumber } from '@/lib/utils/decimal';
import { requireAuth } from '@/lib/auth/authorization';

export async function GET(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
    try {
        const session = await requireAuth();
        const inspectorName = session.user.name || 'Usuario Sistema';
        const { id } = await params;

        // 1. Obtener datos del vehículo + última inspección
        const vehiculo = await prisma.vehiculo.findUnique({
            where: { id },
            include: {
                tipo_vehiculo: true,
                neumaticos_instalados: {
                    include: {
                        modelo: { include: { fabricante: true } },
                        lecturas_presion: {
                            orderBy: { fecha_lectura: 'desc' },
                            take: 1
                        },
                        ubicacion_posicion: true
                    }
                },
                registros_contador: {
                    orderBy: { fecha_registro: 'desc' },
                    take: 1
                }
            }
        });

        if (!vehiculo) {
            return new NextResponse('Vehículo no encontrado', { status: 404 });
        }

        // 2. Preparar DTO para el reporte
        const vehiculoData = {
            placa: vehiculo.placa || 'SIN PLACA',
            tipo: vehiculo.tipo_vehiculo?.nombre || 'N/A',
            marca: vehiculo.marca || 'N/A',
            modelo: vehiculo.modelo_vehiculo || 'N/A',
            kilometraje: toNumber(vehiculo.registros_contador[0]?.valor || vehiculo.odometro_actual)
        };

        const inspeccionData = {
            fecha: new Date().toLocaleDateString(),
            inspector: inspectorName,
            resultado: 'APTO' // Simplificado
        };

        const neumaticosData = vehiculo.neumaticos_instalados.map(n => {
            const presion = toNumber(n.lecturas_presion[0]?.presion_psi || n.presion_actual_psi);
            return {
                posicion: n.ubicacion_posicion?.posicion_relativa?.toString() || '?',
                marca: n.modelo.fabricante.nombre,
                modelo: n.modelo.nombre_modelo,
                presion: presion,
                profundidad: toNumber(n.profundidad_remanente_actual_mm),
                estado: presion < 80 ? 'CRITICO' : 'OK'
            };
        });

        // 3. Generar Stream PDF
        const stream = await ReactPDF.renderToStream(
            <CertificadoOperatividadDocument
                vehiculo={vehiculoData}
                inspeccion={inspeccionData}
                neumaticos={neumaticosData}
            />
        );

        // 4. Retornar respuesta
        return new NextResponse(stream as any, {
            headers: {
                'Content-Type': 'application/pdf',
                'Content-Disposition': `attachment; filename="certificado-${vehiculo.placa}.pdf"`
            }
        });

    } catch (error: any) {
        console.error('Error generating PDF:', error);
        return new NextResponse(JSON.stringify({ error: error.message }), { status: 500 });
    }
}
