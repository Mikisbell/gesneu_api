import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { NeumaticoService } from '@/lib/services/neumatico.service';
import { VehiculoService } from '@/lib/services/vehiculo.service';
import MontajeClient from './montaje-client';
import { EstadoNeumaticoEnum } from '@prisma/client';
import { VehiculoId } from '@/types/branded.types';

export const metadata: Metadata = {
    title: 'Montaje de Neumáticos | GesNeu',
    description: 'Gestión visual de montaje de neumáticos',
};

interface PageProps {
    params: Promise<{
        id: string;
    }>;
}

// Servicios (Instanciados aquí o usar inyección de dependencias si está configurada)
// Nota: En un entorno real, estos deberían ser singletons o usar un contenedor DI.
// Por simplicidad y dado que son stateless (mayormente), los instanciamos.
const vehiculoService = new VehiculoService();
const neumaticoService = new NeumaticoService();

export default async function MontajePage({ params }: PageProps) {
    const { id } = await params;

    // 1. Obtener Vehículo (Result pattern)
    const vehiculoResult = await vehiculoService.getByIdWithFullConfig(id as VehiculoId);
    if (!vehiculoResult.success) {
        notFound();
    }
    const vehiculo = vehiculoResult.data;

    // 2. Obtener Neumáticos Instalados en este vehículo (Optimizado)
    const neumaticosInstaladosResult = await neumaticoService.getAll({
        ubicacion_vehiculo_id: id,
        estado_actual: EstadoNeumaticoEnum.INSTALADO
    });
    const neumaticosInstalados = neumaticosInstaladosResult.success ? neumaticosInstaladosResult.data : [];

    // 3. Obtener Stock Disponible (Optimizado)
    const stockResult = await neumaticoService.getAll({
        estado_actual: EstadoNeumaticoEnum.EN_STOCK
    });
    const stock = stockResult.success ? stockResult.data : [];

    // Helper to serialize Prisma objects (handle Decimals)
    const serializeNeumatico = (n: any) => ({
        ...n,
        costo_compra: n.costo_compra ? Number(n.costo_compra) : null,
    });

    const serializedVehiculo = {
        ...vehiculo,
        // VehiculoResponse may not have neumaticos_instalados, handle safely
        neumaticos_instalados: (vehiculo as any).neumaticos_instalados?.map(serializeNeumatico) || []
    };

    return (
        <MontajeClient
            vehiculo={serializedVehiculo}
            stock={stock.map(serializeNeumatico)}
            neumaticosInstalados={neumaticosInstalados.map(serializeNeumatico)}
        />
    );
}
