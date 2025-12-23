import 'dotenv/config'
import { PrismaClient } from '@prisma/client';

// Use simple PrismaClient without pg adapter for seed (works in CI without SSL)
const prisma = new PrismaClient();
import {
    TipoMedicionEnum,
    TipoEventoNeumaticoEnum,
    EstadoNeumaticoEnum,
    RolEnum,
    TipoEjeEnum,
    LadoVehiculoEnum,
    TipoProveedorEnum
} from '@prisma/client';
import bcrypt from 'bcryptjs';

async function main() {
    console.log('🌱 Iniciando carga de datos COMPLETA para GesNeu...');

    // --- 0. USUARIOS ---
    const passwordHash = await bcrypt.hash('123456', 10);

    const admin = await prisma.usuario.upsert({
        where: { username: 'admin' },
        update: {},
        create: {
            username: 'admin',
            email: 'admin@gesneu.com',
            nombre_completo: 'Administrador Sistema',
            password_hash: passwordHash,
            rol: RolEnum.ADMIN
        }
    });

    const gestor = await prisma.usuario.upsert({
        where: { username: 'gestor' },
        update: {},
        create: {
            username: 'gestor',
            email: 'gestor@gesneu.com',
            nombre_completo: 'Juan Perez (Gestor)',
            password_hash: passwordHash,
            rol: RolEnum.GESTOR
        }
    });

    const operador = await prisma.usuario.upsert({
        where: { username: 'operador' },
        update: {},
        create: {
            username: 'operador',
            email: 'operador@gesneu.com',
            nombre_completo: 'Carlos Operador',
            password_hash: passwordHash,
            rol: RolEnum.OPERADOR
        }
    });

    console.log('✅ Usuarios creados/verificados');

    // --- 1. CENTROS DE COSTO ---
    const cecoTransporte = await prisma.centroCosto.upsert({
        where: { codigo: '650101' },
        update: {},
        create: { codigo: '650101', nombre: 'TRANSPORTE COMERCIAL Y DE MERCANCIAS', area_negocio: 'TRANSPORTE COMERCIAL' }
    });

    const cecoTaller = await prisma.centroCosto.upsert({
        where: { codigo: '640304' },
        update: {},
        create: { codigo: '640304', nombre: 'TALLER TRANSPORTES', area_negocio: 'MANTENIMIENTO' }
    });

    // --- 2. ALMACENES ---
    const almacenPrincipal = await prisma.almacen.create({
        data: { nombre: 'ALMACEN CENTRAL', tipo: 'PRINCIPAL', ubicacion: 'Base Central' }
    });

    const almacenScrap = await prisma.almacen.create({
        data: { nombre: 'AREA DE DESECHOS', tipo: 'SCRAP', ubicacion: 'Patio Trasero' }
    });

    // Usamos create en lugar de upsert para almacenes si no tienen ID unico natural, 
    // pero para seed idempotente mejor buscar primero o borrar todo. 
    // Por simplicidad en este MVP seed, asumiremos que si corre dos veces duplicará almacenes 
    // a menos que pongamos lógica extra. Para E2E limpio, resetear DB es mejor.

    // --- 3. PROVEEDORES ---
    const provGoodyear = await prisma.proveedor.upsert({
        where: { ruc: '20100070970' },
        update: {},
        create: { nombre: 'GOODYEAR PERU S.A.', ruc: '20100070970', tipo: TipoProveedorEnum.FABRICANTE }
    });

    const provReencauche = await prisma.proveedor.upsert({
        where: { ruc: '20456789012' },
        update: {},
        create: { nombre: 'REENCAUCHADORA DEL SUR', ruc: '20456789012', tipo: TipoProveedorEnum.SERVICIO_REENCAUCHE }
    });

    // --- 4. MOTIVOS DESECHO ---
    await prisma.motivoDesecho.upsert({
        where: { nombre: 'DESGASTE NATURAL' },
        update: {},
        create: { nombre: 'DESGASTE NATURAL', descripcion: 'Llegó al límite de profundidad' }
    });

    await prisma.motivoDesecho.upsert({
        where: { nombre: 'CORTE LATERAL' },
        update: {},
        create: { nombre: 'CORTE LATERAL', descripcion: 'Daño irreparable en flanco', requiere_evidencia: true }
    });

    // --- 5. TIPOS DE VEHICULO Y CONFIGURACIONES ---
    const tipoTracto = await prisma.tipoVehiculo.upsert({
        where: { nombre: 'TRACTO 6X4' },
        update: {},
        create: { nombre: 'TRACTO 6X4', descripcion: 'Tracto camión Volvo/Scania' }
    });

    // Configuración 6x4 (Eje 1: Direccional, Eje 2: Tracción, Eje 3: Tracción)
    const eje1Tracto = await prisma.configuracionEje.create({
        data: {
            tipo_vehiculo_id: tipoTracto.id,
            numero_eje: 1,
            tipo_eje: TipoEjeEnum.DIRECCION,
            posiciones_neumatico: 2,
            permite_reencauchados: false
        }
    });

    const eje2Tracto = await prisma.configuracionEje.create({
        data: {
            tipo_vehiculo_id: tipoTracto.id,
            numero_eje: 2,
            tipo_eje: TipoEjeEnum.TRACCION,
            posiciones_neumatico: 4,
            permite_reencauchados: true
        }
    });

    // Posiciones Eje 1
    const pos1Izq = await prisma.posicionNeumatico.create({ data: { configuracion_eje_id: eje1Tracto.id, numero_posicion: 1, lado_vehiculo: LadoVehiculoEnum.IZQUIERDO } });
    const pos1Der = await prisma.posicionNeumatico.create({ data: { configuracion_eje_id: eje1Tracto.id, numero_posicion: 2, lado_vehiculo: LadoVehiculoEnum.DERECHO } });

    // ... (Simplificando: solo creamos algunas posiciones claves para tests)

    const tipoVolquete = await prisma.tipoVehiculo.upsert({
        where: { nombre: 'VOLQUETE' },
        update: {},
        create: { nombre: 'VOLQUETE', descripcion: 'Volquete Volvo FMX' }
    });

    // --- 6. VEHICULOS ---
    const v1 = await prisma.vehiculo.upsert({
        where: { codigo_interno: 'TC-100' },
        update: {},
        create: {
            codigo_interno: 'TC-100',
            placa: 'F8U-901',
            tipo_vehiculo_id: tipoTracto.id,
            marca: 'VOLVO',
            modelo: 'FH 440',
            anio: 2014,
            tipo_medicion: TipoMedicionEnum.KILOMETRAJE,
            contador_actual: 672491.5,
            centro_costo_id: cecoTransporte.id
        }
    });

    // --- 7. FABRICANTES Y MODELOS ---
    const fabGoodyear = await prisma.fabricanteNeumatico.upsert({
        where: { nombre: 'GOODYEAR' },
        update: {},
        create: { nombre: 'GOODYEAR' }
    });

    const modKmaxS = await prisma.modeloNeumatico.upsert({
        where: { id: '00000000-0000-0000-0000-000000000001' },
        update: {},
        create: {
            id: '00000000-0000-0000-0000-000000000001',
            nombre: 'KMAX S',
            medida: '295/80R22.5',
            profundidad_inicial_mm: 15.8,
            fabricante_id: fabGoodyear.id,
            reencauches_maximos: 2
        }
    });

    // --- 8. NEUMATICOS (INVENTARIO Y MONTADOS) ---

    // 10 En Stock (Nuevos)
    for (let i = 1; i <= 10; i++) {
        await prisma.neumatico.create({
            data: {
                numero_serie: `NEW-${1000 + i}`,
                modelo_id: modKmaxS.id,
                dot: '2024',
                estado_actual: EstadoNeumaticoEnum.EN_STOCK,
                profundidad_inicial_mm: 15.8,
                profundidad_actual_mm: 15.8,
                ubicacion_almacen_id: almacenPrincipal.id,
                costo_compra: 450.00,
                fecha_compra: new Date()
            }
        });
    }

    // 2 Montados en TC-100 (Eje 1)
    await prisma.neumatico.create({
        data: {
            numero_serie: `MNT-001`,
            modelo_id: modKmaxS.id,
            dot: '1923',
            estado_actual: EstadoNeumaticoEnum.INSTALADO,
            profundidad_inicial_mm: 15.8,
            profundidad_actual_mm: 12.5,
            ubicacion_vehiculo_id: v1.id,
            ubicacion_posicion_id: pos1Izq.id,
            kilometraje_acumulado: 35000
        }
    });

    await prisma.neumatico.create({
        data: {
            numero_serie: `MNT-002`,
            modelo_id: modKmaxS.id,
            dot: '1923',
            estado_actual: EstadoNeumaticoEnum.INSTALADO,
            profundidad_inicial_mm: 15.8,
            profundidad_actual_mm: 12.4,
            ubicacion_vehiculo_id: v1.id,
            ubicacion_posicion_id: pos1Der.id,
            kilometraje_acumulado: 35000
        }
    });

    // 2 Scrap
    await prisma.neumatico.create({
        data: {
            numero_serie: `SCR-999`,
            modelo_id: modKmaxS.id,
            dot: '1020',
            estado_actual: EstadoNeumaticoEnum.DESECHADO,
            profundidad_inicial_mm: 15.8,
            profundidad_actual_mm: 2.0,
            ubicacion_almacen_id: almacenScrap.id,
            kilometraje_acumulado: 120000
        }
    });

    console.log('✅ Datos reales de ECOSEM + Datos base cargados exitosamente.');
}

main()
    .catch((e) => {
        console.error(e);
        process.exit(1);
    })
    .finally(async () => {
        await prisma.$disconnect();
    });
