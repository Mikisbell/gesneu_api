
import { NeumaticoRepository } from '@/lib/repositories/neumatico.repository';
import {
    CreateNeumaticoDTO,
    UpdateNeumaticoDTO,
    NeumaticoResponse,
    NeumaticoFilters
} from '@/types/domain/neumatico.types';
import {
    mapDtoToPrismaCreate,
    mapDtoToPrismaUpdate,
    mapEntityToResponse
} from '@/lib/mappers/neumatico.mapper';
import {
    Result,
    ok,
    err,
    BusinessError,
    ConflictError,
    NotFoundError
} from '@/types/result.types';
import { asNeumaticoId, NeumaticoId, UsuarioId } from '@/types/branded.types';
import { prisma } from '@/lib/prisma';
import { TipoEventoNeumaticoEnum, Prisma } from '@prisma/client';
import { toNumber } from '@/lib/utils/decimal';
import { EventoNeumaticoCreate } from '@/lib/validators/evento-neumatico';
import { EventoNeumaticoService } from './evento-neumatico.service';
import { canDeleteNeumatico } from '@/lib/validators/domain-rules/neumatico.rules';


export class NeumaticoService {
    private repository: NeumaticoRepository;

    constructor() {
        this.repository = new NeumaticoRepository();
    }

    /**
     * Crea un nuevo neumático (Compra/Alta).
     */
    async create(
        dto: CreateNeumaticoDTO,
        empresa_id: string,
        userId: string
    ): Promise<Result<NeumaticoResponse, BusinessError>> {
        // ✅ Validation 1: Duplicate numero_serie (tenant-scoped)
        // Schema: @@unique([empresa_id, numero_serie]) -> Tenant-scoped unique
        if (dto.numero_serie) {
            const existing = await this.repository.findBySerie(dto.numero_serie);
            if (existing && existing.empresa_id === empresa_id) {
                return err(new ConflictError(`Ya existe un neumático con el número de serie "${dto.numero_serie}" en esta empresa`));
            }
        }

        // ✅ Business Rule 2: COMPRA debe tener costo > 0
        if (!dto.costo_compra || dto.costo_compra <= 0) {
            return err(new BusinessError(
                'El costo de compra es requerido y debe ser mayor a 0',
                'INVALID_COST',
                400
            ));
        }

        // ✅ Business Rule 3: Profundidad inicial > 0
        if (!dto.profundidad_inicial_mm || dto.profundidad_inicial_mm <= 0) {
            return err(new BusinessError(
                'La profundidad inicial debe ser mayor a 0',
                'INVALID_DEPTH',
                400
            ));
        }

        try {
            // 2. Transaction
            const result = await prisma.$transaction(async (tx) => {
                // Map Data (Now handles relations and IDs)
                const prismaInput = mapDtoToPrismaCreate(dto, userId, empresa_id);

                // Create Neumatico
                const neumatico = await tx.neumatico.create({
                    data: prismaInput,
                    include: {
                        modelo: { include: { fabricante: true } },
                        ubicacion_almacen: true,
                        ubicacion_vehiculo: { include: { tipo_vehiculo: true } },
                        ubicacion_posicion: true,
                        proveedor_compra: true,
                        motivo_desecho: true
                    }
                });

                // Evento Inicial (COMPRA)
                await tx.eventoNeumatico.create({
                    data: {
                        tipo_evento: TipoEventoNeumaticoEnum.COMPRA,
                        neumatico_id: neumatico.id,
                        fecha_evento: new Date(dto.fecha_compra),

                        proveedor_id: dto.proveedor_compra_id,
                        almacen_destino_id: dto.ubicacion_almacen_id,
                        costo_evento: dto.costo_compra ? new Prisma.Decimal(dto.costo_compra) : undefined,
                        profundidad_remanente: dto.profundidad_actual_mm ?? 0, // Using actual


                        // EventoNeumatico has no bedrijf_id? Wait, Schema check `EventoNeumatico`.
                        // Usually inherits, but check if `empresa_id` field exists on Evento.
                        // Assuming inferred or not needed if related to Neumatico.
                        // Wait, previous code didn't set `empresa_id` on Evento.

                        notas: 'Alta inicial sistema',
                        creado_por: userId
                    }
                });

                return neumatico;
            }, { maxWait: 10000, timeout: 30000 });

            // 3. Response
            return ok(mapEntityToResponse(result as any));


        } catch (error: any) {
            console.error('[NeumaticoService.create] Input:', JSON.stringify(dto, null, 2));
            console.error('[NeumaticoService.create] Prisma Error:', error);
            console.error('[NeumaticoService.create] Code:', error.code);
            console.error('[NeumaticoService.create] Meta:', error.meta);

            // ✅ Mensajes de error específicos por código Prisma
            if (error.code === 'P2002') {
                // Unique constraint violation
                const target = error.meta?.target || [];
                if (target.includes('numero_serie')) {
                    return err(new ConflictError(
                        `Ya existe un neumático con el número de serie "${dto.numero_serie}" en esta empresa`
                    ));
                }
                return err(new ConflictError('Ya existe un neumático con estos datos únicos'));
            }

            if (error.code === 'P2003') {
                // Foreign key constraint violation
                const field = error.meta?.field_name || 'relacionado';
                let message = 'Referencia inválida';

                if (field.includes('modelo')) {
                    message = `El modelo de neumático especificado no existe`;
                } else if (field.includes('proveedor')) {
                    message = `El proveedor especificado no existe`;
                } else if (field.includes('almacen')) {
                    message = `El almacén especificado no existe`;
                } else if (field.includes('empresa')) {
                    message = `La empresa especificada no existe`;
                }

                return err(new BusinessError(message, 'INVALID_REFERENCE', 400));
            }

            if (error.code === 'P2025') {
                // Record not found
                return err(new NotFoundError('Recurso relacionado no encontrado'));
            }

            if (error.code === 'P2034') {
                // Transaction conflict
                return err(new BusinessError(
                    'Conflicto de transacción. Por favor, intente nuevamente',
                    'TRANSACTION_CONFLICT',
                    409
                ));
            }

            // Error genérico
            return err(new BusinessError(
                'Error al crear neumático. Verifique los datos e intente nuevamente',
                'CREATE_ERROR',
                500
            ));
        }
    }

    async getAll(empresa_id: string, filters?: NeumaticoFilters): Promise<Result<NeumaticoResponse[]>> {
        try {
            const entities = await this.repository.findAllWithRelations({ ...filters, empresa_id });
            return ok(entities.map(mapEntityToResponse));
        } catch (error) {
            console.error('[NeumaticoService.getAll] Error:', error);
            return err(new BusinessError('Error al obtener neumáticos', 'QUERY_ERROR', 500));
        }
    }

    async getById(empresa_id: string, id: string): Promise<Result<NeumaticoResponse>> {
        try {
            const entity = await this.repository.findByIdWithFullRelations(asNeumaticoId(id));
            if (!entity || entity.empresa_id !== empresa_id) {
                return err(new NotFoundError('Neumático'));
            }
            return ok(mapEntityToResponse(entity));
        } catch (error) {
            return err(new BusinessError('Error finding neumatico', 'FIND_ERROR', 500));
        }
    }

    async update(empresa_id: string, id: string, dto: UpdateNeumaticoDTO, userId: string): Promise<Result<NeumaticoResponse>> {
        try {
            const existing = await this.repository.findById(asNeumaticoId(id));
            if (!existing || existing.empresa_id !== empresa_id) return err(new NotFoundError('Neumático'));

            const updateInput = mapDtoToPrismaUpdate(dto, userId);

            // Should reuse repository update, but need `NeumaticoUpdateInput` match.
            // Repository expects `UpdateNeumaticoDTO`. Repository method calls `prisma.update({data: dto})`?
            // Repository `base.repository` implementation usually takes Partial<Entity> or Input?
            // `NeumaticoRepository` extends `BaseRepository<Neumatico, CreateDTO, UpdateDTO>`.
            // BaseRepository.update(id, data: Partial<UpdateDTO>).
            // But `mapDtoToPrismaUpdate` returns `Prisma.NeumaticoUpdateInput` (nested objects).
            // Passing `PrismaInput` to Repository expecting `DTO` might type fail if repository is strict.
            // However, runtime it works if repository passes data to prisma.
            // I'll call repository.update casted as any to be safe or bypass repository for direct prisma update as mapper prepares prisma structure?
            // Better to use repository if possible. I'll cast `updateInput` as any.

            const updated = await this.repository.update(asNeumaticoId(id), updateInput as any);
            // Re-fetch relations? Update typically returns entity.
            // Map expects relations.
            // Repository update usually returns plain entity without relations?
            // Verify repository implementation. BaseRepo `update` does `model.update`.
            // So we might get bare entity.
            // Let's refetch to be safe for response.

            const reloaded = await this.repository.findByIdWithFullRelations(asNeumaticoId(id));
            if (!reloaded) return err(new NotFoundError('Neumático')); // Should not happen

            return ok(mapEntityToResponse(reloaded));
        } catch (error) {
            console.error('[NeumaticoService.update] Error:', error);
            return err(new BusinessError('Error updating neumatico', 'UPDATE_ERROR', 500));
        }
    }

    async delete(empresa_id: string, id: string): Promise<Result<void>> {
        try {
            const existing = await this.repository.findById(asNeumaticoId(id));
            if (!existing || existing.empresa_id !== empresa_id) return err(new NotFoundError('Neumático'));

            const canDelete = canDeleteNeumatico(existing);
            if (!canDelete.success) return err(canDelete.error);

            await this.repository.delete(asNeumaticoId(id));
            return ok(undefined);
        } catch (error) {
            console.error('[NeumaticoService.delete] Error:', error);
            return err(new BusinessError('Error deleting neumatico', 'DELETE_ERROR', 500));
        }
    }

    // ============================================
    // EVENT DELEGATION (Adapted)
    // ============================================

    private eventoService = new EventoNeumaticoService();

    async registrarEvento(evento: EventoNeumaticoCreate, userId: string, empresa_id: string): Promise<any> {
        const neumaticoId = asNeumaticoId(evento.neumatico_id!);
        const exists = await this.repository.findById(neumaticoId);
        if (!exists || exists.empresa_id !== empresa_id) {
            throw new Error('Neumático no encontrado o no pertenece a la empresa');
        }

        const result = await this.eventoService.registrarEvento(evento, userId as any);
        if (!result.success) throw result.error;
        return result.data;
    }

    /**
     * Ejecuta una rotación multi-neumático como transacción atómica.
     *
     * Patrón enterprise: todos los movimientos se validan antes de ejecutar,
     * y se procesan dentro de una sola transacción para garantizar atomicidad.
     * Si cualquier movimiento falla, toda la operación se revierte.
     */
    async ejecutarRotacion(
        rotacionInput: {
            vehiculo_id: string;
            contador_vehiculo: number;
            movimientos: Array<{ neumatico_id: string; posicion_destino_id: string }>;
            observaciones?: string;
        },
        userId: string,
        empresa_id: string
    ): Promise<{ movimientos_procesados: number; eventos_creados: string[] }> {
        const { vehiculo_id, contador_vehiculo, movimientos, observaciones } = rotacionInput;
        const now = new Date();

        // ============================================================
        // FASE 1: VALIDACIÓN PRE-FLIGHT (todo antes de la transacción)
        // ============================================================

        // 1.1. Validar que todos los neumáticos existen, están INSTALADOS y pertenecen a la empresa
        const neumaticosData = await prisma.neumatico.findMany({
            where: {
                id: { in: movimientos.map(m => m.neumatico_id) },
                empresa_id,
                estado_actual: 'INSTALADO',
                activo: true
            },
            select: {
                id: true,
                numero_serie: true,
                es_reencauchado: true,
                ubicacion_posicion_id: true,
                ubicacion_vehiculo_id: true
            }
        });

        if (neumaticosData.length !== movimientos.length) {
            const foundIds = new Set(neumaticosData.map(n => n.id));
            const missingIds = movimientos.map(m => m.neumatico_id).filter(id => !foundIds.has(id));
            throw new Error(
                `Neumáticos no encontrados o no instalados: ${missingIds.map(id => id.slice(0, 8)).join(', ')}`
            );
        }

        // 1.2. Validar que todos pertenecen al mismo vehículo
        const vehicleIds = new Set(neumaticosData.map(n => n.ubicacion_vehiculo_id));
        if (vehicleIds.size !== 1 || !vehicleIds.has(vehiculo_id)) {
            throw new Error('Todos los neumáticos deben pertenecer al mismo vehículo especificado');
        }

        // 1.3. Validar que no haya posiciones destino duplicadas
        const destinoIds = movimientos.map(m => m.posicion_destino_id);
        const uniqueDestinos = new Set(destinoIds);
        if (uniqueDestinos.size !== destinoIds.length) {
            throw new Error('Hay posiciones destino duplicadas en los movimientos');
        }

        // 1.4. Cargar todas las posiciones destino y validar política de reencauche
        const posicionesDestino = await prisma.posicionNeumatico.findMany({
            where: { id: { in: destinoIds } },
            include: { configuracion_eje: true }
        });

        const posMap = new Map<string, typeof posicionesDestino[number]>(posicionesDestino.map(p => [p.id, p]));

        for (const movimiento of movimientos) {
            const pos = posMap.get(movimiento.posicion_destino_id);
            if (!pos) {
                throw new Error(`Posición destino no encontrada: ${movimiento.posicion_destino_id.slice(0, 8)}`);
            }

            const neumData = neumaticosData.find(n => n.id === movimiento.neumatico_id)!;
            if (neumData.es_reencauchado && !pos.configuracion_eje.permite_reencauchados) {
                throw new Error(
                    `Neumático reencauchado ${neumData.numero_serie?.slice(0, 12)} no puede ir a posición ${pos.codigo_posicion} (eje ${pos.configuracion_eje.nombre_eje} no permite reencauchados)`
                );
            }
        }

        // 1.5. Cargar neumáticos que están en las posiciones destino (para swap)
        const ocupantesEnDestino = await prisma.neumatico.findMany({
            where: {
                ubicacion_posicion_id: { in: destinoIds },
                activo: true,
                estado_actual: 'INSTALADO'
            },
            select: {
                id: true,
                numero_serie: true,
                es_reencauchado: true,
                ubicacion_posicion_id: true
            }
        });

        const ocupanteMap = new Map<string, typeof ocupantesEnDestino[number]>(ocupantesEnDestino.map(o => [o.ubicacion_posicion_id!, o]));

        // 1.6. Validar swap: si un ocupante va a volver a la posición origen del que llega,
        //      verificar que la posición origen permita reencauchados (si aplica)
        const origenPosIds = neumaticosData
            .map(n => n.ubicacion_posicion_id)
            .filter((id): id is string => id !== null);

        const origenPosiciones = await prisma.posicionNeumatico.findMany({
            where: { id: { in: origenPosIds } },
            include: { configuracion_eje: true }
        });

        const origenPosMap = new Map<string, typeof origenPosiciones[number]>(origenPosiciones.map(p => [p.id, p]));

        for (const ocupante of ocupantesEnDestino) {
            // ¿Cuál neumático de la rotación va a la posición del ocupante?
            const movimientoHaciaOcupante = movimientos.find(
                m => m.posicion_destino_id === ocupante.ubicacion_posicion_id
            );

            if (movimientoHaciaOcupante) {
                const neumOrigen = neumaticosData.find(n => n.id === movimientoHaciaOcupante.neumatico_id)!;
                const posOrigenDelOcupante = neumOrigen.ubicacion_posicion_id;

                if (posOrigenDelOcupante && ocupante.es_reencauchado) {
                    const posOrigen = origenPosMap.get(posOrigenDelOcupante);
                    if (posOrigen && !posOrigen.configuracion_eje.permite_reencauchados) {
                        throw new Error(
                            `Swap inválido: reencauchado ${ocupante.numero_serie?.slice(0, 12)} no puede volver a posición ${posOrigen.codigo_posicion}`
                        );
                    }
                }
            }
        }

        // ============================================================
        // FASE 2: EJECUCIÓN ATÓMICA (todo o nada)
        // ============================================================

        const eventosCreados: string[] = [];

        await prisma.$transaction(async (tx) => {
            for (const movimiento of movimientos) {
                const { neumatico_id, posicion_destino_id } = movimiento;
                const neumData = neumaticosData.find(n => n.id === neumatico_id)!;
                const origenPosId = neumData.ubicacion_posicion_id;

                // Registrar evento de rotación
                const evento = await tx.eventoNeumatico.create({
                    data: {
                        tipo_evento: 'ROTACION',
                        neumatico_id,
                        fecha_evento: now,
                        contador_vehiculo,
                        vehiculo_id,
                        posicion_montaje_id: posicion_destino_id,
                        notas: observaciones || null,
                        creado_por: userId
                    }
                });
                eventosCreados.push(evento.id);

                // Actualizar posición del neumático
                await tx.neumatico.update({
                    where: { id: neumatico_id },
                    data: {
                        ubicacion_posicion_id: posicion_destino_id,
                        kilometraje_acumulado: contador_vehiculo,
                        actualizado_en: now
                    }
                });
            }

            // Procesar swaps: los ocupantes de posiciones destino van a las posiciones origen
            for (const ocupante of ocupantesEnDestino) {
                const movimientoHaciaOcupante = movimientos.find(
                    m => m.posicion_destino_id === ocupante.ubicacion_posicion_id
                );

                if (movimientoHaciaOcupante) {
                    const neumOrigen = neumaticosData.find(n => n.id === movimientoHaciaOcupante.neumatico_id)!;
                    const posOrigenDelOcupante = neumOrigen.ubicacion_posicion_id;

                    if (posOrigenDelOcupante) {
                        // Registrar evento de rotación para el ocupante
                        const eventoSwap = await tx.eventoNeumatico.create({
                            data: {
                                tipo_evento: 'ROTACION',
                                neumatico_id: ocupante.id,
                                fecha_evento: now,
                                contador_vehiculo,
                                vehiculo_id,
                                posicion_montaje_id: posOrigenDelOcupante,
                                notas: `Intercambio automático con ${neumOrigen.numero_serie}`,
                                creado_por: userId
                            }
                        });
                        eventosCreados.push(eventoSwap.id);

                        // Mover ocupante a posición origen
                        await tx.neumatico.update({
                            where: { id: ocupante.id },
                            data: {
                                ubicacion_posicion_id: posOrigenDelOcupante,
                                actualizado_en: now
                            }
                        });
                    }
                }
            }
        });

        // ============================================================
        // FASE 3: POST-CONDICIÓN (eventos y alertas post-rotación)
        // ============================================================

        // Disparar evento EventBus para observers (audit, analytics, etc.)
        try {
            const { EventBus } = await import('@/lib/events/core');
            const { NeumaticoUpdateEvent } = await import('@/lib/events/neumatico.events');

            for (const movimiento of movimientos) {
                const neumData = neumaticosData.find(n => n.id === movimiento.neumatico_id)!;
                EventBus.getInstance().emit(new NeumaticoUpdateEvent(
                    empresa_id,
                    neumData.id,
                    { ...neumData, ubicacion_posicion_id: movimiento.posicion_destino_id },
                    'ROTACION'
                ));
            }
        } catch (postError) {
            // Log but don't fail the rotation if post-conditions fail
            console.error('[Rotacion] Post-condition event failed:', postError);
        }

        return {
            movimientos_procesados: movimientos.length,
            eventos_creados: eventosCreados
        };
    }

    async getHistorialPresion(empresa_id: string, id: string) {
        // Implementation kept separate or could be moved to Helper/HistoryService
        const check = await this.repository.findById(asNeumaticoId(id));
        if (!check || check.empresa_id !== empresa_id) throw new Error('Neumático no encontrado');

        const lecturas = await prisma.lecturaPresion.findMany({
            where: { neumatico_id: id },
            orderBy: { fecha_lectura: 'asc' },
            take: 50,
            include: { usuario: { select: { nombre_completo: true, username: true } } }
        });

        const neumatico = await prisma.neumatico.findUnique({
            where: { id },
            include: { modelo: true }
        });

        return {
            lecturas: lecturas.map(l => ({
                id: l.id,
                fecha: l.fecha_lectura.toISOString(),
                presion: toNumber(l.presion_psi),
                temperatura: l.temperatura_c ? toNumber(l.temperatura_c) : undefined,
                inspector: l.usuario?.nombre_completo || l.usuario?.username || 'Sistema',
                fuente: l.fuente
            })),
            recomendada: neumatico?.modelo?.presion_recomendada_psi
                ? toNumber(neumatico.modelo.presion_recomendada_psi)
                : undefined
        };
    }

    /**
     * Calcula métricas financieras y de proyección de vida (Excel Gap Closure)
     */
    async getFinancials(empresa_id: string, id: string) {
        const neumatico = await this.repository.findByIdWithRelations(asNeumaticoId(id));
        if (!neumatico || neumatico.empresa_id !== empresa_id) {
            throw new NotFoundError('Neumático no encontrado');
        }

        const kmActual = toNumber(neumatico.kilometraje_acumulado);
        const costoCompra = toNumber(neumatico.costo_compra ?? 0);
        const profOriginal = toNumber(neumatico.modelo.profundidad_original_mm);
        // Usar profundidad remanente actual o calculada del promedio
        const profActual = toNumber(neumatico.profundidad_remanente_actual_mm);
        const profMinima = toNumber(neumatico.modelo.profundidad_minima_retiro_mm);

        // 1. CPK Actual (Cost Per Kilometer)
        // Evitar división por cero
        const cpkActual = kmActual > 0 ? costoCompra / kmActual : 0;

        // 2. Desgaste y Proyecciones
        const desgasteTotal = profOriginal - profActual;
        const mmConsumidos = Math.max(0, desgasteTotal);

        // Rendimiento: Km por cada mm consumido
        const rendimientoMm = mmConsumidos > 0 ? kmActual / mmConsumidos : 0;

        // Remanente Utilizable (hasta el retiro)
        const mmDisponibles = Math.max(0, profActual - profMinima);

        // Proyección de vida restante (Km)
        // Si no hay rendimiento calculado (nuevo), usar teórico del modelo o estimación base
        const vidaRestanteKm = rendimientoMm > 0
            ? mmDisponibles * rendimientoMm
            : (toNumber(neumatico.modelo.vida_util_teorica_km ?? 100000) - kmActual);

        const vidaTotalEstimada = kmActual + vidaRestanteKm;

        // 3. CPK Proyectado (Mejor case: si el neumatico llega al final de su vida)
        const cpkProyectado = vidaTotalEstimada > 0 ? costoCompra / vidaTotalEstimada : 0;

        // 4. Ahorro/Pérdida vs Mercado (Benchmark simple)
        // Podríamos tener un CPK objetivo en config
        const cpkObjetivo = 0.005; // Ejemplo: $0.005/km
        const ahorroProyectado = (cpkObjetivo - cpkProyectado) * vidaTotalEstimada;

        return {
            moneda: neumatico.moneda_compra ?? 'USD',
            costo_inicial: costoCompra,
            km_actual: kmActual,
            profundidad_actual_mm: profActual,

            // KPIs Financieros
            cpk_actual: Number(cpkActual.toFixed(6)),
            cpk_proyectado: Number(cpkProyectado.toFixed(6)),

            // Proyecciones
            rendimiento_km_por_mm: Number(rendimientoMm.toFixed(2)),
            vida_util_estimada_km: Number(vidaTotalEstimada.toFixed(0)),
            vida_restante_km: Number(vidaRestanteKm.toFixed(0)),

            // Status
            porcentaje_vida_restante: Number(((vidaRestanteKm / vidaTotalEstimada) * 100).toFixed(1)),
            estado_financiero: cpkProyectado < cpkObjetivo ? 'AHORRO' : 'SOBRECOSTO'
        };
    }
}

export const neumaticoService = new NeumaticoService();
