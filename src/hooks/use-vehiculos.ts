import { useQuery } from '@tanstack/react-query';

interface Vehiculo {
    id: string;
    placa: string;
    tipo_vehiculo_id: string;
    tipo_medicion: 'KILOMETRAJE' | 'HOROMETRO';
    odometro_actual: number;
    // Add other fields as needed
}

export function useVehiculos() {
    return useQuery<Vehiculo[]>({
        queryKey: ['vehiculos'],
        queryFn: async () => {
            const response = await fetch('/api/v1/vehiculos');
            if (!response.ok) {
                throw new Error('Error fetching vehiculos');
            }
            const data = await response.json();
            return data.data || data; // Handle potential API response wrapper
        },
    });
}
