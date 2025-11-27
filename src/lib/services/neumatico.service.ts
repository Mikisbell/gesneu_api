import { NeumaticoRepository } from '@/lib/repositories/neumatico.repository';
import { CreateNeumaticoDTO, UpdateNeumaticoDTO, INeumatico, NeumaticoFilters } from '@/types/domain/neumatico.types';

export class NeumaticoService {
    private repository: NeumaticoRepository;

    constructor() {
        this.repository = new NeumaticoRepository();
    }

    async getAll(filters?: NeumaticoFilters): Promise<INeumatico[]> {
        return await this.repository.findAllWithRelations(filters);
    }

    async getById(id: string): Promise<INeumatico | null> {
        return await this.repository.findById(id);
    }

    async getBySerie(serie: string): Promise<INeumatico | null> {
        return await this.repository.findBySerie(serie);
    }

    async create(data: CreateNeumaticoDTO): Promise<INeumatico> {
        // Validación de negocio: Verificar unicidad de serie
        const existing = await this.repository.findBySerie(data.numero_serie);
        if (existing) {
            throw new Error(`El neumático con serie ${data.numero_serie} ya existe.`);
        }

        return await this.repository.create(data);
    }

    async update(id: string, data: UpdateNeumaticoDTO): Promise<INeumatico> {
        const existing = await this.repository.findById(id);
        if (!existing) {
            throw new Error('Neumático no encontrado');
        }
        return await this.repository.update(id, data);
    }

    async delete(id: string): Promise<INeumatico> {
        return await this.repository.delete(id);
    }
}
