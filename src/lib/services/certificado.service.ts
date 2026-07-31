import { prisma } from '@/lib/prisma';
import { Prisma, EstadoOperatividadEnum } from '@prisma/client';

/**
 * Umbrales de evaluación de operatividad de neumáticos.
 *
 * Valores basados en prácticas de la industria para flotas de carga pesada.
 * IMPORTANTE: revisar con el área de operaciones/seguridad del cliente antes
 * de emitir certificaciones oficiales. Estos defaults son conservadores pero
 * no sustituyen la política formal de la empresa.
 *
 * TODO: mover a ParametroSistema para permitir configuración por empresa.
 */
export const OPERATIVIDAD_THRESHOLDS = {
    profundidad: {
        critica_mm: 3.0,
        condicional_mm: 4.0,
    },
    presion: {
        desviacion_critica_pct: 20,
        desviacion_condicional_pct: 10,
    },
} as const;

export interface OperatividadThresholds {
    profundidad: {
        critica_mm: number;
        condicional_mm: number;
    };
    presion: {
        desviacion_critica_pct: number;
        desviacion_condicional_pct: number;
    };
}

/**
 * Obtiene los umbrales de operatividad dinámicos desde ParametroSistema o usa los defaults.
 */
export async function obtenerUmbralesOperatividad(
    _empresaId?: string
): Promise<OperatividadThresholds> {
    try {
        const parametros = await prisma.parametroSistema.findMany({
            where: {
                clave: {
                    in: [
                        'OPERATIVIDAD_PROFUNDIDAD_CRITICA_MM',
                        'OPERATIVIDAD_PROFUNDIDAD_CONDICIONAL_MM',
                        'OPERATIVIDAD_PRESION_DESVIACION_CRITICA_PCT',
                        'OPERATIVIDAD_PRESION_DESVIACION_CONDICIONAL_PCT',
                    ],
                },
            },
        });

        const paramMap = new Map(parametros.map((p) => [p.clave, parseFloat(p.valor)]));

        return {
            profundidad: {
                critica_mm:
                    paramMap.get('OPERATIVIDAD_PROFUNDIDAD_CRITICA_MM') ??
                    OPERATIVIDAD_THRESHOLDS.profundidad.critica_mm,
                condicional_mm:
                    paramMap.get('OPERATIVIDAD_PROFUNDIDAD_CONDICIONAL_MM') ??
                    OPERATIVIDAD_THRESHOLDS.profundidad.condicional_mm,
            },
            presion: {
                desviacion_critica_pct:
                    paramMap.get('OPERATIVIDAD_PRESION_DESVIACION_CRITICA_PCT') ??
                    OPERATIVIDAD_THRESHOLDS.presion.desviacion_critica_pct,
                desviacion_condicional_pct:
                    paramMap.get('OPERATIVIDAD_PRESION_DESVIACION_CONDICIONAL_PCT') ??
                    OPERATIVIDAD_THRESHOLDS.presion.desviacion_condicional_pct,
            },
        };
    } catch {
        return OPERATIVIDAD_THRESHOLDS;
    }
}

export interface NeumaticoEvaluado {
    neumatico_id: string;
    numero_serie: string | null;
    posicion: string;
    marca: string;
    modelo: string;
    profundidad_mm: number;
    presion_psi: number;
    presion_recomendada_psi: number | null;
    estado: EstadoOperatividadEnum;
    razones: string[];
}

export interface EvaluacionVehiculo {
    estado: EstadoOperatividadEnum;
    razones: string[];
    neumaticos: NeumaticoEvaluado[];
}

/**
 * Tipo derivado de la query de Prisma que hace emitirCertificadoOperatividad().
 * Usar Prisma.NeumaticoGetPayload garantiza que el tipo siempre esté alineado
 * con el schema real. Si el schema cambia, TypeScript detecta el breakage.
 */
type NeumaticoParaEvaluacion = Prisma.NeumaticoGetPayload<{
    include: {
        modelo: {
            include: { fabricante: true };
        };
        ubicacion_posicion: true;
    };
}>;

/**
 * Evalúa el estado de operatividad de cada neumático del vehículo y computa
 * el estado global. Retorna razones específicas para cada decisión crítica.
 *
 * Reglas globales:
 * - NO_APTO: al menos un neumático en estado crítico (profundidad o presión)
 * - CONDICIONAL: al menos un neumático condicional, ninguno crítico
 * - APTO: todos los neumáticos en rangos aceptables
 */
export function evaluarOperatividadVehiculo(
    neumaticos: NeumaticoParaEvaluacion[],
    customThresholds?: OperatividadThresholds
): EvaluacionVehiculo {
    const thresholds = customThresholds ?? OPERATIVIDAD_THRESHOLDS;
    if (neumaticos.length === 0) {
        return {
            estado: EstadoOperatividadEnum.NO_APTO,
            razones: ['Vehículo no tiene neumáticos instalados'],
            neumaticos: [],
        };
    }

    const neumaticosEvaluados: NeumaticoEvaluado[] = neumaticos.map((n) => {
        const profundidad = Number(n.profundidad_remanente_actual_mm);
        const presion = n.presion_actual_psi ? Number(n.presion_actual_psi) : 0;
        const presionRecomendada = n.modelo.presion_recomendada_psi
            ? Number(n.modelo.presion_recomendada_psi)
            : null;

        const razones: string[] = [];
        let estado: EstadoOperatividadEnum = EstadoOperatividadEnum.APTO;

        // Evaluación de profundidad de dibujo
        if (profundidad < thresholds.profundidad.critica_mm) {
            estado = EstadoOperatividadEnum.NO_APTO;
            razones.push(
                `Profundidad crítica: ${profundidad}mm (mínimo operativo ${thresholds.profundidad.critica_mm}mm)`
            );
        } else if (profundidad < thresholds.profundidad.condicional_mm) {
            estado = EstadoOperatividadEnum.CONDICIONAL;
            razones.push(`Profundidad en rango condicional: ${profundidad}mm`);
        }

        // Evaluación de presión (solo si hay lectura y presión recomendada)
        if (presionRecomendada && presion > 0) {
            const desviacionPct = Math.abs(
                ((presion - presionRecomendada) / presionRecomendada) * 100
            );
            if (desviacionPct > thresholds.presion.desviacion_critica_pct) {
                estado = EstadoOperatividadEnum.NO_APTO;
                razones.push(
                    `Presión crítica: ${presion}psi vs recomendada ${presionRecomendada}psi (${desviacionPct.toFixed(1)}% desviación)`
                );
            } else if (desviacionPct > thresholds.presion.desviacion_condicional_pct) {
                if (estado === EstadoOperatividadEnum.APTO) {
                    estado = EstadoOperatividadEnum.CONDICIONAL;
                }
                razones.push(
                    `Presión fuera de rango: ${presion}psi vs recomendada ${presionRecomendada}psi`
                );
            }
        } else if (presionRecomendada && presion === 0) {
            if (estado === EstadoOperatividadEnum.APTO) {
                estado = EstadoOperatividadEnum.CONDICIONAL;
            }
            razones.push('Sin lectura de presión disponible');
        }

        return {
            neumatico_id: n.id,
            numero_serie: n.numero_serie,
            posicion: n.ubicacion_posicion?.codigo_posicion ?? 'SIN POSICIÓN',
            marca: n.modelo.fabricante.nombre,
            modelo: n.modelo.nombre_modelo,
            profundidad_mm: profundidad,
            presion_psi: presion,
            presion_recomendada_psi: presionRecomendada,
            estado,
            razones,
        };
    });

    // Estado global = peor estado entre los neumáticos
    const hayNoApto = neumaticosEvaluados.some(
        (n) => n.estado === EstadoOperatividadEnum.NO_APTO
    );
    const hayCondicional = neumaticosEvaluados.some(
        (n) => n.estado === EstadoOperatividadEnum.CONDICIONAL
    );

    let estadoGlobal: EstadoOperatividadEnum = EstadoOperatividadEnum.APTO;
    const razonesGlobales: string[] = [];

    if (hayNoApto) {
        estadoGlobal = EstadoOperatividadEnum.NO_APTO;
        const noAptos = neumaticosEvaluados.filter(
            (n) => n.estado === EstadoOperatividadEnum.NO_APTO
        );
        razonesGlobales.push(
            `${noAptos.length} neumático(s) en estado crítico`
        );
    } else if (hayCondicional) {
        estadoGlobal = EstadoOperatividadEnum.CONDICIONAL;
        const condicionales = neumaticosEvaluados.filter(
            (n) => n.estado === EstadoOperatividadEnum.CONDICIONAL
        );
        razonesGlobales.push(
            `${condicionales.length} neumático(s) en estado condicional`
        );
    } else {
        razonesGlobales.push('Todos los neumáticos en rangos operativos');
    }

    return {
        estado: estadoGlobal,
        razones: razonesGlobales,
        neumaticos: neumaticosEvaluados,
    };
}

export interface CertificadoEmitidoResult {
    id: string;
    folio_numero: number;
    fecha_emision: Date;
    estado_operatividad: EstadoOperatividadEnum;
    vehiculo: {
        placa: string;
        tipo: string;
        marca: string;
        modelo: string;
        kilometraje: number;
    };
    inspeccion: {
        fecha: Date | null;
        inspector: string;
    };
    evaluacion: EvaluacionVehiculo;
}

/**
 * Emite un certificado de operatividad para un vehículo.
 *
 * Características clave:
 * - Folio secuencial ÚNICO por empresa (generado atómicamente vía transacción + unique constraint)
 * - Snapshot inmutable del estado del vehículo al momento de emisión (audit trail)
 * - Evaluación real de operatividad (no hardcoded)
 * - Filtro por empresa_id (protección IDOR para fase multi-tenant)
 * - Reintentos defensivos en colisiones de folio concurrentes
 *
 * @throws Error si el vehículo no existe o no pertenece a la empresa del usuario
 */
export async function emitirCertificadoOperatividad(params: {
    vehiculoId: string;
    emitidoPor: string;
    empresaId: string;
    maxRetries?: number;
}): Promise<CertificadoEmitidoResult> {
    const { vehiculoId, emitidoPor, empresaId, maxRetries = 3 } = params;

    // 1. Obtener datos del vehículo filtrando por empresa (protección IDOR)
    const vehiculo = await prisma.vehiculo.findFirst({
        where: {
            id: vehiculoId,
            empresa_id: empresaId,
        },
        include: {
            tipo_vehiculo: true,
            registros_contador: {
                orderBy: { fecha_registro: 'desc' },
                take: 1,
            },
            neumaticos_instalados: {
                where: { activo: true },
                include: {
                    modelo: {
                        include: { fabricante: true },
                    },
                    ubicacion_posicion: true,
                },
            },
        },
    });

    if (!vehiculo) {
        throw new Error('Vehículo no encontrado o no pertenece a su empresa');
    }

    // 2. Obtener la inspección más reciente de cualquier neumático instalado
    let ultimaInspeccion: { fecha_inspeccion: Date; inspector: { nombre_completo: string } } | null = null;
    const neumaticoIds = vehiculo.neumaticos_instalados.map((n) => n.id);
    if (neumaticoIds.length > 0) {
        ultimaInspeccion = await prisma.inspeccion.findFirst({
            where: {
                empresa_id: empresaId,
                neumatico_id: { in: neumaticoIds },
            },
            orderBy: { fecha_inspeccion: 'desc' },
            include: {
                inspector: { select: { nombre_completo: true } },
            },
        });
    }

    // 3. Evaluar operatividad real con umbrales dinámicos (ParametroSistema / fallback)
    const thresholds = await obtenerUmbralesOperatividad(empresaId);
    const evaluacion = evaluarOperatividadVehiculo(vehiculo.neumaticos_instalados, thresholds);

    // 4. Crear certificado con folio secuencial atómico (con reintentos defensivos)
    const fechaEmision = new Date();
    let ultimoError: unknown = null;

    for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
            const certificado = await prisma.$transaction(async (tx) => {
                const ultimo = await tx.certificadoEmitido.findFirst({
                    where: { empresa_id: empresaId },
                    orderBy: { folio_numero: 'desc' },
                    select: { folio_numero: true },
                });

                const folioNumero = (ultimo?.folio_numero ?? 0) + 1;

                const kilometraje = Number(
                    vehiculo.registros_contador[0]?.valor ??
                    vehiculo.odometro_actual ??
                    0
                );

                const snapshot = {
                    vehiculo: {
                        placa: vehiculo.placa ?? 'SIN PLACA',
                        tipo: vehiculo.tipo_vehiculo?.nombre ?? 'N/A',
                        marca: vehiculo.marca ?? 'N/A',
                        modelo: vehiculo.modelo_vehiculo ?? 'N/A',
                        kilometraje,
                    },
                    evaluacion,
                    inspeccion: ultimaInspeccion
                        ? {
                            fecha: ultimaInspeccion.fecha_inspeccion.toISOString(),
                            inspector: ultimaInspeccion.inspector?.nombre_completo ?? 'N/A',
                        }
                        : null,
                };

                return tx.certificadoEmitido.create({
                    data: {
                        folio_numero: folioNumero,
                        vehiculo_id: vehiculoId,
                        emitido_por: emitidoPor,
                        empresa_id: empresaId,
                        estado_operatividad: evaluacion.estado,
                        razones: evaluacion.razones as unknown as Prisma.InputJsonValue,
                        snapshot_data: snapshot as unknown as Prisma.InputJsonValue,
                        fecha_emision: fechaEmision,
                    },
                });
            });

            return {
                id: certificado.id,
                folio_numero: certificado.folio_numero,
                fecha_emision: certificado.fecha_emision,
                estado_operatividad: certificado.estado_operatividad,
                vehiculo: {
                    placa: vehiculo.placa ?? 'SIN PLACA',
                    tipo: vehiculo.tipo_vehiculo?.nombre ?? 'N/A',
                    marca: vehiculo.marca ?? 'N/A',
                    modelo: vehiculo.modelo_vehiculo ?? 'N/A',
                    kilometraje: Number(
                        vehiculo.registros_contador[0]?.valor ??
                        vehiculo.odometro_actual ??
                        0
                    ),
                },
                inspeccion: {
                    fecha: ultimaInspeccion?.fecha_inspeccion ?? null,
                    inspector: ultimaInspeccion?.inspector?.nombre_completo ?? 'Sin inspección previa',
                },
                evaluacion,
            };
        } catch (err) {
            ultimoError = err;
            // P2002 = unique constraint violation (colisión de folio en concurrencia)
            if (err instanceof Prisma.PrismaClientKnownRequestError && err.code === 'P2002') {
                if (attempt < maxRetries - 1) {
                    await new Promise((resolve) => setTimeout(resolve, 50 * (attempt + 1)));
                    continue;
                }
            }
            throw err;
        }
    }

    throw new Error(
        `No se pudo emitir el certificado tras ${maxRetries} intentos: ${String(ultimoError)}`
    );
}

/**
 * Obtiene un certificado previamente emitido a partir de su folio secuencial y empresa.
 * Reconstruye la estructura CertificadoEmitidoResult desde el snapshot_data inmutable.
 *
 * @throws Error si el certificado no existe o no pertenece a la empresa
 */
export async function obtenerCertificadoPorFolio(params: {
    empresaId: string;
    folioNumero: number;
}): Promise<CertificadoEmitidoResult> {
    const { empresaId, folioNumero } = params;

    const certificado = await prisma.certificadoEmitido.findFirst({
        where: {
            empresa_id: empresaId,
            folio_numero: folioNumero,
        },
    });

    if (!certificado) {
        throw new Error('Certificado no encontrado o no pertenece a su empresa');
    }

    const snapshot = certificado.snapshot_data as any;

    return {
        id: certificado.id,
        folio_numero: certificado.folio_numero,
        fecha_emision: certificado.fecha_emision,
        estado_operatividad: certificado.estado_operatividad,
        vehiculo: snapshot.vehiculo ?? {
            placa: 'N/A',
            tipo: 'N/A',
            marca: 'N/A',
            modelo: 'N/A',
            kilometraje: 0,
        },
        inspeccion: {
            fecha: snapshot.inspeccion?.fecha ? new Date(snapshot.inspeccion.fecha) : null,
            inspector: snapshot.inspeccion?.inspector ?? 'N/A',
        },
        evaluacion: snapshot.evaluacion ?? {
            estado: certificado.estado_operatividad,
            razones: (certificado.razones as string[]) ?? [],
            neumaticos: [],
        },
    };
}

/**
 * Lista los certificados emitidos históricamente para un vehículo.
 */
export async function listarCertificadosVehiculo(params: {
    empresaId: string;
    vehiculoId: string;
}) {
    const { empresaId, vehiculoId } = params;

    return await prisma.certificadoEmitido.findMany({
        where: {
            empresa_id: empresaId,
            vehiculo_id: vehiculoId,
        },
        orderBy: { folio_numero: 'desc' },
        select: {
            id: true,
            folio_numero: true,
            fecha_emision: true,
            estado_operatividad: true,
            emitido_por: true,
        },
    });
}

export interface ListarCertificadosFlotaFilters {
    page?: number;
    limit?: number;
    search?: string;
    estado?: EstadoOperatividadEnum;
    fechaDesde?: Date;
    fechaHasta?: Date;
}

/**
 * Lista certificados de operatividad emitidos históricamente para toda la flota de la empresa,
 * soporta paginación, búsqueda por folio/placa y filtrado por estado y fecha.
 */
export async function listarCertificadosFlota(
    empresaId: string,
    filters: ListarCertificadosFlotaFilters = {}
) {
    const page = Math.max(1, filters.page ?? 1);
    const limit = Math.min(100, Math.max(1, filters.limit ?? 20));
    const skip = (page - 1) * limit;

    const where: Prisma.CertificadoEmitidoWhereInput = {
        empresa_id: empresaId,
        ...(filters.estado ? { estado_operatividad: filters.estado } : {}),
        ...(filters.fechaDesde || filters.fechaHasta
            ? {
                  fecha_emision: {
                      ...(filters.fechaDesde ? { gte: filters.fechaDesde } : {}),
                      ...(filters.fechaHasta ? { lte: filters.fechaHasta } : {}),
                  },
              }
            : {}),
    };

    if (filters.search && filters.search.trim() !== '') {
        const queryStr = filters.search.trim();
        const numericFolio = parseInt(queryStr, 10);
        where.OR = [
            ...(!isNaN(numericFolio) ? [{ folio_numero: numericFolio }] : []),
            {
                vehiculo: {
                    placa: { contains: queryStr, mode: 'insensitive' as const },
                },
            },
        ];
    }

    const [total, items] = await Promise.all([
        prisma.certificadoEmitido.count({ where }),
        prisma.certificadoEmitido.findMany({
            where,
            orderBy: { folio_numero: 'desc' },
            skip,
            take: limit,
            include: {
                vehiculo: {
                    select: {
                        id: true,
                        placa: true,
                        numero_economico: true,
                        marca: true,
                        modelo_vehiculo: true,
                    },
                },
                emisor: {
                    select: {
                        id: true,
                        nombre_completo: true,
                        email: true,
                    },
                },
            },
        }),
    ]);

    return {
        data: items,
        pagination: {
            total,
            page,
            limit,
            totalPages: Math.ceil(total / limit),
        },
    };
}

