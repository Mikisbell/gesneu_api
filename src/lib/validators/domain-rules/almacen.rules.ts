/**
 * Almacen Domain Rules
 */
import { AlmacenEntity } from '@/types/domain/almacen.types';
import { Result, ok, err, ConflictError, BusinessError } from '@/types/result.types';

export function canDeactivateAlmacen(almacen: AlmacenEntity, neumaticosCount: number): Result<true, BusinessError> {
    if (neumaticosCount > 0) {
        return err(new ConflictError(`No se puede desactivar un almacén con ${neumaticosCount} neumáticos en stock`));
    }
    return ok(true);
}
