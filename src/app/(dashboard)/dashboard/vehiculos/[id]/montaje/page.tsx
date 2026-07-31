import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { NeumaticoService } from '@/lib/services/neumatico.service';
import { VehiculoService } from '@/lib/services/vehiculo.service';
import { requireAuth } from '@/lib/auth/authorization';
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
    const session = await requireAuth();

    if (!session.user.empresa_id) {
        notFound(); // O redirect a error
    }

    // 1. Obtener Vehículo (Result pattern)
    const vehiculoResult = await vehiculoService.getByIdWithFullConfig(session.user.empresa_id!, id as VehiculoId);
    if (!vehiculoResult.success) {
        notFound();
    }
    const vehiculo = vehiculoResult.data;

    // 2. Obtener Neumáticos Instalados en este vehículo (Optimizado)
    const neumaticosInstaladosResult = await neumaticoService.getAll(session.user.empresa_id!, {
        ubicacion_vehiculo_id: id,
        estado_actual: EstadoNeumaticoEnum.INSTALADO
    });
    const neumaticosInstalados = neumaticosInstaladosResult.success ? neumaticosInstaladosResult.data : [];

    // 3. Obtener Stock Disponible (Robusto contra variaciones de enum)
    const stockResult = await neumaticoService.getAll(session.user.empresa_id!);
    const allNeumaticos = stockResult.success ? stockResult.data : [];
    const stock = allNeumaticos.filter((n: any) => {
        const estado = n.estado || n.estado_actual;
        const esAlmacen = n.ubicacion?.tipo === 'ALMACEN' || Boolean(n.ubicacion_almacen_id);
        return esAlmacen || estado === 'EN_STOCK' || estado === 'DISPONIBLE';
    });

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
