
const autocannon = require('autocannon');
const { v4: uuidv4 } = require('uuid');

// Database Setup for Valid IDs
const { PrismaClient } = require('@prisma/client');
const { PrismaPg } = require('@prisma/adapter-pg');
const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: { rejectUnauthorized: false },
    max: 5 // Limit script DB connections
});
const adapter = new PrismaPg(pool);
const prisma = new PrismaClient({ adapter });

// Configuration
const BASE_URL = process.env.BASE_URL || 'http://localhost:3005';
const API_URL = `${BASE_URL}/api/v1`;

const DURATION = parseInt(process.env.STRESS_DURATION || '30');
const CONNECTIONS = parseInt(process.env.STRESS_CONCURRENCY || '5');

let VALID_DATA = {
    modelo_id: null,
    proveedor_id: null,
    almacen_id: null,
    neumatico_id: null
};

// Credentials
const USER_CREDENTIALS = {
    identifier: process.env.STRESS_USER || "admin",
    password: process.env.STRESS_PASSWORD || "admin123"
};

async function loginAndGetCookie() {
    console.log('🔐 Authenticating as real user...');

    // 1. CSRF
    const csrfRes = await fetch(`${BASE_URL}/api/auth/csrf`);
    const csrfData = await csrfRes.json();
    const csrfToken = csrfData.csrfToken;
    let cookies = csrfRes.headers.get('set-cookie');

    // 2. Login
    const formData = new URLSearchParams();
    formData.append('identifier', USER_CREDENTIALS.identifier);
    formData.append('password', USER_CREDENTIALS.password);
    formData.append('csrfToken', csrfToken);
    formData.append('callbackUrl', BASE_URL);
    formData.append('json', 'true');

    const loginRes = await fetch(`${BASE_URL}/api/auth/callback/credentials`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': cookies
        },
        body: formData,
        redirect: 'manual'
    });

    if (loginRes.status !== 200 && loginRes.status !== 302) {
        console.error('Login Failed:', await loginRes.text());
        process.exit(1);
    }

    // 3. Extract Session Token
    const loginCookies = loginRes.headers.get('set-cookie');
    if (!loginCookies) {
        console.error('No session cookies received!');
        process.exit(1);
    }

    const cleanCookie = loginCookies.split(',')
        .map(c => c.split(';')[0].trim())
        .filter(c => !c.match(/^(Path|Expires|HttpOnly|Secure|SameSite|Priority|Domain)=/i))
        .join('; ');

    console.log('✅ Authentication Successful.');
    return [cookies, cleanCookie].join('; ');
}

// Helper: Ensure valid data exists
async function fetchValidIds() {
    console.log('🔍 Fetching valid IDs from DB...');
    try {
        const modelo = await prisma.modeloNeumatico.findFirst() || await prisma.modeloNeumatico.create({
            data: {
                nombre: 'Modelo Stress Test',
                marca: { connectOrCreate: { where: { nombre: 'StressBrand' }, create: { nombre: 'StressBrand' } } },
                medida: '295/80R22.5',
                indice_carga: '152/148',
                indice_velocidad: 'M',
                tipo: 'RADIAL',
                eje_recomendado: 'DIRECCIONAL',
                presion_recomendada_psi: 120,
                profundidad_arquitectura_mm: 22
            }
        });

        const proveedor = await prisma.proveedor.findFirst() || await prisma.proveedor.create({
            data: { nombre: 'Proveedor Stress', ruc: '20100000001', tipo: 'EXTERNO' }
        });

        const almacen = await prisma.almacen.findFirst() || await prisma.almacen.create({
            data: { nombre: 'Almacen Stress', tipo: 'CENTRAL' }
        });

        // Ensure a neumatico exists for event testing
        const user = await prisma.usuario.findUnique({ where: { username: USER_CREDENTIALS.identifier } });
        const neumatico = await prisma.neumatico.findFirst() || await prisma.neumatico.create({
            data: {
                modelo_id: modelo.id,
                proveedor_compra_id: proveedor.id,
                ubicacion_almacen_id: almacen.id,
                estado_actual: 'EN_STOCK',
                profundidad_remanente_actual_mm: 15,
                kilometraje_acumulado: 0,
                horas_acumuladas: 0,
                costo_compra: 100,
                moneda_compra: 'USD',
                numero_serie: `ADV-TEST-${Date.now()}`,
                empresa_id: user.empresa_id,
                profundidad_inicial_mm: 20,
                vida_actual: 1,
                reencauches_realizados: 0,
                activo: true,
                fecha_compra: new Date(),
                fecha_fabricacion: new Date()
            }
        });

        VALID_DATA = { modelo_id: modelo.id, proveedor_id: proveedor.id, almacen_id: almacen.id, neumatico_id: neumatico.id };
        console.log('✅ IDs Loaded');
    } catch (e) {
        console.error('Error fetching/creating IDs:', e);
        process.exit(1);
    }
}

// Advanced Payload: Inspeccion (Read/Write intensive but safe)
const generateInspectPayload = () => ({
    tipo_evento: 'INSPECCION',
    neumatico_id: VALID_DATA.neumatico_id,
    fecha_evento: new Date().toISOString(),
    profundidad_remanente: 10 + Math.random() * 5,
    presion_psi: 100 + Math.random() * 10,
    kilometraje_acumulado: 1000 + Math.random() * 100
});

async function runAuthenticatedStressTest() {
    await fetchValidIds();
    const sessionCookie = await loginAndGetCookie();

    console.log('🚀 Starting ADVANCED Authenticated Stress Test...');

    const instance = autocannon({
        url: `${API_URL}/neumaticos/eventos`,
        connections: CONNECTIONS,
        duration: DURATION,
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Cookie': sessionCookie
        },
        requests: [
            {
                method: 'POST',
                path: '/api/v1/neumaticos/eventos',
                setupRequest: (req) => {
                    req.body = JSON.stringify(generateInspectPayload());
                    return req;
                }
            }
        ]
    });

    autocannon.track(instance, { renderProgressBar: true });

    instance.on('done', (result) => {
        console.log('\n✅ Advanced Stress Test Completed');
        console.log(`Duration: ${result.duration}s`);
        console.log(`Requests: ${result.requests.total}`);
        console.log(`Latency (avg): ${result.latency.average} ms`);
        console.log(`2xx: ${result['2xx']} | 4xx: ${result['4xx']} | 5xx: ${result['5xx']}`);
    });
}

if (require.main === module) {
    runAuthenticatedStressTest();
}
