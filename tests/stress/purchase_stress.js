
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
    almacen_id: null
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
        redirect: 'manual' // 🚨 Stop fetch from following redirect to capture the Set-Cookie
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

        VALID_DATA = { modelo_id: modelo.id, proveedor_id: proveedor.id, almacen_id: almacen.id };
        console.log('✅ IDs Loaded');
    } catch (e) {
        console.error('Error fetching/creating IDs:', e);
        process.exit(1);
    }
}

const generatePurchasePayload = () => {
    const depth = 20 + Math.random() * 2;
    return {
        modelo_id: VALID_DATA.modelo_id,
        proveedor_compra_id: VALID_DATA.proveedor_id,
        ubicacion_almacen_id: VALID_DATA.almacen_id,
        numero_serie: `PURCHASE-${uuidv4().substring(0, 8)}`,
        dot: '2425',
        profundidad_inicial_mm: depth,
        profundidad_actual_mm: depth,
        costo_compra: 200 + Math.random() * 50,
        fecha_compra: new Date().toISOString(),
        es_reencauchado: false,
        moneda_compra: 'PEN'
    };
};

async function runTest() {
    await fetchValidIds();
    const sessionCookie = await loginAndGetCookie();

    console.log('🚀 Starting PURCHASE Stress Test (Creating Neumaticos)...');
    const instance = autocannon({
        url: `${API_URL}/neumaticos`,
        connections: CONNECTIONS,
        duration: DURATION,
        method: 'POST',
        headers: { 'Cookie': sessionCookie, 'Content-Type': 'application/json' },
        requests: [
            {
                method: 'POST',
                path: '/api/v1/neumaticos',
                setupRequest: (req) => {
                    req.body = JSON.stringify(generatePurchasePayload());
                    return req;
                }
            }
        ]
    });

    autocannon.track(instance, { renderProgressBar: true });

    instance.on('done', (result) => {
        console.log('\n✅ Purchase Verification Complete');
        console.log('---------------------------------');
        console.log(`Duration: ${result.duration}s`);
        console.log(`Requests: ${result.requests.total}`);
        console.log(`Latency (avg): ${result.latency.average} ms`);
        console.log(`2xx: ${result['2xx']} | 4xx: ${result['4xx']} | 5xx: ${result['5xx']}`);
    });
}

runTest();
