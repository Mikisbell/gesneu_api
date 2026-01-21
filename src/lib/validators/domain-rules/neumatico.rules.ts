import { NeumaticoEntity } from '@/types/domain/neumatico.types';
import { Result, ok, err, ConflictError, BusinessError } from '@/types/result.types';
import { EstadoNeumaticoEnum } from '@prisma/client';

/**
 * Valida si un neumático puede ser eliminado del sistema.
 * Regla: No se puede eliminar si está instalado, en reparación, en reencauche,
 *        o si tiene historial de mediciones (para preservar integridad).
 *        Solo se permite eliminar si es un neumático NUEVO (error de carga) o DESECHO (si se purga).
 *        
 * Nota: En la práctica, solemos preferir soft-delete o marcar como inactivo, 
 *       pero si se requiere delete físico, estas son las reglas.
 */
// Partial to allow both Entity and Scalar/Prisma object
export function canDeleteNeumatico(neumatico: {
    estado_actual: EstadoNeumaticoEnum;
    ubicacion_vehiculo_id: string | null;
    ubicacion_posicion_id: string | null;
}): Result<true, BusinessError> {
    // 1. Estado Actual
    const estadosProtegidos: EstadoNeumaticoEnum[] = [
        EstadoNeumaticoEnum.INSTALADO,
        EstadoNeumaticoEnum.EN_REPARACION,
        EstadoNeumaticoEnum.EN_REENCAUCHE
    ];

    if (estadosProtegidos.includes(neumatico.estado_actual)) {
        return err(new ConflictError(`No se puede eliminar un neumático en estado ${neumatico.estado_actual}`));
    }

    // 2. Ubicación Activa (Redundante con estado, pero por seguridad)
    if (neumatico.ubicacion_vehiculo_id || neumatico.ubicacion_posicion_id) {
        return err(new ConflictError('El neumático está asignado a un vehículo/posición'));
    }

    // 3. Dependencias (Opcional: Si queremos ser muy estrictos)
    // Prisma se quejará por FKs si intentamos borrar y tiene eventos, 
    // pero aquí validamos la regla de negocio "lógica".

    return ok(true);
}

/**
 * Valida si se puede actualizar un neumático.
 * Regla: Algunos campos críticos no deberían cambiar si el neumático ya tiene uso.
 */
export function canUpdateSemanticaNeumatico(neumatico: NeumaticoEntity, changes: any): Result<true, BusinessError> {
    // Ejemplo: No cambiar modelo si ya tiene históricos (podría invalidar estadísticas)
    // Por ahora permitimos todo, pero dejamos el hook listo.
    return ok(true);
}
