import { NextRequest, NextResponse } from 'next/server';
import React from 'react';
import ReactPDF from '@react-pdf/renderer';
import { CertificadoOperatividadDocument } from '@/components/reports/CertificadoDocument';
import { requireAuth } from '@/lib/auth/authorization';
import { obtenerCertificadoPorFolio } from '@/lib/services/certificado.service';

/**
 * GET /api/v1/reportes/certificado/folio/[folio]
 *
 * Re-descarga el PDF de un certificado previamente emitido a partir de su folio secuencial.
 * Utiliza el snapshot_data inmutable guardado en la BD sin generar un nuevo número de folio.
 */
export async function GET(
    _request: NextRequest,
    { params }: { params: Promise<{ folio: string }> }
) {
    try {
        const session = await requireAuth();

        if (!session.user.empresa_id) {
            return new NextResponse('Usuario sin empresa asignada', {
                status: 403,
            });
        }

        const { folio } = await params;
        const folioNumero = parseInt(folio, 10);

        if (isNaN(folioNumero) || folioNumero <= 0) {
            return new NextResponse('Número de folio inválido', { status: 400 });
        }

        // Obtener certificado desde el snapshot inmutable (protección IDOR por empresa_id)
        const certificado = await obtenerCertificadoPorFolio({
            empresaId: session.user.empresa_id,
            folioNumero,
        });

        // Preparar datos para el componente PDF
        const neumaticosData = certificado.evaluacion.neumaticos.map((n) => ({
            posicion: n.posicion,
            marca: n.marca,
            modelo: n.modelo,
            presion_psi: n.presion_psi,
            profundidad_mm: n.profundidad_mm,
            estado: n.estado as 'APTO' | 'CONDICIONAL' | 'NO_APTO',
        }));

        const fechaEmisionFormateada = certificado.fecha_emision.toLocaleString(
            'es-PE',
            {
                dateStyle: 'short',
                timeStyle: 'short',
            }
        );

        const fechaInspeccionFormateada = certificado.inspeccion.fecha
            ? new Date(certificado.inspeccion.fecha).toLocaleDateString('es-PE')
            : null;

        // Generar stream PDF desde snapshot
        const stream = await ReactPDF.renderToStream(
            <CertificadoOperatividadDocument
                folio={certificado.folio_numero}
                fechaEmision={fechaEmisionFormateada}
                vehiculo={certificado.vehiculo}
                inspeccion={{
                    fecha: fechaInspeccionFormateada,
                    inspector: certificado.inspeccion.inspector,
                }}
                resultado={{
                    estado: certificado.estado_operatividad as
                        | 'APTO'
                        | 'CONDICIONAL'
                        | 'NO_APTO',
                    razones: certificado.evaluacion.razones,
                }}
                neumaticos={neumaticosData}
            />
        );

        const filename = `certificado-${certificado.vehiculo.placa}-${certificado.folio_numero
            .toString()
            .padStart(6, '0')}.pdf`;

        return new NextResponse(stream as unknown as ReadableStream, {
            headers: {
                'Content-Type': 'application/pdf',
                'Content-Disposition': `attachment; filename="${filename}"`,
            },
        });
    } catch (error) {
        const message =
            error instanceof Error ? error.message : 'Error desconocido';
        console.error('Error re-generating certificate PDF from snapshot:', error);

        if (message.includes('no encontrado') || message.includes('no pertenece')) {
            return new NextResponse(message, { status: 404 });
        }

        return new NextResponse(
            JSON.stringify({ error: message }),
            {
                status: 500,
                headers: { 'Content-Type': 'application/json' },
            }
        );
    }
}
