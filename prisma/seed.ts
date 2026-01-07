import 'dotenv/config';
import { PrismaClient } from '@prisma/client';
import { PrismaPg } from '@prisma/adapter-pg';
import { Pool } from 'pg';
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

const connectionString = process.env.DATABASE_URL;
const pool = new Pool({
    connectionString,
    ssl: connectionString?.includes('localhost') ? false : { rejectUnauthorized: false },
});
const adapter = new PrismaPg(pool);
const prisma = new PrismaClient({ adapter });

async function main() {
    console.log('🌱 Iniciando carga de datos COMPLETA para GesNeu...');

    // --- 0. EMPRESA TENANT (NEW) ---
    const empresa = await prisma.empresa.upsert({
        where: { ruc: '20600112233' },
        update: {},
        create: {
            nombre: 'ECOSEM HUARAUCACA',
            ruc: '20600112233',
            direccion: 'Pasco, Peru',
            activo: true
        }
    });

    // --- 0.5 USUARIOS ---
    const passwordHash = await bcrypt.hash('123456', 10);

    const admin = await prisma.usuario.upsert({
        where: { username: 'admin' },
        update: { empresa_id: empresa.id },
        create: {
            username: 'admin',
            email: 'admin@gesneu.com',
            nombre_completo: 'Administrador Sistema',
            password_hash: passwordHash,
            rol: RolEnum.ADMIN,
            empresa_id: empresa.id // Tenant Admin
        }
    });
    // ... (repetir empresa_id para otros usuarios) ...

    const gestor = await prisma.usuario.upsert({
        where: { username: 'gestor' },
        update: { empresa_id: empresa.id },
        create: {
            username: 'gestor',
            email: 'gestor@gesneu.com',
            nombre_completo: 'Juan Perez (Gestor)',
            password_hash: passwordHash,
            rol: RolEnum.GESTOR,
            empresa_id: empresa.id
        }
    });

    const operador = await prisma.usuario.upsert({
        where: { username: 'operador' },
        update: { empresa_id: empresa.id },
        create: {
            username: 'operador',
            email: 'operador@gesneu.com',
            nombre_completo: 'Carlos Operador',
            password_hash: passwordHash,
            rol: RolEnum.OPERADOR,
            empresa_id: empresa.id
        }
    });

    console.log('✅ Usuarios y Tenant creados');

    // ... (Centros de costo) ...

    // --- 2. ALMACENES ---
    const almacenPrincipal = await prisma.almacen.upsert({
        where: { codigo: 'ALM-CEN' },
        update: { empresa_id: empresa.id },
        create: {
            codigo: 'ALM-CEN',
            nombre: 'ALMACEN CENTRAL',
            tipo: 'PRINCIPAL',
            direccion: 'Base Central',
            empresa_id: empresa.id
        }
    });

    const almacenScrap = await prisma.almacen.upsert({
        where: { codigo: 'ALM-DES' },
        update: { empresa_id: empresa.id },
        create: {
            codigo: 'ALM-DES',
            nombre: 'AREA DE DESECHOS',
            tipo: 'SCRAP',
            direccion: 'Patio Trasero',
            empresa_id: empresa.id
        }
    });

    // --- 3. PROVEEDORES ---
    await prisma.proveedor.upsert({
        where: { ruc: '20100070970' },
        update: { empresa_id: empresa.id },
        create: {
            nombre: 'GOODYEAR PERU S.A.',
            ruc: '20100070970',
            tipo: TipoProveedorEnum.FABRICANTE,
            empresa_id: empresa.id
        }
    });
    // ...

    // --- 1. CENTROS DE COSTO (Restaurado) ---
    const cecoTransporte = await prisma.centroCosto.upsert({ where: { codigo: '650101' }, update: {}, create: { codigo: '650101', nombre: 'TRANSPORTE', area_negocio: 'TRANSPORTE' } });

    // --- 4. MOTIVOS DESECHO ---
    await prisma.motivoDesecho.upsert({ where: { codigo: 'DN-001' }, update: {}, create: { codigo: 'DN-001', nombre: 'DESGASTE NATURAL', descripcion: 'Llegó al límite' } });
    await prisma.motivoDesecho.upsert({ where: { codigo: 'CL-001' }, update: {}, create: { codigo: 'CL-001', nombre: 'CORTE LATERAL', descripcion: 'Daño irreparable', requiere_evidencia: true } });

    // --- 5. TIPOS DE VEHICULO Y CONFIGURACIONES ---
    const tipoTracto = await prisma.tipoVehiculo.upsert({ where: { nombre: 'TRACTO 6X4' }, update: {}, create: { nombre: 'TRACTO 6X4', descripcion: 'Tracto camión Volvo/Scania' } });

    const countEjes = await prisma.configuracionEje.count({ where: { tipo_vehiculo_id: tipoTracto.id } });
    if (countEjes === 0) {
        const eje1 = await prisma.configuracionEje.create({
            data: { tipo_vehiculo_id: tipoTracto.id, numero_eje: 1, tipo_eje: TipoEjeEnum.DIRECCION, nombre_eje: 'Direccional', numero_posiciones: 2, permite_reencauchados: false }
        });
        await prisma.posicionNeumatico.create({ data: { configuracion_eje_id: eje1.id, codigo_posicion: '1I', lado: LadoVehiculoEnum.IZQUIERDO, posicion_relativa: 1, es_direccion: true } });
        await prisma.posicionNeumatico.create({ data: { configuracion_eje_id: eje1.id, codigo_posicion: '1D', lado: LadoVehiculoEnum.DERECHO, posicion_relativa: 1, es_direccion: true } });

        const eje2 = await prisma.configuracionEje.create({
            data: { tipo_vehiculo_id: tipoTracto.id, numero_eje: 2, tipo_eje: TipoEjeEnum.TRACCION, nombre_eje: 'Tracción 1', numero_posiciones: 4, posiciones_duales: true }
        });
        // Posiciones Tracción simplificado
        await prisma.posicionNeumatico.create({ data: { configuracion_eje_id: eje2.id, codigo_posicion: '2EI', lado: LadoVehiculoEnum.IZQUIERDO, posicion_relativa: 1, es_traccion: true, es_interna: true } });
        await prisma.posicionNeumatico.create({ data: { configuracion_eje_id: eje2.id, codigo_posicion: '2EE', lado: LadoVehiculoEnum.IZQUIERDO, posicion_relativa: 1, es_traccion: true } });
        await prisma.posicionNeumatico.create({ data: { configuracion_eje_id: eje2.id, codigo_posicion: '2DI', lado: LadoVehiculoEnum.DERECHO, posicion_relativa: 1, es_traccion: true, es_interna: true } });
        await prisma.posicionNeumatico.create({ data: { configuracion_eje_id: eje2.id, codigo_posicion: '2DE', lado: LadoVehiculoEnum.DERECHO, posicion_relativa: 1, es_traccion: true } });
    }

    const configEje1 = await prisma.configuracionEje.findUnique({ where: { tipo_vehiculo_id_numero_eje: { tipo_vehiculo_id: tipoTracto.id, numero_eje: 1 } }, include: { posiciones: true } });
    const pos1Izq = configEje1?.posiciones.find(p => p.codigo_posicion === '1I');
    const pos1Der = configEje1?.posiciones.find(p => p.codigo_posicion === '1D');

    if (!pos1Izq) throw new Error("Error en seed configuraciones");

    // --- 7. FABRICANTES Y MODELOS (Restaurado) ---
    const fabGoodyear = await prisma.fabricanteNeumatico.upsert({ where: { codigo_abreviado: 'GY' }, update: {}, create: { nombre: 'GOODYEAR', codigo_abreviado: 'GY' } });

    const modKmaxS = await prisma.modeloNeumatico.upsert({
        where: { fabricante_id_nombre_modelo_medida: { fabricante_id: fabGoodyear.id, nombre_modelo: 'KMAX S', medida: '295/80R22.5' } },
        update: {},
        create: {
            nombre_modelo: 'KMAX S',
            medida: '295/80R22.5',
            profundidad_original_mm: 15.8,
            profundidad_minima_retiro_mm: 3.0,
            fabricante_id: fabGoodyear.id,
            reencauches_maximos: 2,
            indice_carga: '152', indice_velocidad: 'M'
        }
    });

    // --- 6. VEHICULOS ---
    const v1 = await prisma.vehiculo.upsert({
        where: { numero_economico: 'TC-100' },
        update: { empresa_id: empresa.id },
        create: {
            numero_economico: 'TC-100',
            placa: 'F8U-901',
            tipo_vehiculo_id: tipoTracto.id,
            marca: 'VOLVO',
            modelo_vehiculo: 'FH 440',
            anio_fabricacion: 2014,
            tipo_medicion: TipoMedicionEnum.KILOMETRAJE,
            odometro_actual: 672491,
            centro_costo_id: cecoTransporte.id,
            empresa_id: empresa.id,
            version: 0
        }
    });

    // ... (Fab, Modelo) ...

    // --- 8. NEUMATICOS ---
    for (let i = 1; i <= 10; i++) {
        await prisma.neumatico.create({
            data: {
                numero_serie: `NEW-${1000 + i}`,
                modelo_id: modKmaxS.id,
                dot: '2024',
                estado_actual: EstadoNeumaticoEnum.EN_STOCK,
                profundidad_inicial_mm: 15.8,
                profundidad_remanente_actual_mm: 15.8,
                ubicacion_almacen_id: almacenPrincipal.id,
                costo_compra: 450.00,
                fecha_compra: new Date(),
                empresa_id: empresa.id, // Tenant
                version: 0
            }
        });
    }

    // Montados
    await prisma.neumatico.create({
        data: {
            numero_serie: `MNT-001`,
            modelo_id: modKmaxS.id,
            dot: '1923',
            estado_actual: EstadoNeumaticoEnum.INSTALADO,
            profundidad_inicial_mm: 15.8,
            profundidad_remanente_actual_mm: 12.5,
            ubicacion_vehiculo_id: v1.id,
            ubicacion_posicion_id: pos1Izq.id,
            kilometraje_acumulado: 35000,
            fecha_compra: new Date(),
            costo_compra: 400,
            empresa_id: empresa.id,
            version: 0
        }
    });

    console.log('✅ Seed Base Completado.');
}

main().catch(console.error).finally(() => prisma.$disconnect());
