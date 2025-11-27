import { PrismaClient } from '@prisma/client';
import * as bcrypt from 'bcryptjs';

const prisma = new PrismaClient();

async function main() {
    console.log('🌱 Iniciando Seed de Base de Datos...');

    // 1. ROLES Y PERMISOS
    console.log('... Creando Roles');
    const roles = [
        { nombre: 'ADMINISTRADOR', descripcion: 'Acceso total al sistema' },
        { nombre: 'GESTOR', descripcion: 'Gestión de flota y neumáticos' },
        { nombre: 'OPERADOR', descripcion: 'Registro de operaciones y mediciones' },
        { nombre: 'CONSULTOR', descripcion: 'Solo lectura de reportes' },
    ];

    const rolesMap = new Map();
    for (const rol of roles) {
        const created = await prisma.rol.upsert({
            where: { nombre: rol.nombre },
            update: {},
            create: rol,
        });
        rolesMap.set(rol.nombre, created.id);
    }

    // 2. USUARIO ADMIN
    console.log('... Creando Usuario Admin');
    const adminPassword = await bcrypt.hash('admin123', 10);
    const admin = await prisma.usuario.upsert({
        where: { username: 'admin' },
        update: {},
        create: {
            username: 'admin',
            email: 'admin@gesneu.com',
            nombre_completo: 'Administrador del Sistema',
            password_hash: adminPassword,
            activo: true,
        },
    });

    // Asignar rol Admin
    await prisma.usuarioRol.createMany({
        data: [{ usuario_id: admin.id, rol_id: rolesMap.get('ADMINISTRADOR') }],
        skipDuplicates: true,
    });

    // 3. CATÁLOGOS BASE
    console.log('... Creando Catálogos Base');

    // Fabricantes
    const fabricantes = [
        { nombre: 'Michelin', pais_origen: 'Francia' },
        { nombre: 'Bridgestone', pais_origen: 'Japón' },
        { nombre: 'Goodyear', pais_origen: 'USA' },
        { nombre: 'Continental', pais_origen: 'Alemania' },
        { nombre: 'Pirelli', pais_origen: 'Italia' },
    ];

    for (const fab of fabricantes) {
        await prisma.fabricanteNeumatico.upsert({
            where: { nombre: fab.nombre },
            update: {},
            create: {
                nombre: fab.nombre,
                pais_origen: fab.pais_origen
            },
        });
    }

    // Proveedores
    // Upsert para evitar error si ya existe
    const existingProveedor = await prisma.proveedor.findFirst({ where: { ruc: '20123456789' } });
    if (!existingProveedor) {
        await prisma.proveedor.create({
            data: {
                nombre: 'Distribuidora Central de Llantas S.A.',
                ruc: '20123456789',
                tipo: 'DISTRIBUIDOR',
                activo: true,
            }
        });
    }

    // Almacenes
    const existingAlmacen = await prisma.almacen.findFirst({ where: { codigo: 'ALM-MAIN' } });
    if (!existingAlmacen) {
        await prisma.almacen.create({
            data: {
                nombre: 'Almacén Principal',
                codigo: 'ALM-MAIN',
                ubicacion: 'Sede Central - Zona A',
                activo: true,
            }
        });
    }

    // 4. TIPOS DE VEHÍCULO
    console.log('... Creando Tipos de Vehículo');
    const tiposVehiculo = [
        { nombre: 'Tractocamión 6x4', codigo: 'T3-S3', ejes: 3, neumaticos: 10 },
        { nombre: 'Bus Interprovincial 6x2', codigo: 'BUS-6X2', ejes: 3, neumaticos: 8 },
        { nombre: 'Camión Rígido 4x2', codigo: 'C2', ejes: 2, neumaticos: 6 },
        { nombre: 'Semirremolque 3 Ejes', codigo: 'S3', ejes: 3, neumaticos: 12 },
    ];

    for (const tipo of tiposVehiculo) {
        await prisma.tipoVehiculo.upsert({
            where: { nombre: tipo.nombre },
            update: {},
            create: {
                nombre: tipo.nombre,
                descripcion: `Vehículo tipo ${tipo.nombre} (${tipo.ejes} ejes, ${tipo.neumaticos} neumáticos)`,
            },
        });
    }

    console.log('✅ Seed completado exitosamente');
}

main()
    .catch((e) => {
        console.error(e);
        process.exit(1);
    })
    .finally(async () => {
        await prisma.$disconnect();
    });
