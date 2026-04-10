/**
 * SIMULACIÓN DE INTEGRACIÓN WEBHOOKS / ERP
 * 
 * Escenarios simulados:
 * 1. CONFIGURACIÓN - Crear webhook apuntando a ERP mock
 * 2. EVENTOS CRÍTICOS - Generar alertas que disparan webhooks
 * 3. COLA DE PROCESAMIENTO - Verificar queue de webhooks
 * 4. ERP MOCK - Servidor local que simula recepción de ERP
 * 5. RETRY - Simular fallos de ERP y reintentos
 * 
 * Uso: node scripts/simulacion-webhooks-erp.js
 */

const BASE_URL = process.env.BASE_URL || 'http://localhost:3005';
const USERNAME = process.env.STRESS_USER || 'admin';
const PASSWORD = process.env.STRESS_PASSWORD || 'admin123';
const ERP_MOCK_PORT = process.env.ERP_MOCK_PORT || 9999;

const http = require('http');

// ============ AUTH ============
async function authenticate() {
    const csrfRes = await fetch(`${BASE_URL}/api/auth/csrf`);
    const { csrfToken } = await csrfRes.json();
    const cookies = csrfRes.headers.get('set-cookie');
    
    const params = new URLSearchParams();
    params.append('identifier', USERNAME);
    params.append('password', PASSWORD);
    params.append('csrfToken', csrfToken);
    params.append('json', 'true');
    
    const loginRes = await fetch(`${BASE_URL}/api/auth/callback/credentials`, {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': cookies || ''
        },
        body: params.toString(),
        redirect: 'manual'
    });
    
    const rawCookies = loginRes.headers.get('set-cookie');
    if (!rawCookies) throw new Error(`Auth failed: no cookies. Status: ${loginRes.status}`);
    
    const sessionMatch = rawCookies.match(/authjs\.session-token=([^;]+)/);
    if (!sessionMatch) throw new Error('No session token found in cookies');
    
    return `authjs.session-token=${sessionMatch[1]}`;
}

function authHeaders(cookie) {
    return {
        'Content-Type': 'application/json',
        'Cookie': cookie
    };
}

// ============ ERP MOCK SERVER ============
function createErpMockServer() {
    let receivedPayloads = [];
    let failNext = false;
    
    const server = http.createServer((req, res) => {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', () => {
            const timestamp = new Date().toISOString();
            
            if (failNext) {
                failNext = false;
                console.log(`   🚫 ERP MOCK: Simulando fallo (500) - ${timestamp}`);
                res.writeHead(500, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'ERP temporalmente no disponible' }));
                return;
            }
            
            const payload = JSON.parse(body || '{}');
            receivedPayloads.push({ timestamp, headers: req.headers, payload });
            
            console.log(`   ✅ ERP MOCK: Recibido evento ${payload.evento || payload.tipo_evento || 'desconocido'} - ${timestamp}`);
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ success: true, processedAt: timestamp }));
        });
    });
    
    return {
        server,
        getReceived: () => receivedPayloads,
        setFailNext: (val) => { failNext = val; }
    };
}

// ============ WEBHOOK API HELPERS ============
async function getApi(cookie, endpoint) {
    try {
        const res = await fetch(`${BASE_URL}/api/v1/${endpoint}`, {
            headers: authHeaders(cookie)
        });
        const text = await res.text();
        if (!text) return { data: [] };
        return JSON.parse(text);
    } catch (e) {
        return { data: [] };
    }
}

async function postApi(cookie, endpoint, body) {
    const res = await fetch(`${BASE_URL}/api/v1/${endpoint}`, {
        method: 'POST',
        headers: authHeaders(cookie),
        body: JSON.stringify(body)
    });
    return { status: res.status, data: await res.json() };
}

// ============ SCENARIO HELPERS ============
async function findModelo(cookie) {
    const data = await getApi(cookie, 'catalogos/modelos-neumatico');
    const modelos = data.data || data;
    return Array.isArray(modelos) ? modelos[0] : null;
}

async function findAlmacen(cookie) {
    const data = await getApi(cookie, 'catalogos/almacenes');
    const almacenes = data.data || data;
    return Array.isArray(almacenes) ? almacenes[0] : null;
}

async function findProveedor(cookie) {
    const data = await getApi(cookie, 'catalogos/proveedores');
    const proveedores = data.data || data;
    return Array.isArray(proveedores) ? proveedores[0] : null;
}

async function findNeumaticoStock(cookie) {
    const data = await getApi(cookie, 'neumaticos?estado=EN_STOCK&limit=5');
    const items = data.data || data;
    return Array.isArray(items) ? items.find(n => n.estado_actual === 'EN_STOCK') : null;
}

// ============ MAIN ============
async function main() {
    console.log('╔══════════════════════════════════════════════════════════╗');
    console.log('║   SIMULACIÓN DE INTEGRACIÓN WEBHOOKS / ERP               ║');
    console.log('║   GesNeu API - Pruebas Reales                            ║');
    console.log('╚══════════════════════════════════════════════════════════╝');
    
    const startTime = Date.now();
    const results = {};
    
    try {
        // 1. START ERP MOCK SERVER
        console.log('\n🖥️ ESCENARIO 1: ERP MOCK SERVER');
        console.log('─'.repeat(50));
        
        const erpMock = createErpMockServer();
        
        await new Promise((resolve) => erpMock.server.listen(ERP_MOCK_PORT, () => {
            console.log(`   ✅ ERP Mock escuchando en puerto ${ERP_MOCK_PORT}`);
            resolve();
        }));
        
        // 2. AUTH
        console.log('\n🔐 ESCENARIO 2: AUTENTICACIÓN');
        console.log('─'.repeat(50));
        
        const cookie = await authenticate();
        console.log('   ✅ Autenticado exitosamente');
        
        // 3. CREATE WEBHOOK CONFIG
        console.log('\n🔗 ESCENARIO 3: CONFIGURACIÓN DE WEBHOOK');
        console.log('─'.repeat(50));
        
        const webhookPayload = {
            nombre: 'ERP Integration Test',
            url: `https://localhost:${ERP_MOCK_PORT}/webhook/receive`,
            secret: 'test_secret_key_12345',
            eventos: ['ALERTA_CRITICAL', 'DESECHO'],
            activo: true
        };
        
        const webhookRes = await postApi(cookie, 'webhooks', webhookPayload);
        console.log(`   Status: ${webhookRes.status}`);
        
        if (webhookRes.status === 201 || webhookRes.status === 200) {
            const webhook = webhookRes.data.data || webhookRes.data;
            console.log(`   ✅ Webhook creado: ${webhook.nombre}`);
            console.log(`   ✅ ID: ${webhook.id}`);
            console.log(`   ✅ Eventos suscritos: ${webhook.eventos?.join(', ') || 'N/A'}`);
            results.configuracion = { creado: true, id: webhook.id };
        } else {
            console.log(`   ❌ Error creando webhook: ${JSON.stringify(webhookRes.data).slice(0, 200)}`);
            results.configuracion = { creado: false };
        }
        
        // 4. LIST WEBHOOKS
        console.log('\n📋 ESCENARIO 4: LISTAR WEBHOOKS');
        console.log('─'.repeat(50));
        
        const webhooksData = await getApi(cookie, 'webhooks');
        const webhooks = webhooksData.data || webhooksData;
        console.log(`   ✅ Webhooks configurados: ${Array.isArray(webhooks) ? webhooks.length : 0}`);
        results.listado = { total: Array.isArray(webhooks) ? webhooks.length : 0 };
        
        // 5. TRIGGER CRITICAL EVENT (Inspección con presión crítica)
        console.log('\n🚨 ESCENARIO 5: GENERAR EVENTO CRÍTICO');
        console.log('─'.repeat(50));
        
        const neum = await findNeumaticoStock(cookie);
        if (!neum) {
            console.log('   ⚠️ No hay neumáticos en stock. Creando uno...');
            
            const modelo = await findModelo(cookie);
            const almacen = await findAlmacen(cookie);
            const proveedor = await findProveedor(cookie);
            
            if (modelo && almacen) {
                const compraRes = await postApi(cookie, 'neumaticos', {
                    modelo_id: modelo.id,
                    proveedor_compra_id: proveedor?.id,
                    ubicacion_almacen_id: almacen.id,
                    numero_serie: `WEBHOOK-TEST-${Date.now()}`,
                    dot: '2425',
                    profundidad_inicial_mm: 18,
                    costo_compra: 250,
                    fecha_compra: new Date().toISOString(),
                    es_reencauchado: false,
                    moneda_compra: 'PEN'
                });
                
                if (compraRes.status === 201) {
                    const created = compraRes.data.data || compraRes.data;
                    results.neumatico_creado = { id: created.id };
                    console.log(`   ✅ Neumático creado: ${created.id?.slice(0, 8)}`);
                }
            }
        }
        
        // Create critical inspection event
        if (neum) {
            console.log(`   📤 Enviando inspección con presión crítica (50 PSI)...`);
            const eventRes = await postApi(cookie, 'neumaticos/eventos', {
                tipo_evento: 'INSPECCION',
                neumatico_id: neum.id,
                fecha_evento: new Date().toISOString(),
                contador_vehiculo: 50000,
                profundidad_remanente: 8.5,
                presion_psi: 50, // Critical: below 80% of typical 100 PSI
                observaciones: 'Simulación webhook: presión crítica detectada'
            });
            
            console.log(`   Status: ${eventRes.status}`);
            if (eventRes.data.success) {
                console.log('   ✅ Evento registrado exitosamente');
                results.evento_critico = { registrado: true };
            } else {
                console.log(`   ❌ Error: ${JSON.stringify(eventRes.data).slice(0, 200)}`);
                results.evento_critico = { registrado: false };
            }
        }
        
        // 6. CHECK WEBHOOK QUEUE
        console.log('\n📊 ESCENARIO 6: VERIFICAR COLA DE WEBHOOKS');
        console.log('─'.repeat(50));
        
        await new Promise(r => setTimeout(r, 3000)); // Wait for async processing
        
        const jobsData = await getApi(cookie, 'webhooks/jobs?limit=10');
        const jobs = jobsData.data || jobsData;
        const jobCount = Array.isArray(jobs) ? jobs.length : 0;
        console.log(`   ✅ Jobs en cola: ${jobCount}`);
        
        if (jobCount > 0) {
            const statuses = {};
            for (const job of jobs) {
                statuses[job.status] = (statuses[job.status] || 0) + 1;
            }
            console.log(`   📊 Por estado: ${JSON.stringify(statuses)}`);
            results.cola = { total: jobCount, estados: statuses };
        } else {
            results.cola = { total: 0, nota: 'Sin jobs o endpoint no disponible' };
        }
        
        // 7. ERP RECEIPT VERIFICATION
        console.log('\n🏭 ESCENARIO 7: VERIFICAR RECEPCIÓN ERP');
        console.log('─'.repeat(50));
        
        const received = erpMock.getReceived();
        console.log(`   ✅ Eventos recibidos por ERP: ${received.length}`);
        results.erp_recepcion = { eventos_recibidos: received.length };
        
        // 8. RETRY SIMULATION
        console.log('\n🔄 ESCENARIO 8: SIMULACIÓN DE RETRY');
        console.log('─'.repeat(50));
        
        erpMock.setFailNext(true);
        console.log('   🚫 Configurado: próximo request al ERP fallará (500)');
        
        // Trigger another event that should hit the failing ERP
        if (neum) {
            const retryEvent = await postApi(cookie, 'neumaticos/eventos', {
                tipo_evento: 'INSPECCION',
                neumatico_id: neum.id,
                fecha_evento: new Date().toISOString(),
                contador_vehiculo: 51000,
                profundidad_remanente: 7.0,
                presion_psi: 45,
                observaciones: 'Simulación retry: segunda inspección crítica'
            });
            
            console.log(`   Evento status: ${retryEvent.status}`);
            results.retry = { evento_disparado: retryEvent.status === 200 || retryEvent.status === 201 };
            
            await new Promise(r => setTimeout(r, 2000));
            
            const receivedAfterFail = erpMock.getReceived();
            const failJobs = receivedAfterFail.length - received.length;
            console.log(`   ✅ Eventos tras fallo simulado: ${failJobs} nuevos`);
        }
        
        // 9. FINAL SUMMARY
        const totalTime = ((Date.now() - startTime) / 1000).toFixed(1);
        
        console.log('\n╔══════════════════════════════════════════════════════════╗');
        console.log('║             REPORTE FINAL - INTEGRACIÓN ERP              ║');
        console.log('╠══════════════════════════════════════════════════════════╣');
        console.log(`║  Tiempo total: ${String(totalTime).padStart(42)}s ║`);
        
        for (const [scenario, data] of Object.entries(results)) {
            const summary = typeof data === 'object' ? 
                Object.entries(data).map(([k, v]) => `${k}: ${typeof v === 'object' ? JSON.stringify(v) : v}`).join(', ') :
                data;
            const label = `║  ${scenario}:`;
            const padding = 56 - label.length - summary.length;
            console.log(`${label} ${summary}${' '.repeat(Math.max(0, padding))} ║`);
        }
        
        console.log('╚══════════════════════════════════════════════════════════╝');
        
        // Cleanup
        erpMock.server.close();
        console.log('\n✅ Simulación de webhooks/ERP completada exitosamente');
        
    } catch (error) {
        console.error('\n❌ Error fatal:', error.message);
        console.error(error.stack);
        process.exit(1);
    }
}

main();
