import { NeumaticoService } from '../src/lib/services/neumatico.service';
import { prisma } from '../src/lib/prisma';

async function main() {
    console.log('🚀 Iniciando prueba del Módulo de Neumáticos...');

    const service = new NeumaticoService();

    try {
        // 1. Buscar un modelo existente o crear uno dummy para la prueba
        // Para simplificar, buscaremos el primero que exista
        let modelo = await prisma.modeloNeumatico.findFirst();

        if (!modelo) {
            console.log('⚠️ No hay modelos. Creando uno de prueba...');
            const fabricante = await prisma.fabricanteNeumatico.create({
                data: {
                    nombre: 'Fabricante Test Script',
                    pais_origen: 'Japón'
                }
            });
            modelo = await prisma.modeloNeumatico.create({
                data: {
                    nombre: 'Modelo Test Script',
                    fabricante_id: fabricante.id,
                    medida: '11R22.5',
                    profundidad_inicial_mm: 20,
                    reencauches_maximos: 2
                }
            });
        }

        // 2. Crear un neumático
        const serie = `TEST-SCRIPT-${Date.now()}`;
        console.log(`📝 Creando neumático con serie: ${serie}`);

        const nuevo = await service.create({
            numero_serie: serie,
            modelo_id: modelo.id,
            dot: '2024',
            profundidad_inicial_mm: 20,
            estado_actual: 'EN_STOCK'
        });

        console.log('✅ Neumático creado:', nuevo.id);

        // 3. Buscar por serie
        console.log('🔍 Buscando por serie...');
        const encontrado = await service.getBySerie(serie);

        if (encontrado?.id === nuevo.id) {
            console.log('✅ Búsqueda exitosa');
        } else {
            console.error('❌ Error: No se encontró el neumático creado');
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
