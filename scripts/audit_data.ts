import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function audit() {
    console.log('--- 🔍 AUDITORÍA DEL SISTEMA GESNEU ---');

    // 1. Usuarios
    const usuarios = await prisma.usuario.groupBy({ by: ['rol'], _count: true });
    console.log('\n👤 USUARIOS:');
    usuarios.forEach(u => console.log(`   - ${u.rol}: ${u._count} usuarios`));

    // 2. Almacenes
    const almacenes = await prisma.almacen.findMany();
    console.log('\n🏭 ALMACENES:');
    almacenes.forEach(a => console.log(`   - ${a.nombre} (${a.tipo}) - Ubicación: ${a.ubicacion || 'N/A'}`));

    // 3. Proveedores
    const proveedores = await prisma.proveedor.findMany();
    console.log('\n🤝 PROVEEDORES:');
    proveedores.forEach(p => console.log(`   - ${p.nombre} (${p.tipo})`));

    // 4. Centros de Costo
    const cecos = await prisma.centroCosto.findMany();
    console.log('\n💰 CENTROS DE COSTO:');
    cecos.forEach(c => console.log(`   - [${c.codigo}] ${c.nombre}`));

    // 5. Vehículos (Resumen)
    const vehiculosCount = await prisma.vehiculo.count();
    const vehiculosTipos = await prisma.vehiculo.groupBy({ by: ['tipo_vehiculo_id'], _count: true });
    // Need to fetch types names
    console.log(`\n🚛 VEHÍCULOS (Total: ${vehiculosCount}):`);
    const tiposVehiculo = await prisma.tipoVehiculo.findMany();
    const tipoMap = new Map(tiposVehiculo.map(t => [t.id, t.nombre]));
    vehiculosTipos.forEach(v => console.log(`   - ${tipoMap.get(v.tipo_vehiculo_id) || 'Desconocido'}: ${v._count} unidades`));

    // 6. Neumáticos
    const neumaticosCount = await prisma.neumatico.count();
    const neumaticosEstado = await prisma.neumatico.groupBy({ by: ['estado_actual'], _count: true });
    console.log(`\n🍩 NEUMÁTICOS (Total: ${neumaticosCount}):`);
    neumaticosEstado.forEach(n => console.log(`   - ${n.estado_actual}: ${n._count}`));

    // 7. Marcas/Modelos
    const fabricantesCount = await prisma.fabricanteNeumatico.count();
    const modelosCount = await prisma.modeloNeumatico.count();
    console.log(`\n🏷️ CATÁLOGO:`);
    console.log(`   - ${fabricantesCount} Fabricantes`);
    console.log(`   - ${modelosCount} Modelos de neumáticos`);

    // 8. Eventos
    const eventosCount = await prisma.eventoNeumatico.count();
    const eventosTipo = await prisma.eventoNeumatico.groupBy({ by: ['tipo_evento'], _count: true });
    console.log(`\n📋 OPERACIONES REGISTRADAS (Total: ${eventosCount}):`);
    eventosTipo.forEach(e => console.log(`   - ${e.tipo_evento}: ${e._count}`));

    // 9. Alertas
    const alertasCount = await prisma.alerta.count();
    const alertasSeveridad = await prisma.alerta.groupBy({ by: ['severidad'], _count: true });
    console.log(`\n🚨 ALERTAS (Total: ${alertasCount}):`);
    alertasSeveridad.forEach(a => console.log(`   - ${a.severidad}: ${a._count}`));

    // 10. Configuraciones
    const configEjesCount = await prisma.configuracionEje.count();
    console.log(`\n⚙️ CONFIGURACIÓN TÉCNICA:`);
    console.log(`   - ${configEjesCount} Configuraciones de eje definidas`);
}

audit()
    .catch(e => console.error(e))
    .finally(async () => await prisma.$disconnect());
