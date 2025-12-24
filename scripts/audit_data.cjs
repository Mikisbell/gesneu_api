const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function audit() {
    console.log('--- 🔍 AUDITORÍA DEL SISTEMA GESNEU ---');

    // 1. Usuarios
    console.log('\n👤 USUARIOS:');
    try {
        const usuarios = await prisma.usuario.groupBy({ by: ['rol'], _count: true });
        usuarios.forEach(u => console.log(`   - ${u.rol}: ${u._count} usuarios`));
    } catch (e) {
        console.log('   (No hay datos de Usuarios)');
    }

    // 2. Almacenes
    console.log('\n🏭 ALMACENES:');
    const almacenes = await prisma.almacen.findMany();
    almacenes.forEach(a => console.log(`   - ${a.nombre} (${a.tipo}) - Ubicación: ${a.ubicacion || 'N/A'}`));

    // 3. Proveedores
    console.log('\n🤝 PROVEEDORES:');
    const proveedores = await prisma.proveedor.findMany();
    proveedores.forEach(p => console.log(`   - ${p.nombre} (${p.tipo})`));

    // 4. Centros de Costo
    console.log('\n💰 CENTROS DE COSTO:');
    const cecos = await prisma.centroCosto.findMany();
    cecos.forEach(c => console.log(`   - [${c.codigo}] ${c.nombre}`));

    // 5. Vehículos
    console.log(`\n🚛 VEHÍCULOS:`);
    const vehiculosCount = await prisma.vehiculo.count();
    console.log(`   - Total: ${vehiculosCount}`);

    // Agrupar por tipo (usando include si posible, o fetch aparte)
    const vehiculos = await prisma.vehiculo.findMany({ select: { tipo_vehiculo: { select: { nombre: true } } } });
    const tipoMap = {};
    vehiculos.forEach(v => {
        const t = v.tipo_vehiculo ? v.tipo_vehiculo.nombre : 'Desconocido';
        tipoMap[t] = (tipoMap[t] || 0) + 1;
    });
    for (const [tipo, count] of Object.entries(tipoMap)) {
        console.log(`   - ${tipo}: ${count} unidades`);
    }

    // 6. Neumáticos
    console.log(`\n🍩 NEUMÁTICOS:`);
    const neumaticosCount = await prisma.neumatico.count();
    console.log(`   - Total: ${neumaticosCount}`);

    const neumaticosEstado = await prisma.neumatico.groupBy({ by: ['estado_actual'], _count: true });
    neumaticosEstado.forEach(n => console.log(`   - ${n.estado_actual}: ${n._count}`));

    // 7. Catálogo
    const fabricantesCount = await prisma.fabricanteNeumatico.count();
    const modelosCount = await prisma.modeloNeumatico.count();
    const modelos = await prisma.modeloNeumatico.findMany({ include: { fabricante: true } });
    console.log(`\n🏷️ CATÁLOGO:`);
    console.log(`   - ${fabricantesCount} Fabricantes`);
    console.log(`   - ${modelosCount} Modelos de neumáticos`);
    // Listar modelos
    // modelos.forEach(m => console.log(`     * ${m.fabricante.nombre} ${m.nombre} (${m.medida})`));

    // 8. Eventos
    const eventosCount = await prisma.eventoNeumatico.count();
    const eventosTipo = await prisma.eventoNeumatico.groupBy({ by: ['tipo_evento'], _count: true });
    console.log(`\n📋 OPERACIONES:`);
    console.log(`   - Total: ${eventosCount}`);
    eventosTipo.forEach(e => console.log(`   - ${e.tipo_evento}: ${e._count}`));

    // 9. Alertas
    const alertasCount = await prisma.alerta.count();
    const alertasSeveridad = await prisma.alerta.groupBy({ by: ['severidad'], _count: true });
    console.log(`\n🚨 ALERTAS:`);
    console.log(`   - Total: ${alertasCount}`);
    alertasSeveridad.forEach(a => console.log(`   - ${a.severidad}: ${a._count}`));

    // 10. Configuración
    const configEjesCount = await prisma.configuracionEje.count();
    console.log(`\n⚙️ CONFIGURACIÓN:`);
    console.log(`   - ${configEjesCount} configs de eje`);
}

audit()
    .catch(e => console.error(e))
    .finally(async () => await prisma.$disconnect());
