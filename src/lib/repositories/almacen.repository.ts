import { Almacen } from '@prisma/client';
import { BaseRepository } from './base.repository';
import { CreateAlmacenDTO, UpdateAlmacenDTO, AlmacenEntity } from '@/types/domain/almacen.types';

export class AlmacenRepository extends BaseRepository<Almacen, CreateAlmacenDTO, UpdateAlmacenDTO> {
    protected model = this.db.almacen;

    /**
     * Busca almacén por código único
     */
    async findByCodigo(codigo: string): Promise<AlmacenEntity | null> {
        try {
            const result = await this.model.findUnique({
                where: { codigo }
            });
            return result as AlmacenEntity | null;
        } catch (error) {
            this.handleError(error);
            throw error;
        }
    }
}
