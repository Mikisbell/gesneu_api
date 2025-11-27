import { VehiculoRepository } from '@/lib/repositories/vehiculo.repository';
import { CreateVehiculoDTO, UpdateVehiculoDTO, IVehiculo, VehiculoFilters } from '@/types/domain/vehiculo.types';

export class VehiculoService {
    private repository: VehiculoRepository;

    constructor() {
        this.repository = new VehiculoRepository();
    }

    async getAll(filters?: VehiculoFilters): Promise<IVehiculo[]> {
        return await this.repository.findAllWithRelations(filters);
    }

    async getById(id: string): Promise<IVehiculo | null> {
        return await this.repository.findById(id);
    }

    async getByPlaca(placa: string): Promise<IVehiculo | null> {
        return await this.repository.findByPlaca(placa);
    }

    async create(data: CreateVehiculoDTO): Promise<IVehiculo> {
        // Validación de negocio: Verificar unicidad de placa
        const existing = await this.repository.findByPlaca(data.placa);
        if (existing) {
            throw new Error(`El vehículo con placa ${data.placa} ya existe.`);
        }

        return await this.repository.create(data);
    }

    async update(id: string, data: UpdateVehiculoDTO): Promise<IVehiculo> {
        const existing = await this.repository.findById(id);
        if (!existing) {
            throw new Error('Vehículo no encontrado');
        }
        return await this.repository.update(id, data);
    }

    async delete(id: string): Promise<IVehiculo> {
        return await this.repository.delete(id);
    }
}
