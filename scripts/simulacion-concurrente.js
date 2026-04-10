/**
 * SIMULACIÓN DE ESTRÉS: OPERACIONES CONCURRENTES
 * 
 * Simula comportamiento real de múltiples operadores trabajando simultáneamente.
 * - 5 "operadores" creando inspecciones en paralelo
 * - Contención de recursos (mismos neumáticos)
 * - Detección de race conditions
 * - Métricas de rendimiento bajo carga
 * 
 * Uso: node scripts/simulacion-concurrente.js
 */

const BASE_URL = process.env.BASE_URL || 'http://localhost:3005';
const CONCURRENCY = parseInt(process.env.CONCURRENCY || '5');
const OPS_PER_OPERATOR = parseInt(process.env.OPS_PER_OPERATOR || '20');

async function auth() {
    const csrfRes = await fetch(`${BASE_URL}/api/auth/csrf`);
    const { csrfToken } = await csrfRes.json();
    const cookies = csrfRes.headers.get('set-cookie');
    const params = new URLSearchParams();
    params.append('identifier', 'admin');
    params.append('password', 'admin123');
    params.append('csrfToken', csrfToken);
    params.append('json', 'true');
    const r = await fetch(`${BASE_URL}/api/auth/callback/credentials`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'Cookie': cookies || '' },
        body: params.toString(), redirect: 'manual'
    });
    const m = r.headers.get('set-cookie')?.match(/authjs\.session-token=([^;]+)/);
    return m ? `authjs.session-token=${m[1]}` : null;
}

const authH = (c) => ({ 'Content-Type': 'application/json', 'Cookie': c });

async function main() {
    console.log('╔══════════════════════════════════════════════════════════╗');
    console.log('║   SIMULACIÓN DE ESTRÉS: OPERACIONES CONCURRENTES         ║');
    console.log(`║   ${CONCURRENCY} operadores × ${OPS_PER_OPERATOR} ops = ${CONCURRENCY * OPS_PER_OPERATOR} operaciones totales           ║`);
    console.log('╚══════════════════════════════════════════════════════════╝');
    
    const t0 = Date.now();
    const cookie = await auth();
    if (!cookie) { console.log('❌ Auth failed'); return; }
    console.log('✅ Autenticado\n');
    
    // Get installed tires
    const neumsR = await fetch(`${BASE_URL}/api/v1/neumaticos?limit=100`, { headers: authH(cookie) });
    const neumsData = await neumsR.json();
    const allNeums = Array.isArray(neumsData.data) ? neumsData.data : (Array.isArray(neumsData) ? neumsData : []);
    const installed = allNeums.filter(n => n.estado_actual === 'INSTALADO' || n.estado === 'INSTALADO');
    
    if (installed.length < 4) {
        console.log(`⚠️ Solo ${installed.length} neumáticos instalados. Ejecute simulacion-rapida.js primero.`);
        return;
    }
    
    console.log(`📊 ${installed.length} neumáticos instalados disponibles\n`);
    
    // ============ SCENARIO: Concurrent Inspections ============
    console.log(`🔄 Escenario: ${CONCURRENCY} operadores × ${OPS_PER_OPERATOR} inspecciones`);
    console.log('─'.repeat(55));
    
    const operatorResults = [];
    const allLatencies = [];
    let totalSuccess = 0;
    let totalErrors = 0;
    let raceConditions = 0;
    
    const operators = [];
    for (let op = 0; op < CONCURRENCY; op++) {
        operators.push((async () => {
            const operatorId = `OP-${op + 1}`;
            let successes = 0;
            let errors = 0;
            let latencies = [];
            
            for (let i = 0; i < OPS_PER_OPERATOR; i++) {
                // Each operator picks a random installed tire
                const tire = installed[Math.floor(Math.random() * installed.length)];
                const km = 50000 + Math.floor(Math.random() * 100000);
                const depth = 4 + Math.random() * 14;
                const pressure = 60 + Math.random() * 50;
                
                const start = Date.now();
                try {
                    const r = await fetch(`${BASE_URL}/api/v1/neumaticos/eventos`, {
                        method: 'POST',
                        headers: authH(cookie),
                        body: JSON.stringify({
                            tipo_evento: 'INSPECCION',
                            neumatico_id: tire.id,
                            fecha_evento: new Date().toISOString(),
                            contador_vehiculo: km,
                            profundidad_remanente: parseFloat(depth.toFixed(1)),
                            presion_psi: parseFloat(pressure.toFixed(1)),
                            observaciones: `${operatorId} op ${i + 1}/${OPS_PER_OPERATOR}`
                        })
                    });
                    
                    const latency = Date.now() - start;
                    latencies.push(latency);
                    allLatencies.push(latency);
                    
                    if (r.status === 200 || r.status === 201) {
                        successes++;
                        totalSuccess++;
                    } else {
                        errors++;
                        totalErrors++;
                        const d = await r.json();
                        if (d.code === 'CONFLICT' || d.error?.includes('competencia')) {
                            raceConditions++;
                        }
                    }
                } catch (e) {
                    errors++;
                    totalErrors++;
                    latencies.push(Date.now() - start);
                }
            }
            
            const avgLatency = latencies.length > 0 ? Math.round(latencies.reduce((a, b) => a + b, 0) / latencies.length) : 0;
            return { operatorId, successes, errors, avgLatency };
        })());
    }
    
    const results = await Promise.all(operators);
    
    console.log('\n📊 Resultados por operador:');
    console.log('┌──────────┬──────────┬────────┬──────────┐');
    console.log('│ Operador │ Éxitos   │ Errores│ Latencia │');
    console.log('├──────────┼──────────┼────────┼──────────┤');
    for (const r of results) {
        console.log(`│ ${r.operatorId.padEnd(8)} │ ${String(r.successes).padEnd(8)} │ ${String(r.errors).padEnd(6)} │ ${String(r.avgLatency + 'ms').padEnd(8)} │`);
    }
    console.log('└──────────┴──────────┴────────┴──────────┘');
    
    // Stats
    const totalOps = CONCURRENCY * OPS_PER_OPERATOR;
    const totalTime = ((Date.now() - t0) / 1000).toFixed(1);
    const avgLatency = allLatencies.length > 0 ? Math.round(allLatencies.reduce((a, b) => a + b, 0) / allLatencies.length) : 0;
    const p95Latency = allLatencies.length > 0 ? allLatencies.sort((a, b) => a - b)[Math.floor(allLatencies.length * 0.95)] : 0;
    const maxLatency = allLatencies.length > 0 ? Math.max(...allLatencies) : 0;
    const opsPerSecond = (totalSuccess / parseFloat(totalTime)).toFixed(1);
    
    console.log('\n📈 Estadísticas generales:');
    console.log(`   ✅ Éxitos: ${totalSuccess}/${totalOps} (${((totalSuccess / totalOps) * 100).toFixed(1)}%)`);
    console.log(`   ❌ Errores: ${totalErrors}`);
    console.log(`   ⚡ Race conditions: ${raceConditions}`);
    console.log(`   ⏱️ Latencia promedio: ${avgLatency}ms`);
    console.log(`   📊 P95 latencia: ${p95Latency}ms`);
    console.log(`   🔴 Max latencia: ${maxLatency}ms`);
    console.log(`   🚀 Ops/segundo: ${opsPerSecond}`);
    
    // Final inventory check
    const invR = await fetch(`${BASE_URL}/api/v1/dashboard/inventario`, { headers: authH(cookie) });
    const inv = await invR.json();
    const invData = inv.data || inv;
    if (invData.por_estado && Array.isArray(invData.por_estado)) {
        console.log('\n📦 Estado final del inventario:');
        for (const item of invData.por_estado) {
            console.log(`   ${item.estado || item._id}: ${item.cantidad || item.count}`);
        }
    }
    
    console.log('\n╔══════════════════════════════════════════════════════════╗');
    console.log('║            REPORTE DE ESTRÉS - CONCURRENCIA              ║');
    console.log('╠══════════════════════════════════════════════════════════╣');
    console.log(`║  Operadores: ${String(CONCURRENCY).padStart(42)}   ║`);
    console.log(`║  Ops/operador: ${String(OPS_PER_OPERATOR).padStart(40)}   ║`);
    console.log(`║  Tiempo total: ${String(totalTime).padStart(40)}s ║`);
    console.log(`║  Tasa: ${String(opsPerSecond + ' ops/s').padStart(44)} ║`);
    console.log(`║  Éxito: ${String(((totalSuccess / totalOps) * 100).toFixed(1) + '%').padStart(44)} ║`);
    console.log(`║  Race conditions: ${String(raceConditions).padStart(37)}   ║`);
    console.log('╚══════════════════════════════════════════════════════════╝');
    
    // Verdict
    const successRate = (totalSuccess / totalOps) * 100;
    console.log(successRate >= 95 ? '\n✅ SISTEMA ESTABLE bajo carga concurrente' :
                successRate >= 80 ? '\n⚠️ SISTEMA ACEPTABLE con degradación leve' :
                '\n❌ SISTEMA INESTABLE bajo carga concurrente');
}

main().catch(e => { console.error('❌', e.message); process.exit(1); });
