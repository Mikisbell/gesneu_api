import { NeumaticoRepository } from '@/lib/repositories/neumatico.repository';
import {
    CreateNeumaticoDTO,
    UpdateNeumaticoDTO,
    NeumaticoResponse,
    NeumaticoFilters,
    EventoCompraInput
} from '@/types/domain/neumatico.types';
import {
    mapDtoToPrismaCreate,
    mapDtoToPrismaUpdate,
    mapEntityToResponse,
    mapEntitiesToResponses
} from '@/lib/mappers/neumatico.mapper';
import {
    Result,
    ok,
    err,
    BusinessError,
    ConflictError,
    NotFoundError,
    ValidationError
} from '@/types/result.types';
import { asNeumaticoId, NeumaticoId, EmpresaId, UsuarioId } from '@/types/branded.types';
import { prisma } from '@/lib/prisma';
import { TipoEventoNeumaticoEnum, EstadoNeumaticoEnum, Prisma, Neumatico } from '@prisma/client';
import { toNumber } from '@/lib/utils/decimal';
import { EventoNeumaticoCreate } from '@/lib/validators/evento-neumatico';
import { EventoNeumaticoService } from './evento-neumatico.service';


// Tipado seguro para la transacción
type TxClient = Prisma.TransactionClient;

// Definición extendida para typescript dentro del servicio (Legacy support)
interface EventoCompra extends EventoNeumaticoCreate {
    numero_serie?: string;
    modelo_id?: string;
    dot?: string;
    profundidad_inicial?: number;
    costo_compra?: number;
}

export class NeumaticoService {
    private repository: NeumaticoRepository;

    constructor() {
        this.repository = new NeumaticoRepository();
    }

    /**
     * Crea un nuevo neumático (Compra/Alta).
     * Implementa multi-tenancy y validación de negocio.
     */
    async create(
        dto: CreateNeumaticoDTO,
        empresa_id: EmpresaId,
        userId: UsuarioId
    ): Promise<Result<NeumaticoResponse, BusinessError>> {
        // 1. Validaciones previas
        if (dto.numero_serie) {
            const existing = await this.repository.findBySerie(dto.numero_serie);
            if (existing) {
                return err(new ConflictError(`Ya existe un neumático con serie ${dto.numero_serie}`));
            }
        }

        try {
            // 2. Transacción de creación (Neumático + Evento Compra)
            const result = await prisma.$transaction(async (tx) => {
                // Preparar datos con mapper
                const prismaInput = mapDtoToPrismaCreate(dto);

                // Forzar empresa_id (Multi-tenancy critical)
                const createData = {
                    ...prismaInput,
                    empresa: { connect: { id: empresa_id } },
                    creado_por: userId,
                    activo: true,
                    fecha_compra: new Date(dto.fecha_compra || new Date()),
                };

                // Crear Neumático
                const neumatico = await tx.neumatico.create({
                    data: createData as any, // Cast necesario por tipos complejos de connect
                    include: {
                        modelo: { include: { fabricante: true } },
                        ubicacion_almacen: true,
                        ubicacion_vehiculo: { include: { tipo_vehiculo: true } },
                        ubicacion_posicion: true,
                        proveedor_compra: true,
                        motivo_desecho: true
                    }
                });

                // Registrar Evento Inicial (COMPRA)
                await tx.eventoNeumatico.create({
                    data: {
                        tipo_evento: TipoEventoNeumaticoEnum.COMPRA,
                        neumatico_id: neumatico.id,
                        fecha_evento: new Date(dto.fecha_compra || new Date()),
                        // Datos del evento
                        proveedor_id: dto.proveedor_id,
                        almacen_destino_id: dto.ubicacion_almacen_id, // Si fue a almacén
                        costo_evento: dto.costo_compra ? new Prisma.Decimal(dto.costo_compra) : undefined,
                        profundidad_remanente: dto.profundidad_inicial ?? 0,
                        notas: 'Alta inicial sistema',
                        creado_por: userId
                    }
                });

                return neumatico;
            });

            // 3. Mapear respuesta
            return ok(mapEntityToResponse(result as any));

        } catch (error: any) {
            console.error('[NeumaticoService.create] Error:', error);
            if (error.code === 'P2002') {
                return err(new ConflictError('Ya existe un neumático con estos datos únicos'));
            }
            return err(new BusinessError('Error al crear neumático', 'CREATE_ERROR', 500));
        }
    }

    /**
     * Obtiene todos los neumáticos con filtros.
     */
    async getAll(filters?: NeumaticoFilters): Promise<Result<NeumaticoResponse[], BusinessError>> {
        try {
            const entities = await this.repository.findAllWithRelations(filters);
            return ok(mapEntitiesToResponses(entities as any));
        } catch (error) {
            console.error('[NeumaticoService.getAll] Error:', error);
            return err(new BusinessError('Error al obtener neumáticos', 'QUERY_ERROR', 500));
        }
    }

    async getById(id: NeumaticoId): Promise<Result<NeumaticoResponse, NotFoundError | BusinessError>> {
        try {
            const entity = await this.repository.findByIdWithFullRelations(id);
            if (!entity) return err(new NotFoundError('Neumático', id));
            return ok(mapEntityToResponse(entity));
        } catch (error) {
            return err(new BusinessError('Error finding neumatico', 'FIND_ERROR', 500));
        }
    }

    /**
     * Actualiza un neumático.
     */
    async update(id: NeumaticoId, dto: UpdateNeumaticoDTO): Promise<Result<NeumaticoResponse, BusinessError>> {
        try {
            // Validar existencia
            const existing = await this.repository.findById(id);
            if (!existing) return err(new NotFoundError('Neumático', id));

            // Helper to map UpdateDTO to Prisma Update Input
            const updateInput = mapDtoToPrismaUpdate(dto);

            const updated = await this.repository.update(id, updateInput as any);
            return ok(mapEntityToResponse(updated as any));
        } catch (error) {
            console.error('[NeumaticoService.update] Error:', error);
            return err(new BusinessError('Error updating neumatico', 'UPDATE_ERROR', 500));
        }
    }

    /**
     * Elimina (soft-delete) un neumático.
     */
    async delete(id: NeumaticoId): Promise<Result<void, BusinessError>> {
        try {
            // Validar existencia
            const existing = await this.repository.findById(id);
            if (!existing) return err(new NotFoundError('Neumático', id));

            // Check if can be deleted (no active usage?)
            // For now just proxy to repo which likely does soft delete
            await this.repository.delete(id);
            return ok(undefined);
        } catch (error) {
            console.error('[NeumaticoService.delete] Error:', error);
            return err(new BusinessError('Error deleting neumatico', 'DELETE_ERROR', 500));
        }
    }

    // ============================================
    // LEGACY & OPERATION METHODS (Restored)
    // ============================================

    // ============================================
    // EVENT DELEGATION (Standardized)
    // ============================================

    private eventoService = new EventoNeumaticoService();

    /**
     * Registra un evento delegando al servicio especializado.
     */
    async registrarEvento(evento: EventoNeumaticoCreate, userId: string): Promise<any> {
        // Adaptador para usar el nuevo servicio que retorna Result<>
        // Mantenemos la firma de promesa básica para compatibilidad, o lanzamos error si falla
        const result = await this.eventoService.registrarEvento(evento, userId as UsuarioId);

        if (!result.success) {
            throw result.error; // Re-throw como excepción para mantener compatibilidad con callers legacy
        }

        return result.data;
    }

    async getHistorialPresion(id: string) {
        // Obtenemos lecturas de presión ordenadas por fecha
        const lecturas = await prisma.lecturaPresion.findMany({
            where: { neumatico_id: id },
            orderBy: { fecha_lectura: 'asc' }, // Ascendente para gráfico
            take: 50, // Límite razonable
            include: {
                usuario: {
                    select: { nombre_completo: true, username: true }
                }
            }
        });

        // Obtenemos info del neumático para saber la recomendada
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
}

