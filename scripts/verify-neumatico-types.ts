import 'dotenv/config';
import { PrismaClient } from '@prisma/client';
import { NeumaticoService } from '@/lib/services/neumatico.service';
import { CreateNeumaticoDTO, UpdateNeumaticoDTO } from '@/types/domain/neumatico.types';
import { asNeumaticoId, asEmpresaId, asUsuarioId } from '@/types/branded.types';

const prisma = new PrismaClient();
const service = new NeumaticoService();

async function main() {
    console.log('🔄 Starting NeumaticoService Type Verification...');

    // 1. Setup Mock User/Company (or fetch existing)
    const empresaId = asEmpresaId('00000000-0000-0000-0000-000000000000'); // Assuming seed data exists or this UUID format is valid for testing
    // However, verification script usually runs against local DB. 
    // I should probably fetch a valid user/empresa first or create dummy ones if "seed" is not guaranteed.
    // Let's try to fetch the first user.
    const user = await prisma.usuario.findFirst();
    if (!user) {
        console.error('❌ No user found to run test. Seed DB first.');
        process.exit(1);
    }
    const userId = asUsuarioId(user.id);
    const realEmpresaId = asEmpresaId(user.empresa_id || empresaId);

    // 2. Fetch a valid Model (required for creation)
    const modelo = await prisma.modeloNeumatico.findFirst();
    if (!modelo) {
        console.error('❌ No ModeloNeumatico found.');
        process.exit(1);
    }

    console.log(`✅ Setup: User ${user.email}, Company ${realEmpresaId}, Modelo ${modelo.nombre_modelo}`);

    // 3. Test Create
    const serial = `TEST-TYPE-${Date.now()}`;
    const createDto: CreateNeumaticoDTO = {
        modelo_id: modelo.id,
        numero_serie: serial,
        fecha_compra: new Date().toISOString(),
        costo_compra: 100,
        ubicacion_almacen_id: undefined // Optional
    };

    console.log('▶️ Testing create()...');
    const createResult = await service.create(createDto, realEmpresaId, userId);

    if (!createResult.success) {
        console.error('❌ Create failed:', createResult.error);
        process.exit(1);
    }
    const neumaticoId = createResult.data.id; // Already typed as NeumaticoId
    console.log(`✅ Create success: ID ${neumaticoId}, Serie ${createResult.data.identificacion.serie}`);

    // 4. Test GetById
    console.log('▶️ Testing getById()...');
    // Note: getById expects NeumaticoId, which we got from createResult
    const getResult = await service.getById(neumaticoId);
    if (!getResult.success) {
        console.error('❌ GetById failed:', getResult.error);
        process.exit(1);
    }
    console.log('✅ GetById success');

    // 5. Test Update
    console.log('▶️ Testing update()...');
    const updateDto: UpdateNeumaticoDTO = {
        notas: 'Updated via type verification script'
    };
    const updateResult = await service.update(neumaticoId, updateDto);
    if (!updateResult.success) {
        console.error('❌ Update failed:', updateResult.error);
        process.exit(1);
    }
    console.log('✅ Update success');

    // 6. Test Delete
    console.log('▶️ Testing delete()...');
    const deleteResult = await service.delete(neumaticoId);
    if (!deleteResult.success) {
        console.error('❌ Delete failed:', deleteResult.error);
        process.exit(1);
    }
    console.log('✅ Delete success');

    console.log('🎉 All service type verifications passed!');
}

main()
    .catch((e) => {
        console.error('❌ Script error:', e);
        process.exit(1);
    })
    .finally(async () => {
        await prisma.$disconnect();
    });
