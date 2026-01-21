import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { AlertasService } from '@/lib/services/alertas.service';
import { z } from 'zod';

const alertasService = new AlertasService();

// Schema principal de validación para el payload
const lecturaTpmsSchema = z.object({
    sensor_id: z.string().min(1),
    psi: z.number().min(0),
    temp_c: z.number().optional(),
    battery_level: z.number().optional(), // 0-100
    timestamp: z.string().datetime().optional()
});

const batchTpmsSchema = z.array(lecturaTpmsSchema);

// Helper para respuesta rápida
const jsonResponse = (data: any, status = 200) => NextResponse.json(data, { status });

export async function POST(request: NextRequest) {
    try {
        // 1. Autenticación Simple (API Key)
        // Para IoT Gateways, usamos un header personalizado o query param. 
        // Header standard: X-API-Key
        const apiKey = request.headers.get('x-api-key');
        const validKey = process.env.TPMS_API_KEY;

        // Si no está configurada la key en servidor, bloquear por seguridad
        if (!validKey) {
            console.error('TPMS_API_KEY not configured on server');
            return jsonResponse({ error: 'Server misconfiguration' }, 500);
        }

        if (apiKey !== validKey) {
            return jsonResponse({ error: 'Unauthorized' }, 401);
        }

        // 2. Parseo y Validación
        const body = await request.json();
        const result = batchTpmsSchema.safeParse(body);

        if (!result.success) {
            return jsonResponse({ error: 'Invalid payload', details: result.error.issues }, 400);
        }

        const lecturas = result.data;
        if (lecturas.length === 0) {
            return jsonResponse({ message: 'No readings provided' });
        }

        const uniqueSensorIds = Array.from(new Set(lecturas.map(l => l.sensor_id)));

        // 3. Buscar Neumáticos asociados a estos sensores
        const neumaticos = await prisma.neumatico.findMany({
            where: {
                sensor_id: { in: uniqueSensorIds },
                activo: true
            },
            select: {
                id: true,
                sensor_id: true,
                modelo: {
                    select: {
                        presion_recomendada_psi: true
                    }
                }
            }
        });

        // Mapa eficiente: sensor_id -> Neumatico
        const neumaticoMap = new Map();
        neumaticos.forEach(n => {
            if (n.sensor_id) neumaticoMap.set(n.sensor_id, n);
        });

        // 4. Procesar lecturas
        let processedCount = 0;
        let alertsCount = 0;

        const now = new Date();

        for (const lectura of lecturas) {
            const neumatico = neumaticoMap.get(lectura.sensor_id);
            if (!neumatico) continue;

            const fechaLectura = lectura.timestamp ? new Date(lectura.timestamp) : now;

            try {
                // Transacción individual para asegurar contexto RLS
                await prisma.$transaction(async (tx) => {
                    // Establecer Contexto RLS (Crucial para políticas de seguridad)
                    try {
                        await tx.$executeRawUnsafe(`SELECT set_config('app.current_tenant', '${neumatico.empresa_id}', true)`);
                    } catch (ignore) { /* Ignorar si no soporta set_config */ }

                    // a. Insertar Lectura
                    await tx.lecturaPresion.create({
                        data: {
                            neumatico_id: neumatico.id,
                            presion_psi: lectura.psi,
                            temperatura_c: lectura.temp_c,
                            fecha_lectura: fechaLectura,
                            fuente: 'SENSOR_TPMS'
                        }
                    });

                    // b. Actualizar Snapshot
                    await tx.neumatico.update({
                        where: { id: neumatico.id },
                        data: {
                            presion_actual_psi: lectura.psi,
                            fecha_ultimo_evento: now
                        }
                    });

                    // c. Verificar Alerta (Baja Presión)
                    const umbral = (neumatico.modelo.presion_recomendada_psi || 100) * 0.8;
                    if (lectura.psi < umbral) {
                        const existe = await tx.alerta.findFirst({
                            where: { neumatico_id: neumatico.id, tipo: 'PRESION_BAJA', resuelta: false }
                        });

                        if (!existe) {
                            await tx.alerta.create({
                                data: {
                                    tipo: 'PRESION_BAJA',
                                    severidad: 'CRITICAL', // Enum value
                                    mensaje: `Presión CRÍTICA: ${lectura.psi} PSI (Mín: ${umbral})`,
                                    neumatico_id: neumatico.id,
                                    leida: false,
                                    resuelta: false
                                }
                            });
                            // Side-effect visible after await
                            alertsCount++;
                        }
                    }
                });
                processedCount++;
            } catch (err) {
                console.error(`Error processing sensor ${lectura.sensor_id}:`, err);
                // Continue with next reading
            }
        }

        return jsonResponse({
            success: true,
            processed: processedCount,
            alerts_triggered: alertsCount
        });

    } catch (error) {
        console.error('TPMS Integration Error:', error);
        return jsonResponse({ error: 'Internal Server Error' }, 500);
    }
}
