import { VehiculoEntity } from '@/types/domain/vehiculo.types';
import { Result, ok, err, ConflictError, BusinessError } from '@/types/result.types';

/**
 * Valida si un vehículo puede ser eliminado del sistema.
 * Regla: No se puede eliminar si tiene neumáticos instalados o si tiene kilometraje acumulado considerable
 *        (aunque esto último es discutible, por ahora solo validamos neumáticos).
 */
export function canDeleteVehiculo(vehiculo: VehiculoEntity): Result<true, BusinessError> {
    // 1. Neumáticos instalados
    if (vehiculo.neumaticos_instalados && vehiculo.neumaticos_instalados.length > 0) {
        return err(new ConflictError(`No se puede eliminar un vehículo con ${vehiculo.neumaticos_instalados.length} neumáticos instalados. Desmóntelos primero.`));
    }

    // 2. Otras reglas futuras (ej: viajes activos, etc.)

    return ok(true);
}

/**
 * Valida si se puede desactivar un vehículo.
 * Regla: Similar a delete, pero quizás menos estricta.
 */
export function canDeactivateVehiculo(vehiculo: VehiculoEntity): Result<true, BusinessError> {
    if (vehiculo.neumaticos_instalados && vehiculo.neumaticos_instalados.length > 0) {
        // Política: ¿Permitimos desactivar con neumáticos? 
        // Riesgo: Los neumáticos quedarían "Instalados" en un vehículo fantasma.
        // Decisión: No, deben desmontarse o el vehículo debe seguir activo.
        return err(new ConflictError('No se puede desactivar un vehículo con neumáticos instalados.'));
    }
    return ok(true);
}
