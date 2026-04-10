/**
 * SIMULACIÓN RÁPIDA: CICLO DE VIDA COMPLETO
 * 
 * Optimizada para velocidad con operaciones paralelas.
 * Escenarios reales: compra → montaje → desgaste → rotación → reencauche → desecho
 * 
 * Uso: node scripts/simulacion-rapida.js
 */

const BASE_URL = process.env.BASE_URL || 'http://localhost:3005';
const USERNAME = process.env.STRESS_USER || 'admin';
const PASSWORD = process.env.STRESS_PASSWORD || 'admin123';

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
        headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'Cookie': cookies || '' },
        body: params.toString(), redirect: 'manual'
    });
    const rawCookies = loginRes.headers.get('set-cookie');
    if (!rawCookies) throw new Error('Auth failed');
    const m = rawCookies.match(/authjs\.session-token=([^;]+)/);
    if (!m) throw new Error('No session token');
    return `authjs.session-token=${m[1]}`;
}

const authH = (c) => ({ 'Content-Type': 'application/json', 'Cookie': c });

async function get(c, e) {
    try {
        const r = await fetch(`${BASE_URL}/api/v1/${e}`, { headers: authH(c) });
        const t = await r.text();
        if (!t) return { data: [] };
        return JSON.parse(t);
    } catch { return { data: [] }; }
}

async function post(c, e, b) {
    const r = await fetch(`${BASE_URL}/api/v1/${e}`, {
        method: 'POST', headers: authH(c), body: JSON.stringify(b)
    });
    return { status: r.status, data: await r.json() };
}

async function main() {
    console.log('╔══════════════════════════════════════════════════════════╗');
    console.log('║   SIMULACIÓN RÁPIDA: CICLO DE VIDA COMPLETO              ║');
    console.log('║   GesNeu API - Operaciones Paralelas                     ║');
    console.log('╚══════════════════════════════════════════════════════════╝');
    
    const t0 = Date.now();
    const results = {};
    
    try {
        // 1. AUTH
        console.log('\n🔐 Autenticando...');
        const cookie = await authenticate();
        console.log('   ✅ OK');
        
        // 2. LOAD CATALOGS
        console.log('\n📋 Catálogos...');
        const [modelosR, almacenesR, proveedoresR, motivosR] = await Promise.all([
            get(cookie, 'catalogos/modelos-neumatico'),
            get(cookie, 'catalogos/almacenes'),
            get(cookie, 'catalogos/proveedores'),
            get(cookie, 'catalogos/motivos-desecho')
        ]);
        const modelos = (modelosR.data || modelosR).filter(Boolean);
        const almacenes = (almacenesR.data || almacenesR).filter(Boolean);
        const proveedores = (proveedoresR.data || proveedoresR).filter(Boolean);
        const motivos = (motivosR.data || motivosR).filter(Boolean);
        console.log(`   Modelos: ${modelos.length} | Almacenes: ${almacenes.length} | Proveedores: ${proveedores.length} | Motivos: ${motivos.length}`);
        
        if (!almacenes[0] || !proveedores[0]) {
            console.log('   ❌ Faltan datos base'); return;
        }
        const almacen = almacenes[0], proveedor = proveedores[0];
        
        // 3. LOAD VEHICLES WITH POSITIONS
        console.log('\n🚗 Vehículos...');
        const vehiculosR = await get(cookie, 'vehiculos?limit=10');
        const vehiculos = (vehiculosR.data || vehiculosR).filter(Boolean);
        const vehiclesWithPos = [];
        for (const v of vehiculos.slice(0, 5)) {
            const m = await get(cookie, `vehiculos/${v.id}/montaje`);
            const md = m.data || m;
            const pos = [];
            for (const eje of (md.ejes || [])) {
                for (const p of (eje.posiciones || [])) {
                    if (!p.ocupada) pos.push(p);
                }
            }
            if (pos.length > 0) vehiclesWithPos.push({ ...v, pos });
        }
        console.log(`   Con posiciones libres: ${vehiclesWithPos.length}`);
        if (vehiclesWithPos.length === 0) { console.log('   ❌ Sin vehículos disponibles'); return; }
        
        // 4. COMPRA (parallel)
        console.log('\n📦 ESCENARIO 1: COMPRA PARALELA (8 neumáticos)');
        const compras = [];
        for (let i = 0; i < 8; i++) {
            const modelo = modelos[i % modelos.length];
            compras.push(post(cookie, 'neumaticos', {
                modelo_id: modelo.id,
                proveedor_compra_id: proveedor.id,
                ubicacion_almacen_id: almacen.id,
                numero_serie: `SIM-${Date.now()}-${i}`,
                dot: '2425',
                profundidad_inicial_mm: modelo.profundidad_original_mm || 18,
                costo_compra: 200 + Math.floor(Math.random() * 100),
                fecha_compra: new Date().toISOString(),
                es_reencauchado: false,
                moneda_compra: 'PEN'
            }));
        }
        const compraResults = await Promise.all(compras);
        const comprados = compraResults.filter(r => r.status === 201).map((r, i) => ({
            id: r.data.data?.id || r.data.id,
            modelo: modelos[i % modelos.length].nombre_modelo
        }));
        console.log(`   ✅ Comprados: ${comprados.length}/8`);
        results.compra = comprados.length;
        
        if (comprados.length === 0) { console.log('   ❌ Sin neumáticos para continuar'); return; }
        
        // 5. MONTAJE (parallel - up to available positions)
        console.log('\n🔧 ESCENARIO 2: MONTAJE PARALELO');
        const v0 = vehiclesWithPos[0];
        const mounts = [];
        const positionsToUse = v0.pos.slice(0, Math.min(comprados.length, v0.pos.length));
        
        for (let i = 0; i < positionsToUse.length && i < comprados.length; i++) {
            mounts.push(post(cookie, 'operaciones/montaje', {
                neumatico_id: comprados[i].id,
                vehiculo_id: v0.id,
                posicion_id: positionsToUse[i].id,
                contador_vehiculo: 50000,
                profundidad_mm: 17.5,
                presion_psi: 105
            }));
        }
        const mountResults = await Promise.all(mounts);
        const montados = mountResults.filter(r => r.status === 200 || r.status === 201).map((_, i) => comprados[i].id);
        console.log(`   ✅ Montados: ${montados.length}/${mounts.length} en ${v0.placa || v0.id.slice(0, 6)}`);
        results.montaje = montados.length;
        
        if (montados.length === 0) { console.log('   ❌ Sin montajes'); return; }
        
        // 6. INSPECCIÓN (parallel - simulating wear over time)
        console.log('\n🔍 ESCENARIO 3: INSPECCIÓN CON DESGASTE');
        const kmSteps = [55000, 65000, 75000];
        let totalAlerts = 0;
        
        for (const km of kmSteps) {
            const depth = Math.max(17 - ((km - 50000) / 10000) * 1.2, 3);
            const inspections = montados.map(tid => post(cookie, 'neumaticos/eventos', {
                tipo_evento: 'INSPECCION',
                neumatico_id: tid,
                fecha_evento: new Date().toISOString(),
                contador_vehiculo: km,
                profundidad_remanente: parseFloat((depth + (Math.random() - 0.5) * 2).toFixed(1)),
                presion_psi: parseFloat((90 + Math.random() * 20 - ((km - 50000) / 10000) * 2).toFixed(1)),
                observaciones: `Simulación Km ${km}`
            }));
            
            const inspResults = await Promise.all(inspections);
            const successCount = inspResults.filter(r => r.status === 200 || r.status === 201).length;
            
            // Check for low pressure alerts
            const alertsCheck = await get(cookie, 'alertas?limit=5');
            const alerts = (alertsCheck.data || alertsCheck).filter(Boolean);
            totalAlerts = alerts.length;
            
            const status = depth < 5 ? '🚨CRÍTICO' : depth < 8 ? '⚠️Bajo' : '✅OK';
            console.log(`   📍 Km ${km.toLocaleString()}: Prof ~${depth.toFixed(1)}mm | ${status} | ${successCount}/${montados.length} OK | Alertas: ${totalAlerts}`);
        }
        results.inspeccion = kmSteps.length;
        
        // 7. ROTACIÓN
        console.log('\n🔄 ESCENARIO 4: ROTACIÓN');
        if (montados.length >= 2 && positionsToUse.length >= 2) {
            const movimientos = montados.slice(0, Math.min(4, positionsToUse.length)).map((tid, i) => ({
                neumatico_id: tid,
                posicion_destino_id: positionsToUse[(i + 1) % Math.min(montados.length, positionsToUse.length)].id
            }));
            
            const rotRes = await post(cookie, 'operaciones/rotacion', {
                vehiculo_id: v0.id,
                contador_vehiculo: 80000,
                movimientos,
                observaciones: 'Rotación simulación rápida'
            });
            
            if (rotRes.status === 200 || rotRes.status === 201) {
                const processed = rotRes.data.data?.movimientos_procesados || movimientos.length;
                console.log(`   ✅ Rotación: ${processed} neumáticos reubicados`);
                results.rotacion = processed;
            } else {
                console.log(`   ❌ Rotación: ${rotRes.data?.error || rotRes.status}`);
                results.rotacion = 0;
            }
        }
        
        // 8. DESENSAMBLAJE
        console.log('\n📤 ESCENARIO 5: DESMONTAJE');
        const dismounts = montados.slice(0, 2).map(tid => post(cookie, 'operaciones/desmontaje', {
            neumatico_id: tid,
            destino: 'STOCK',
            contador_vehiculo: 85000,
            almacen_destino_id: almacen.id
        }));
        const dismountResults = await Promise.all(dismounts);
        const desmontados = dismountResults.filter(r => r.status === 200 || r.status === 201).length;
        console.log(`   ✅ Desmontados: ${desmontados}/${dismounts.length} → STOCK`);
        results.desmontaje = desmontados;
        
        // 9. FINAL METRICS
        console.log('\n📊 ESCENARIO 6: MÉTRICAS FINALES');
        const [invR, alertasR] = await Promise.all([
            get(cookie, 'dashboard/inventario'),
            get(cookie, 'alertas?limit=10')
        ]);
        const inv = invR.data || invR;
        const alertas = (alertasR.data || alertasR).filter(Boolean);
        
        if (inv.por_estado && Array.isArray(inv.por_estado)) {
            console.log('   📦 Inventario:');
            for (const item of inv.por_estado) {
                console.log(`      ${item.estado || item._id}: ${item.cantidad || item.count}`);
            }
        }
        console.log(`   🚨 Alertas activas: ${alertas.length}`);
        results.alertas = alertas.length;
        
        // REPORT
        const totalTime = ((Date.now() - t0) / 1000).toFixed(1);
        const totalOps = Object.values(results).reduce((s, v) => s + (typeof v === 'number' ? v : 0), 0);
        
        console.log('\n╔══════════════════════════════════════════════════════════╗');
        console.log('║              REPORTE FINAL - SIMULACIÓN RÁPIDA           ║');
        console.log('╠══════════════════════════════════════════════════════════╣');
        console.log(`║  Tiempo: ${String(totalTime).padStart(44)}s ║`);
        console.log(`║  Operaciones: ${String(totalOps).padStart(39)}   ║`);
        console.log('╠══════════════════════════════════════════════════════════╣');
        
        const lines = [
            ['Compra', `${results.compra} neumáticos`],
            ['Montaje', `${results.montaje} en vehículo`],
            ['Inspección', `${results.inspeccion} rondas`],
            ['Rotación', `${results.rotacion || 0} neumáticos`],
            ['Desmontaje', `${results.desmontaje} a stock`],
            ['Alertas', `${results.alertas || 0} activas`]
        ];
        
        for (const [name, val] of lines) {
            const l = `║  ${name}:`;
            const p = 56 - l.length - val.length;
            console.log(`${l} ${val}${' '.repeat(Math.max(0, p))} ║`);
        }
        console.log('╚══════════════════════════════════════════════════════════╝');
        console.log('\n✅ Simulación rápida completada');
        
    } catch (e) {
        console.error('\n❌ Error:', e.message);
        process.exit(1);
    }
}

main();
