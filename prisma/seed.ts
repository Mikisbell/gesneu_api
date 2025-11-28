import 'dotenv/config'
import { prisma } from '../src/lib/prisma'

async function main() {
    console.log('🌱 Iniciando seed...')

    // 1. Tipos de Vehículo
    const tiposVehiculo = [
        { nombre: 'Camión Carga Pesada', descripcion: 'Vehículos de carga > 10 ton' },
        { nombre: 'Camioneta', descripcion: 'Vehículos ligeros de carga' },
        { nombre: 'Autobús', descripcion: 'Transporte de personal' },
        { nombre: 'Tractocamión', descripcion: 'Cabezales para remolques' },
    ]

    for (const tipo of tiposVehiculo) {
        await prisma.tipoVehiculo.upsert({
            where: { nombre: tipo.nombre },
            update: {},
            create: tipo,
        })
    }
    console.log('✅ Tipos de Vehículo creados')

    // 2. Almacenes
    const almacenes = [
        { codigo: 'ALM-01', nombre: 'Almacén Central', ubicacion: 'Sede Principal' },
        { codigo: 'ALM-02', nombre: 'Taller Mecánico', ubicacion: 'Zona de Mantenimiento' },
        { codigo: 'ALM-03', nombre: 'Almacén Desechos', ubicacion: 'Zona de Reciclaje' },
    ]

    for (const alm of almacenes) {
        await prisma.almacen.upsert({
            where: { codigo: alm.codigo },
            update: {},
            create: alm,
        })
    }
    console.log('✅ Almacenes creados')

    // 3. Proveedores
    const proveedores = [
        { nombre: 'Michelin Perú', ruc: '20100123456', email: 'ventas@michelin.pe', tipo: 'FABRICANTE' as const },
        { nombre: 'Goodyear Tires', ruc: '20200987654', email: 'contacto@goodyear.com', tipo: 'FABRICANTE' as const },
        { nombre: 'Bridgestone Corp', ruc: '20300567890', email: 'soporte@bridgestone.com', tipo: 'FABRICANTE' as const },
    ]

    for (const prov of proveedores) {
        await prisma.proveedor.upsert({
            where: { ruc: prov.ruc },
            update: {},
            create: prov,
        })
    }
    console.log('✅ Proveedores creados')

    // 4. Fabricantes y Modelos
    const fabricante = await prisma.fabricanteNeumatico.upsert({
        where: { nombre: 'Michelin' },
        update: {},
        create: { nombre: 'Michelin', pais_origen: 'Francia' },
    })

    const modelos = [
        { nombre: 'X Multi Z', medida: '295/80R22.5', tipo_banda: 'Direccional', profundidad_nueva_mm: 18.5 },
        { nombre: 'X Works', medida: '11R22.5', tipo_banda: 'Tracción', profundidad_nueva_mm: 20.0 },
        { nombre: 'Agilis', medida: '205/75R16', tipo_banda: 'Toda Posición', profundidad_nueva_mm: 12.0 },
    ]

    for (const mod of modelos) {
        const existingModelo = await prisma.modeloNeumatico.findFirst({
            where: {
                nombre: mod.nombre,
                medida: mod.medida,
                fabricante_id: fabricante.id
            }
        })

        if (!existingModelo) {
            await prisma.modeloNeumatico.create({
                data: {
                    nombre: mod.nombre,
                    medida: mod.medida,
                    profundidad_inicial_mm: mod.profundidad_nueva_mm,
                    fabricante_id: fabricante.id,
                },
            })
        }
    }
    console.log('✅ Modelos creados')

    // 5. Vehículos (Necesitamos un tipo de vehículo)
    const tipoCamion = await prisma.tipoVehiculo.findFirst({ where: { nombre: 'Camión Carga Pesada' } })
    if (tipoCamion) {
        const vehiculos = [
            { placa: 'ABC-123', marca: 'Volvo', modelo: 'FH16', anio: 2022, kilometraje_actual: 45000 },
            { placa: 'XYZ-789', marca: 'Scania', modelo: 'R500', anio: 2023, kilometraje_actual: 12000 },
            { placa: 'DEF-456', marca: 'Mercedes', modelo: 'Actros', anio: 2021, kilometraje_actual: 89000 },
        ]

        for (const v of vehiculos) {
            await prisma.vehiculo.upsert({
                where: { placa: v.placa },
                update: {},
                create: {
                    ...v,
                    tipo_vehiculo_id: tipoCamion.id,
                },
            })
        }
        console.log('✅ Vehículos creados')
    }

    console.log('🏁 Seed completado exitosamente')
}

main()
    .catch((e) => {
        console.error(e)
        process.exit(1)
    })
    .finally(async () => {
        await prisma.$disconnect()
    })
