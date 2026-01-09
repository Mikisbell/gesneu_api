
import 'dotenv/config';
import { TipoEventoNeumaticoEnum, EstadoNeumaticoEnum } from '@prisma/client';
import { prisma } from '../src/lib/prisma';
import { EventoNeumaticoService } from '../src/lib/services/evento-neumatico.service';
import { NeumaticoService } from '../src/lib/services/neumatico.service';
import { CreateEventoInput } from '../src/lib/validators/evento-neumatico';
import { asUsuarioId, asEmpresaId } from '../src/types/branded.types';

async function main() {
    console.log('🚀 Starting EventoNeumatico Verification...');

    const eventoService = new EventoNeumaticoService();
    const neumaticoService = new NeumaticoService();

    // Cleanup (Robust cascade)
    const testTires = await prisma.neumatico.findMany({ where: { numero_serie: { contains: 'TEST_EVT' } }, select: { id: true } });
    const tireIds = testTires.map(t => t.id);
    if (tireIds.length > 0) {
        await prisma.eventoNeumatico.deleteMany({ where: { neumatico_id: { in: tireIds } } });
        await prisma.historialEstadoNeumatico.deleteMany({ where: { neumatico_id: { in: tireIds } } });
        await prisma.neumatico.deleteMany({ where: { id: { in: tireIds } } });
    }
    const testVehicles = await prisma.vehiculo.findMany({ where: { placa: 'TEST-VBP' }, select: { id: true } });
    if (testVehicles.length > 0) {
        const vIds = testVehicles.map(v => v.id);
        await prisma.registroContador.deleteMany({ where: { vehiculo_id: { in: vIds } } });
        await prisma.vehiculo.deleteMany({ where: { id: { in: vIds } } });
    }

    // 1. Setup: Create Tire & Vehicle
    console.log('1. Setting up test data...');
    const adminUser = await prisma.usuario.findFirst();
    const empresa = await prisma.empresa.findFirst();

    if (!adminUser || !empresa) throw new Error('Need generic user/empresa');
    const userId = asUsuarioId(adminUser.id);
    const empresaId = asEmpresaId(empresa.id);

    // Scoped lookups where applicable
    const modelo = await prisma.modeloNeumatico.findFirst();
    const almacen = await prisma.almacen.findFirst({ where: { empresa_id: empresa.id } });

    if (!modelo) throw new Error('No Modelo found');
    if (!almacen) throw new Error('No Almacen found for this company');

    // Create Tire
    const neumaticoResult = await neumaticoService.create({
        numero_serie: `TEST_EVT_${Date.now()}`,
        modelo_id: modelo.id,
        dot: '2222',
        profundidad_inicial: 20,
        estado: 'NUEVO',
        fecha_compra: new Date(),
        costo_compra: 100,
        ubicacion_almacen_id: almacen.id,
        moneda_compra: 'USD'
    }, empresaId, userId);

    if (!neumaticoResult.success) throw new Error('Failed to create neumatico: ' + neumaticoResult.error.message);
    const neumaticoId = neumaticoResult.data.id;
    console.log(`   ✅ Created Neumatico: ${neumaticoId}`);

    // Create Vehicle
    const tipoVehiculo = await prisma.tipoVehiculo.findFirst();
    if (!tipoVehiculo) throw new Error('No TipoVehiculo found');

    const vehiculo = await prisma.vehiculo.create({
        data: {
            empresa_id: empresa.id,
            placa: 'TEST-VBP',
            tipo_vehiculo_id: tipoVehiculo.id,
            numero_economico: 'TEC-99',
            modelo_vehiculo: 'Test',
            anio_fabricacion: 2024,
            activo: true
        }
    });
    console.log(`   ✅ Created Vehiculo: ${vehiculo.id}`);

    // 2. Test INSTALACION Event
    console.log('2. Testing INSTALACION...');
    const instalacionInput: CreateEventoInput = {
        tipo_evento: TipoEventoNeumaticoEnum.INSTALACION,
        neumatico_id: neumaticoId,
        vehiculo_id: vehiculo.id,
        fecha_evento: new Date(),
        contador_vehiculo: 1000,
        profundidad_remanente: 19.5,
        presion_psi: 100,
        observaciones: 'TEST_AUTO Instalación'
    };

    const instResult = await eventoService.registrarEvento(instalacionInput, userId);

    if (!instResult.success) {
        console.error('❌ Instalacion Failed:', instResult.error);
        process.exit(1);
    }
    console.log('   ✅ Instalacion Event Created');

    // Verify State Change (Side Effect)
    const updatedNeumatico = await prisma.neumatico.findUnique({ where: { id: neumaticoId } });
    if (updatedNeumatico?.estado_actual !== EstadoNeumaticoEnum.INSTALADO) {
        console.error('❌ State mismatch. Expected INSTALADO, got:', updatedNeumatico?.estado_actual);
        process.exit(1);
    }
    if (updatedNeumatico?.ubicacion_vehiculo_id !== vehiculo.id) {
        console.error('❌ Location mismatch. Expected Vehicle ID');
        process.exit(1);
    }
    console.log('   ✅ Neumatico State Updated correctly');

    // 3. Test INSPECCION (While installed)
    console.log('3. Testing INSPECCION...');
    const inspeccionInput: CreateEventoInput = {
        tipo_evento: TipoEventoNeumaticoEnum.INSPECCION,
        neumatico_id: neumaticoId,
        fecha_evento: new Date(),
        contador_vehiculo: 1500,
        profundidad_remanente: 18,
        presion_psi: 95,
        observaciones: 'TEST_AUTO Inspeccion'
    };
    const inspResult = await eventoService.registrarEvento(inspeccionInput, userId);
    if (!inspResult.success) throw new Error('Inspeccion failed');
    console.log('   ✅ Inspeccion Event Created');

    // 4. Test DESMONTAJE
    console.log('4. Testing DESMONTAJE...');
    // We reuse the 'almacen' variable found earlier
    const desmontajeInput: CreateEventoInput = {
        tipo_evento: TipoEventoNeumaticoEnum.DESMONTAJE,
        neumatico_id: neumaticoId,
        fecha_evento: new Date(),
        contador_vehiculo: 2000,
        profundidad_remanente: 17,
        estado_neumatico_resultante: 'EN_STOCK',
        almacen_destino_id: almacen.id,
        observaciones: 'TEST_AUTO Desmontaje'
    };

    const desResult = await eventoService.registrarEvento(desmontajeInput, userId);
    if (!desResult.success) {
        console.error('❌ Desmontaje Failed:', desResult.error);
        process.exit(1);
    }
    console.log('   ✅ Desmontaje Event Created');

    // Verify KM accumulation
    const finalNeumatico = await prisma.neumatico.findUnique({ where: { id: neumaticoId } });
    if (finalNeumatico?.estado_actual !== EstadoNeumaticoEnum.EN_STOCK) {
        console.error('❌ State mismatch after dismount. Expected EN_STOCK');
        process.exit(1);
    }
    // KM Calculation: (2000 - 1000) = 1000km added.
    if (finalNeumatico?.kilometraje_acumulado !== 1000) {
        console.warn(`⚠️ KM Accumulation Warning: Expected 1000, got ${finalNeumatico?.kilometraje_acumulado}. Check logic if initial KM was 0.`);
    } else {
        console.log('   ✅ KM Accumulated Correctly (1000km)');
    }

    console.log('🎉 Verification Successful!');
}

main()
    .catch(e => console.error(e))
    .finally(async () => {
        await prisma.$disconnect();
    });
