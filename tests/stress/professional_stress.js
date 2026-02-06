
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
const AUTH_URL = `${BASE_URL}/api/auth/callback/credentials`; // NextAuth default handler

const DURATION = parseInt(process.env.STRESS_DURATION || '20');
const CONNECTIONS = parseInt(process.env.STRESS_CONCURRENCY || '5');

let VALID_DATA = {
    modelo_id: null,
    proveedor_id: null,
    almacen_id: null
};

// Credentials for a REAL user in your DB
const USER_CREDENTIALS = {
    csrfToken: "", // We might need to fetch this first if NextAuth requires it
    identifier: process.env.STRESS_USER || "admin", // Default user
    password: process.env.STRESS_PASSWORD || "admin123", // Default password
    json: true
};

async function loginAndGetCookie() {
    console.log('🔐 Authenticating as real user...');

    // 1. Fetch CSRF Token (Required by NextAuth)
    const csrfRes = await fetch(`${BASE_URL}/api/auth/csrf`);
    const csrfData = await csrfRes.json();
    const csrfToken = csrfData.csrfToken;
    let cookies = csrfRes.headers.get('set-cookie');

    // 2. Perform Login
    // NextAuth Credentials provider expects a POST form-data or JSON depending on config.
    // Usually it's x-www-form-urlencoded
    const params = new URLSearchParams();
    params.append('identifier', USER_CREDENTIALS.identifier);
    params.append('password', USER_CREDENTIALS.password);
    params.append('csrfToken', csrfToken);
    params.append('json', 'true');

    const loginRes = await fetch(AUTH_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': cookies // Pass CSRF cookie
        },
        body: params,
        redirect: 'manual' // 🚨 Stop fetch from following redirect to capture the Set-Cookie
    });

    console.log(`Login Status: ${loginRes.status}`);

    if (!loginRes.ok && loginRes.status !== 302 && loginRes.status !== 303) {
        const text = await loginRes.text();
        throw new Error(`Login Failed: ${loginRes.status} ${loginRes.statusText} - ${text}`);
    }

    console.log('Login Response Headers:', Array.from(loginRes.headers.entries()));
    const rawCookies = loginRes.headers.get('set-cookie');
    if (!rawCookies) throw new Error('No cookies received after login');

    // Parse cookies: extract name=value from "name=value; Path=..." strings
    // Handle comma-separated multiple cookies if get() joins them
    // But fetch API 'get' behavior on Set-Cookie is tricky. Better to use raw helper if available, 
    // or splitting by valid cookie separators.
    // Simple robust approach for standard cookies:
    const cookieMap = new Map();
    // Split by comma NOT inside expires date? 
    // Actually, node-fetch/undici usually joins with comma space.
    // A better way is to rely on the fact we likely get multiple Set-Cookie lines in raw headers?
    // But headers.get returns string.

    // Let's iterate manually via raw() if possible, or split. 
    // For now, heuristic split: split by ", " then filter for known cookies or just clean attributes.
    // Actually, simple regex to extract name=value pairs before known attributes?

    // Better strategy: Use a proper cookie parser or custom split.
    // Assuming this environment, let's just grab the whole string and clean it up.

    // Hacky but effective for test script:
    const cleanCookie = rawCookies.split(',')
        .map(c => c.split(';')[0].trim()) // Take only first part (name=value) before attributes
        .filter(c => !c.match(/^(Path|Expires|HttpOnly|Secure|SameSite|Priority|Domain)=/i)) // Filter out attributes that might have leaked if split failed
        .join('; ');

    console.log('Parsed Cookie Header:', cleanCookie);
    console.log('✅ Authentication Successful. Session Cookie Acquired.');

    // Combine cookies (CSRF + Session)
    return [cookies, cleanCookie].join('; ');
}

async function fetchValidIds() {
    console.log('🔍 Fetching valid IDs from DB...');
    let modelo = await prisma.modeloNeumatico.findFirst({ where: { activo: true } });

    // Fallback: Create Modelo if missing
    if (!modelo) {
        console.log('⚠️ Missing Modelo. Creating dummy...');
        const fabricante = await prisma.fabricanteNeumatico.create({
            data: { nombre: 'TEST FABRICANTE', activo: true }
        });
        modelo = await prisma.modeloNeumatico.create({
            data: {
                fabricante_id: fabricante.id,
                nombre_modelo: 'TEST MODEL',
                medida: '295/80R22.5',
                profundidad_original_mm: 20,
                activo: true
            }
        });
    }

    let proveedor = await prisma.proveedor.findFirst({ where: { activo: true } });
    if (!proveedor) {
        console.log('⚠️ Missing Proveedor. Creating dummy...');
        const user = await prisma.usuario.findUnique({ where: { username: USER_CREDENTIALS.identifier } });
        proveedor = await prisma.proveedor.create({
            data: {
                nombre: 'TEST PROVEEDOR',
                tipo: 'DISTRIBUIDOR',
                empresa_id: user.empresa_id,
                activo: true
            }
        });
    }

    let almacen = await prisma.almacen.findFirst({ where: { activo: true } });
    if (!almacen) {
        console.log('⚠️ Missing Almacen. Creating dummy...');
        const user = await prisma.usuario.findUnique({ where: { username: USER_CREDENTIALS.identifier } });
        almacen = await prisma.almacen.create({
            data: {
                nombre: 'TEST ALMACEN',
                codigo: 'ALM-TEST',
                empresa_id: user.empresa_id,
                activo: true
            }
        });
    }

    // Now find or create Neumatico
    let neumatico = await prisma.neumatico.findFirst({ select: { id: true } });
    if (!neumatico && modelo && proveedor && almacen) {
        console.log('⚠️ No Neumatico found. Creating dummy neumatico for test...');
        const user = await prisma.usuario.findUnique({ where: { username: USER_CREDENTIALS.identifier } });
        neumatico = await prisma.neumatico.create({
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
                numero_serie: `TEST-${Date.now()}`,
                empresa_id: user.empresa_id,
                profundidad_inicial_mm: 20,
                vida_actual: 1,
                reencauches_realizados: 0,
                activo: true,
                fecha_compra: new Date(), // Required
                fecha_fabricacion: new Date()
            }
        });
        console.log('✅ Created temporary neumatico:', neumatico.id);
    } else {
        console.log('ℹ️ Found existing neumatico:', neumatico?.id);
    }

    const result = {
        modelo_id: modelo?.id,
        proveedor_id: proveedor?.id,
        almacen_id: almacen?.id,
        neumatico_id: neumatico?.id,
    };

    global.ID_CACHE = result; // Update global cache if used
    console.log('✅ IDs Loaded:', result);
    return result;
}

const generatePurchasePayload = () => ({
    tipo_evento: 'COMPRA',
    fecha_evento: new Date().toISOString(),
    costo_evento: 200 + Math.random() * 50,
    modelo_id: VALID_DATA.modelo_id,
    proveedor_id: VALID_DATA.proveedor_id,
    almacen_destino_id: VALID_DATA.almacen_id,
    numero_serie: `PRO-STRESS-${uuidv4().substring(0, 8)}`,
    dot: '4025',
    profundidad_remanente: 20,
    observaciones: 'Professional Authenticated Load Test'
});

const generateInspectPayload = () => ({
    tipo_evento: 'INSPECCION',
    neumatico_id: ID_CACHE.neumatico_id,
    fecha_evento: new Date().toISOString(),
    profundidad_remanente: 10 + Math.random() * 5,
    presion_psi: 100 + Math.random() * 10,
    kilometraje_acumulado: 1000 + Math.random() * 100
});

async function runProfessionalStressTest() {
    try {
        await fetchValidIds(); // Fetch IDs first
        const sessionCookie = await loginAndGetCookie();

        console.log('🚀 Starting PROFESSIONAL Stress Test on GesNeu API...');

        // Verify smoke test
        console.log('💨 Running Smoke Test...');
        const payload = JSON.stringify({
            tipo_evento: 'INSPECCION', // Correct key
            neumatico_id: ID_CACHE.neumatico_id,
            fecha_evento: new Date().toISOString(),
            profundidad_remanente: 12,
            presion_psi: 100,
            kilometraje_acumulado: 1000
        });

        const smokeRes = await fetch(`${API_URL}/neumaticos/eventos`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Cookie': sessionCookie
            },
            body: payload
        });

        if (!smokeRes.ok) {
            console.error('❌ SMOKE TEST FAILED:', smokeRes.status, smokeRes.statusText);
            const text = await smokeRes.text();
            console.error('RESPONSE:', text);
            console.log('Payload was:', payload);
            process.exit(1);
        }
        console.log('✅ Smoke Test Passed (Status 200/201)');

        const instance = autocannon({
            url: `${API_URL}/neumaticos/eventos`,
            connections: CONNECTIONS,
            duration: DURATION,
            method: 'POST',
            headers: {
                'Cookie': sessionCookie,
                'Content-Type': 'application/json'
            },
            requests: [
                {
                    method: 'POST',
                    path: '/api/v1/neumaticos/eventos', // FIXED PATH
                    setupRequest: (req) => {
                        req.body = JSON.stringify(generateInspectPayload());
                        return req;
                    }
                }
            ]
        });

        autocannon.track(instance, { renderProgressBar: true });

        instance.on('done', async (result) => {
            console.log('\n✅ Professional Verification Complete');
            console.log('-----------------------------------');
            console.log(`Duration: ${result.duration}s`);
            console.log(`Requests: ${result.requests.total}`);
            console.log(`Latency (avg): ${result.latency.average} ms`);
            console.log(`2xx: ${result['2xx']} | 4xx: ${result['4xx']} | 5xx: ${result['5xx']}`);
            console.log(`Errors: ${result.errors}`);

            // Cleanup
            await prisma.$disconnect();
            await pool.end();
        });
    } catch (err) {
        console.error('❌ Test Failed:', err.message);
        await prisma.$disconnect();
        await pool.end();
        process.exit(1);
    }
}

if (require.main === module) {
    runProfessionalStressTest();
}
