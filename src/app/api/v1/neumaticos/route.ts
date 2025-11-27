import { NextRequest } from 'next/server';
import { NeumaticoService } from '@/lib/services/neumatico.service';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { CreateNeumaticoDTO, NeumaticoFilters } from '@/types/domain/neumatico.types';

const service = new NeumaticoService();

export async function GET(request: NextRequest) {
    try {
        const { searchParams } = new URL(request.url);

        // Construir filtros desde query params
        const filters: NeumaticoFilters = {
            numero_serie: searchParams.get('numero_serie') || undefined,
            modelo_id: searchParams.get('modelo_id') || undefined,
            ubicacion_almacen_id: searchParams.get('ubicacion_almacen_id') || undefined,
            ubicacion_vehiculo_id: searchParams.get('ubicacion_vehiculo_id') || undefined,
            dot: searchParams.get('dot') || undefined,
            activo: searchParams.has('activo') ? searchParams.get('activo') === 'true' : undefined,
        };

        // TODO: Implementar paginación real en el servicio/repositorio
        // Por ahora obtenemos todos y simulamos paginación o devolvemos lista plana
        const neumaticos = await service.getAll(filters);

        return ApiResponseHelper.success(neumaticos);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();

        // Validación básica manual (idealmente usar Zod aquí)
        if (!body.numero_serie || !body.modelo_id || !body.profundidad_inicial_mm) {
            throw new Error('Faltan campos requeridos: numero_serie, modelo_id, profundidad_inicial_mm');
        }

        const data: CreateNeumaticoDTO = {
            numero_serie: body.numero_serie,
            modelo_id: body.modelo_id,
            dot: body.dot || '0000',
            estado_actual: body.estado_actual,
            profundidad_inicial_mm: Number(body.profundidad_inicial_mm),
            profundidad_actual_mm: body.profundidad_actual_mm ? Number(body.profundidad_actual_mm) : undefined,
            presion_actual_psi: body.presion_actual_psi ? Number(body.presion_actual_psi) : undefined,
            ubicacion_almacen_id: body.ubicacion_almacen_id,
            costo_compra: body.costo_compra ? Number(body.costo_compra) : undefined,
            fecha_compra: body.fecha_compra ? new Date(body.fecha_compra) : undefined,
        };

        const neumatico = await service.create(data);

        return ApiResponseHelper.created(neumatico, 'Neumático creado exitosamente');
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
