import 'dotenv/config'
import { PrismaClient, EstadoNeumaticoEnum } from '@prisma/client'
import { PrismaPg } from '@prisma/adapter-pg'
import { Pool } from 'pg'

const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: false,
})
const adapter = new PrismaPg(pool)
const prisma = new PrismaClient({ adapter })

async function seedStandaloneInventory() {
    console.log('📦 Seeding physical tire inventory (Neumaticos)...')

    // Find or create default Empresa
    let empresa = await prisma.empresa.findFirst()
    if (!empresa) {
        empresa = await prisma.empresa.create({
            data: {
                nombre: 'TRANSPORTE PESADO SOLUCIONES S.A.C.',
                ruc: '20601234567',
            }
        })
    }

    // Find or create default Almacen
    let almacen = await prisma.almacen.findFirst({ where: { empresa_id: empresa.id } })
    if (!almacen) {
        almacen = await prisma.almacen.create({
            data: {
                nombre: 'Almacén Central Lurin',
                codigo: 'ALM-LURIN',
                empresa_id: empresa.id
            }
        })
    }

    // Find all available models
    const modelos = await prisma.modeloNeumatico.findMany({
        include: { fabricante: true }
    })

    if (modelos.length === 0) {
        console.error('❌ No models found in database. Run seed-models first!')
        process.exit(1)
    }

    console.log(`Found ${modelos.length} tire models in database. Creating physical tires...`)

    let createdCount = 0

    // Seed 15 sample physical tires across different models
    for (let i = 1; i <= 15; i++) {
        const modelo = modelos[i % modelos.length]
        const origDepth = Number(modelo.profundidad_original_mm) || 16.0
        const isStock = i % 3 !== 0
        const estado = isStock ? EstadoNeumaticoEnum.EN_STOCK : EstadoNeumaticoEnum.EN_REENCAUCHE
        const remanente = isStock ? origDepth : Number((origDepth * 0.4).toFixed(1))

        const serie = `${modelo.fabricante.codigo_abreviado || 'NEU'}-${202600 + i}`

        const existing = await prisma.neumatico.findFirst({
            where: { numero_serie: serie }
        })

        if (!existing) {
            await prisma.neumatico.create({
                data: {
                    numero_serie: serie,
                    modelo_id: modelo.id,
                    dot: `242${(i % 4) + 1}`,
                    estado_actual: estado,
                    profundidad_inicial_mm: origDepth,
                    profundidad_remanente_actual_mm: remanente,
                    presion_actual_psi: Number(modelo.presion_recomendada_psi) || 110,
                    costo_compra: 480 + (i * 15),
                    moneda_compra: 'PEN',
                    fecha_compra: new Date(Date.now() - (i * 86400000 * 5)),
                    ubicacion_almacen_id: isStock ? almacen.id : null,
                    empresa_id: empresa.id,
                    version: 0
                }
            })
            createdCount++
        }
    }

    console.log(`✅ Successfully created ${createdCount} physical tires in inventory!`)
}

seedStandaloneInventory()
    .then(() => process.exit(0))
    .catch((err) => {
        console.error('❌ Error seeding inventory:', err)
        process.exit(1)
    })
