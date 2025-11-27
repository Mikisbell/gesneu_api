import { VehiculoService } from '../src/lib/services/vehiculo.service';
import { prisma } from '../src/lib/prisma';

async function main() {
    console.log('🚀 Iniciando prueba del Módulo de Vehículos...');

    const service = new VehiculoService();

    try {
        // 1. Buscar un tipo de vehículo existente (del Seed)
        let tipo = await prisma.tipoVehiculo.findFirst();

        if (!tipo) {
            console.error('❌ Error: No hay tipos de vehículo. Ejecuta el seed primero.');
            return;
        }
        console.log(`ℹ️ Usando tipo de vehículo: ${tipo.nombre}`);

        // 2. Crear un vehículo
        const placa = `TEST-${Math.floor(Math.random() * 1000)}`;
        console.log(`📝 Creando vehículo con placa: ${placa}`);

        const nuevo = await service.create({
            placa: placa,
            tipo_vehiculo_id: tipo.id,
            marca: 'Volvo Test',
            modelo: 'FH16',
            anio: 2024,
            kilometraje_actual: 15000
        });

        console.log('✅ Vehículo creado:', nuevo.id);

        // 3. Buscar por placa
        console.log('🔍 Buscando por placa...');
        const encontrado = await service.getByPlaca(placa);

        if (encontrado?.id === nuevo.id) {
            console.log('✅ Búsqueda exitosa');
            console.log(`   - Marca: ${encontrado.marca}`);
            console.log(`   - Tipo: ${encontrado.tipo_vehiculo?.nombre}`);
        } else {
            console.error('❌ Error: No se encontró el vehículo creado');
        }

        // 4. Limpieza
        console.log('🧹 Limpiando datos de prueba...');
        await service.delete(nuevo.id);
        console.log('✅ Limpieza completada');

    } catch (error) {
        console.error('❌ Error en la prueba:', error);
    } finally {
        await prisma.$disconnect();
    }
}

main();
