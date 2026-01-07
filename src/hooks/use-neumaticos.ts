import { useQuery } from '@tanstack/react-query';
import { EstadoNeumaticoEnum } from '@prisma/client';

interface Neumatico {
    id: string;
    numero_serie: string;
    modelo_id: string;
    estado_actual: EstadoNeumaticoEnum;
    profundidad_remanente_actual_mm: number;
    ubicacion_almacen_id?: string;
    ubicacion_vehiculo_id?: string;
    ubicacion_posicion_id?: string;
    // Add other fields as needed
}

export function useNeumaticos(estado?: EstadoNeumaticoEnum) {
    return useQuery<Neumatico[]>({
        queryKey: ['neumaticos', estado],
        queryFn: async () => {
            const url = estado
                ? `/api/v1/neumaticos?estado_actual=${estado}`
                : '/api/v1/neumaticos';

            const response = await fetch(url);
            if (!response.ok) {
                throw new Error('Error fetching neumaticos');
            }
            const data = await response.json();
            return data.data || data; // Handle potential API response wrapper
        },
    });
}

export function useNeumaticosEnStock() {
    return useNeumaticos(EstadoNeumaticoEnum.EN_STOCK);
}
