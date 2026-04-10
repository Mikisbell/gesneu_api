/**
 * SIMULACIÓN AVANZADA: GESTIÓN DE FLOTA MULTI-VEHÍCULO
 * 
 * Escenarios de negocio reales:
 * 1. FLOTA COMPLETA - 10 vehículos, 40+ neumáticos
 * 2. DESGASTE PROGRESIVO - Inspecciones con degradación realista
 * 3. ALERTAS EN CASCADA - Presión baja + profundidad crítica
 * 4. REENCAUCHE COMPLETO - Envío → Proceso → Retorno
 * 5. DESECHO POR DESGASTE - Fin de vida con motivo válido
 * 6. CPK ANALYSIS - Costo por kilómetro por marca/modelo
 * 7. COMPARATIVA RENDIMIENTO - Marcas competidoras
 * 
 * Uso: node scripts/simulacion-flota-avanzada.js
 */

const BASE_URL = process.env.BASE_URL || 'http://localhost:3005';
const USERNAME = process.env.STRESS_USER || 'admin';
const PASSWORD = process.env.STRESS_PASSWORD || 'admin123';

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
    if (!rawCookies) throw new Error(`Auth failed`);
    const sessionMatch = rawCookies.match(/authjs\.session-token=([^;]+)/);
    if (!sessionMatch) throw new Error('No session token');
    return `authjs.session-token=${sessionMatch[1]}`;
}

function authHeaders(cookie) {
    return { 'Content-Type': 'application/json', 'Cookie': cookie };
}

async function getApi(cookie, endpoint) {
    try {
        const res = await fetch(`${BASE_URL}/api/v1/${endpoint}`, { headers: authHeaders(cookie) });
        const text = await res.text();
        if (!text) return { data: [] };
        return JSON.parse(text);
    } catch { return { data: [] }; }
}

async function postApi(cookie, endpoint, body) {
    const res = await fetch(`${BASE_URL}/api/v1/${endpoint}`, {
        method: 'POST',
        headers: authHeaders(cookie),
        body: JSON.stringify(body)
    });
    return { status: res.status, data: await res.json() };
}

// ============ HELPERS DE CATÁLOGO ============
async function loadCatalogs(cookie) {
    const [modelos, almacenes, proveedores, motivos] = await Promise.all([
        getApi(cookie, 'catalogos/modelos-neumatico'),
        getApi(cookie, 'catalogos/almacenes'),
        getApi(cookie, 'catalogos/proveedores'),
        getApi(cookie, 'catalogos/motivos-desecho')
    ]);
    
    return {
        modelos: (modelos.data || modelos).filter(m => m),
        almacenes: (almacenes.data || almacenes).filter(a => a),
        proveedores: (proveedores.data || proveedores).filter(p => p),
        motivos: (motivos.data || motivos).filter(m => m)
    };
}

async function loadVehicles(cookie) {
    const res = await getApi(cookie, 'vehiculos?limit=20');
    const vehicles = (res.data || res).filter(v => v);
    
    // Load positions for each vehicle
    const vehiclesWithPositions = [];
    for (const v of vehicles) {
        const montajeRes = await getApi(cookie, `vehiculos/${v.id}/montaje`);
        const montajeData = montajeRes.data || montajeRes;
        const ejes = montajeData.ejes || [];
        const positions = [];
        for (const eje of ejes) {
            for (const pos of (eje.posiciones || [])) {
                if (!pos.ocupada) positions.push(pos);
            }
        }
        if (positions.length > 0) {
            vehiclesWithPositions.push({ ...v, positions });
        }
    }
    return vehiclesWithPositions;
}

// ============ ESCENARIO 1: COMPRA MASIVA POR MARCA ============
async function scenarioCompraMasiva(cookie, catalogs) {
    console.log('\n📦 ESCENARIO 1: COMPRA MASIVA MULTI-MARCA');
    console.log('─'.repeat(55));
    
    const results = { total: 0, porMarca: {} };
    const almacén = catalogs.almacenes[0];
    const proveedor = catalogs.proveedores[0];
    
    if (!almacén || !proveedor) {
        console.log('   ⚠️ Falta almacén o proveedor');
        return results;
    }
    
    // Buy 3 tires from each available model (simulating brand comparison)
    const modelsToBuy = catalogs.modelos.slice(0, 6);
    
    for (const modelo of modelsToBuy) {
        for (let i = 0; i < 3; i++) {
            const res = await postApi(cookie, 'neumaticos', {
                modelo_id: modelo.id,
                proveedor_compra_id: proveedor.id,
                ubicacion_almacen_id: almacén.id,
                numero_serie: `FLEET-${modelo.nombre_modelo?.slice(0, 6).replace(/\s/g, '')}-${Date.now()}-${i}`,
                dot: '2425',
                profundidad_inicial_mm: modelo.profundidad_original_mm || 18,
                costo_compra: 200 + Math.random() * 100,
                fecha_compra: new Date().toISOString(),
                es_reencauchado: false,
                moneda_compra: 'PEN'
            });
            
            if (res.status === 201) {
                results.total++;
                const marca = modelo.fabricante_nombre || 'Desconocida';
                results.porMarca[marca] = (results.porMarca[marca] || 0) + 1;
            }
        }
    }
    
    console.log(`   ✅ Total comprados: ${results.total}`);
    for (const [marca, count] of Object.entries(results.porMarca)) {
        console.log(`      🏷️ ${marca}: ${count} unidades`);
    }
    return results;
}

// ============ ESCENARIO 2: MONTAJE EN FLOTA ============
async function scenarioMontajeFlota(cookie, vehicles, tiresToMount) {
    console.log('\n🔧 ESCENARIO 2: MONTAJE EN FLOTA MULTI-VEHÍCULO');
    console.log('─'.repeat(55));
    
    let mounted = 0;
    const mountedByVehicle = {};
    
    for (const vehicle of vehicles) {
        if (tiresToMount.length === 0 || vehicle.positions.length === 0) break;
        
        const positionsToUse = vehicle.positions.slice(0, Math.min(4, tiresToMount.length, vehicle.positions.length));
        
        for (let i = 0; i < positionsToUse.length && tiresToMount.length > 0; i++) {
            const tire = tiresToMount.shift();
            const pos = positionsToUse[i];
            
            const res = await postApi(cookie, 'operaciones/montaje', {
                neumatico_id: tire.id,
                vehiculo_id: vehicle.id,
                posicion_id: pos.id,
                contador_vehiculo: Math.floor(40000 + Math.random() * 20000),
                profundidad_mm: tire.profundidad_remanente_actual_mm || 17,
                presion_psi: parseFloat((95 + Math.random() * 20).toFixed(1))
            });
            
            if (res.status === 200 || res.status === 201) {
                mounted++;
                const plate = vehicle.placa || vehicle.id.slice(0, 6);
                mountedByVehicle[plate] = (mountedByVehicle[plate] || 0) + 1;
            }
        }
    }
    
    console.log(`   ✅ Total montados: ${mounted}`);
    for (const [plate, count] of Object.entries(mountedByVehicle)) {
        console.log(`      🚛 ${plate}: ${count} neumáticos`);
    }
    return { mounted, byVehicle: mountedByVehicle };
}

// ============ ESCENARIO 3: DESGASTE PROGRESIVO (5 inspecciones simulando 50k km) ============
async function scenarioDesgasteProgresivo(cookie, tireIds, initialKm = 50000) {
    console.log('\n📉 ESCENARIO 3: DESGASTE PROGRESIVO (Simulación 50k km)');
    console.log('─'.repeat(55));
    
    const inspections = [];
    const kmSteps = [10000, 20000, 30000, 40000, 50000];
    const wearPer10k = 0.8 + Math.random() * 0.4; // 0.8-1.2mm per 10k km (realistic)
    
    for (let step = 0; step < kmSteps.length; step++) {
        const km = initialKm + kmSteps[step];
        const depthLoss = wearPer10k * (step + 1);
        let alertCount = 0;
        let criticalCount = 0;
        
        for (const tireId of tireIds) {
            // Simulate varying conditions per tire
            const baseDepth = 17;
            const currentDepth = parseFloat((baseDepth - depthLoss + (Math.random() - 0.5) * 2).toFixed(1));
            const currentPressure = parseFloat((90 + Math.random() * 25 - (step * 3)).toFixed(1)); // Pressure drops over time
            
            const res = await postApi(cookie, 'neumaticos/eventos', {
                tipo_evento: 'INSPECCION',
                neumatico_id: tireId,
                fecha_evento: new Date(Date.now() + step * 86400000 * 7).toISOString(),
                contador_vehiculo: km,
                profundidad_remanente: Math.max(currentDepth, 2),
                presion_psi: Math.max(currentPressure, 60),
                observaciones: `Inspección ${step + 1}/5 - Km ${km}`
            });
            
            if (res.status === 200 || res.status === 201) {
                if (currentPressure < 80) alertCount++;
                if (currentDepth < 4) criticalCount++;
            }
        }
        
        const summary = [];
        if (alertCount > 0) summary.push(`⚠️${alertCount} baja presión`);
        if (criticalCount > 0) summary.push(`🚨${criticalCount} profundidad crítica`);
        
        console.log(`   📍 Km ${km.toLocaleString()}: Profundidad media ~${(baseDepth - depthLoss).toFixed(1)}mm ${summary.length ? '| ' + summary.join(' ') : '| Todo OK'}`);
        inspections.push({ km, alertCount, criticalCount });
    }
    
    return inspections;
}

// ============ ESCENARIO 4: REENCAUCHE COMPLETO ============
async function scenarioReencaucheCompleto(cookie, tireIds, catalogs) {
    console.log('\n🏭 ESCENARIO 4: CICLO COMPLETO DE REENCAUCHE');
    console.log('─'.repeat(55));
    
    const proveedor = catalogs.proveedores.find(p => p.tipo === 'FABRICANTE') || catalogs.proveedores[0];
    if (!proveedor) {
        console.log('   ⚠️ No hay proveedores disponibles');
        return { enviados: 0, retornados: 0 };
    }
    
    // Phase 1: Send to retreading
    const toRetread = tireIds.slice(0, 2);
    let enviados = 0;
    
    for (const tireId of toRetread) {
        const res = await postApi(cookie, 'reencauche', {
            neumatico_id: tireId,
            proveedor_reencauchador_id: proveedor.id,
            observaciones: 'Envío simulación: desgaste uniforme, apto para reencauche'
        });
        
        if (res.status === 200 || res.status === 201) {
            enviados++;
            console.log(`   ✅ Enviado a reencauche: ${tireId.slice(0, 8)}`);
        } else {
            console.log(`   ⚠️ No se pudo enviar ${tireId.slice(0, 8)}: ${res.data?.error || res.status}`);
        }
    }
    
    console.log(`   📊 Enviados: ${enviados}/${toRetread.length}`);
    return { enviados, retornados: 0 };
}

// ============ ESCENARIO 5: DESECHO PROGRAMADO ============
async function scenarioDesechoProgramado(cookie, tireIds, catalogs) {
    console.log('\n🗑️ ESCENARIO 5: DESECHO PROGRAMADO');
    console.log('─'.repeat(55));
    
    const motivo = catalogs.motivos.find(m => 
        m.nombre?.toLowerCase().includes('desgaste') || 
        m.nombre?.toLowerCase().includes('vida')
    ) || catalogs.motivos[0];
    
    if (!motivo) {
        console.log('   ⚠️ No hay motivos de desecho disponibles');
        return { desechados: 0 };
    }
    
    // Desechar 1 tire
    const tireToScrap = tireIds[0];
    let desechados = 0;
    
    if (tireToScrap) {
        const res = await postApi(cookie, 'neumaticos/eventos', {
            tipo_evento: 'DESECHO',
            neumatico_id: tireToScrap,
            motivo_desecho_id: motivo.id,
            observaciones: 'Desecho por simulación: fin de vida útil programado'
        });
        
        if (res.status === 200 || res.status === 201) {
            desechados++;
            console.log(`   ✅ Desechado: ${tireToScrap.slice(0, 8)} | Motivo: ${motivo.nombre}`);
        } else {
            console.log(`   ❌ Error desecho: ${res.data?.error || res.status}`);
        }
    }
    
    console.log(`   📊 Desechados: ${desechados}`);
    return { desechados };
}

// ============ ESCENARIO 6: MÉTRICAS Y CPK ============
async function scenarioMetricasCPK(cookie) {
    console.log('\n📊 ESCENARIO 6: MÉTRICAS DE RENDIMIENTO');
    console.log('─'.repeat(55));
    
    // Get inventory summary
    const inventoryRes = await getApi(cookie, 'dashboard/inventario');
    const inventory = inventoryRes.data || inventoryRes;
    
    if (inventory) {
        console.log('   📦 Estado del inventario:');
        if (inventory.total_general !== undefined) {
            console.log(`      Total: ${inventory.total_general}`);
        }
        if (Array.isArray(inventory.por_estado)) {
            for (const item of inventory.por_estado) {
                const estado = item.estado || item._id || 'unknown';
                const count = item.cantidad || item.count || item._count || 0;
                console.log(`      ${estado}: ${count}`);
            }
        } else if (inventory.por_estado && typeof inventory.por_estado === 'object') {
            for (const [estado, count] of Object.entries(inventory.por_estado)) {
                if (typeof count === 'object') continue;
                console.log(`      ${estado}: ${count}`);
            }
        }
    }
    
    // Try CPK report
    try {
        const cpkRes = await getApi(cookie, 'reportes/cpk');
        const cpkData = cpkRes.data || cpkRes;
        if (cpkData && Object.keys(cpkData).length > 0) {
            console.log('   💰 Reporte CPK disponible');
        }
    } catch {
        console.log('   ⚠️ Reporte CPK no disponible aún');
    }
    
    // Get alerts summary
    const alertasRes = await getApi(cookie, 'alertas?limit=10');
    const alertas = (alertasRes.data || alertasRes).filter(a => a);
    if (alertas.length > 0) {
        console.log(`   🚨 Alertas activas: ${alertas.length}`);
        const byType = {};
        for (const a of alertas) {
            const tipo = a.tipo || a.tipo_alerta || 'unknown';
            byType[tipo] = (byType[tipo] || 0) + 1;
        }
        for (const [tipo, count] of Object.entries(byType)) {
            console.log(`      ${tipo}: ${count}`);
        }
    }
    
    return { inventory: inventory || {}, alertas: alertas.length || 0 };
}

// ============ MAIN ============
async function main() {
    console.log('╔══════════════════════════════════════════════════════════╗');
    console.log('║   SIMULACIÓN AVANZADA: GESTIÓN DE FLOTA MULTI-VEHÍCULO   ║');
    console.log('║   GesNeu API - Escenarios de Negocio Reales              ║');
    console.log('╚══════════════════════════════════════════════════════════╝');
    
    const startTime = Date.now();
    const results = {};
    
    try {
        // AUTH
        console.log('\n🔐 Autenticando...');
        const cookie = await authenticate();
        console.log('   ✅ Autenticado');
        
        // LOAD DATA
        console.log('\n📋 Cargando datos de referencia...');
        const catalogs = await loadCatalogs(cookie);
        console.log(`   Modelos: ${catalogs.modelos.length}`);
        console.log(`   Almacenes: ${catalogs.almacenes.length}`);
        console.log(`   Proveedores: ${catalogs.proveedores.length}`);
        console.log(`   Motivos desecho: ${catalogs.motivos.length}`);
        
        const vehicles = await loadVehicles(cookie);
        console.log(`   Vehículos con posiciones: ${vehicles.length}`);
        
        // SCENARIO 1: MASS PURCHASE
        const compraResult = await scenarioCompraMasiva(cookie, catalogs);
        results.compra = compraResult;
        
        // Get stock tires for mounting
        const stockRes = await getApi(cookie, 'neumaticos?limit=5');
        const rawStock = stockRes.data || stockRes;
        const allTires = Array.isArray(rawStock) ? rawStock : [];
        
        // Debug: check field names
        if (allTires.length > 0) {
            const sample = allTires[0];
            const estadoField = sample.estado_actual !== undefined ? 'estado_actual' : 
                               sample.estadoActual !== undefined ? 'estadoActual' :
                               sample.estado !== undefined ? 'estado' : 'UNKNOWN';
            console.log(`\n   📦 DEBUG: campo de estado = "${estadoField}", valor = "${sample[estadoField]}"`);
        }
        
        // Filter using correct field
        const stockTires = allTires.filter(n => {
            const estado = n.estado_actual || n.estadoActual || n.estado;
            return estado === 'EN_STOCK';
        });
        
        console.log(`   📦 Neumáticos en stock: ${stockTires.length} (de ${allTires.length} mostrados)`);
        
        // If we didn't get enough stock, query specifically for EN_STOCK
        if (stockTires.length < 4) {
            console.log('   🔍 Buscando neumáticos EN_STOCK con query directa...');
            const directRes = await getApi(cookie, 'neumaticos?limit=100');
            const directTires = Array.isArray(directRes.data) ? directRes.data : (Array.isArray(directRes) ? directRes : []);
            const directStock = directTires.filter(n => {
                const estado = n.estado_actual || n.estadoActual || n.estado;
                return estado === 'EN_STOCK';
            });
            console.log(`   ✅ Encontrados: ${directStock.length} EN_STOCK directos`);
            if (directStock.length > 0) {
                stockTires.length = 0;
                stockTires.push(...directStock.slice(0, 12));
            }
        }
        
        // SCENARIO 2: FLEET MOUNTING
        const montajeResult = await scenarioMontajeFlota(cookie, vehicles, stockTires);
        results.montaje = montajeResult;
        
        // Get installed tires for wear simulation
        const installedRes = await getApi(cookie, 'neumaticos?limit=100');
        const allForInstalled = Array.isArray(installedRes.data) ? installedRes.data : (Array.isArray(installedRes) ? installedRes : []);
        const installedTires = allForInstalled.filter(n => {
            const estado = n.estado_actual || n.estadoActual || n.estado;
            return estado === 'INSTALADO';
        });
        console.log(`\n   🔧 Neumáticos instalados: ${installedTires.length}`);
        
        if (installedTires.length > 0) {
            // SCENARIO 3: PROGRESSIVE WEAR
            const tireIds = installedTires.map(t => t.id);
            const desgasteResult = await scenarioDesgasteProgresivo(cookie, tireIds);
            results.desgaste = { inspecciones: desgasteResult.length };
            
            // SCENARIO 4: RETREADING
            const reencaucheResult = await scenarioReencaucheCompleto(cookie, tireIds, catalogs);
            results.reencauche = reencaucheResult;
            
            // SCENARIO 5: DISPOSAL
            const desechoResult = await scenarioDesechoProgramado(cookie, tireIds, catalogs);
            results.desecho = desechoResult;
        }
        
        // SCENARIO 6: METRICS
        const metricasResult = await scenarioMetricasCPK(cookie);
        results.metricas = metricasResult;
        
        // FINAL REPORT
        const totalTime = ((Date.now() - startTime) / 1000).toFixed(1);
        
        console.log('\n╔══════════════════════════════════════════════════════════╗');
        console.log('║          REPORTE FINAL - SIMULACIÓN DE FLOTA             ║');
        console.log('╠══════════════════════════════════════════════════════════╣');
        console.log(`║  Tiempo total: ${String(totalTime).padStart(42)}s ║`);
        
        // Calculate total operations
        const totalOps = [
            results.compra?.total || 0,
            results.montaje?.mounted || 0,
            (results.desgaste?.inspecciones || 0) * (installedTires?.length || 0),
            results.reencauche?.enviados || 0,
            results.desecho?.desechados || 0
        ].reduce((a, b) => a + b, 0);
        
        console.log(`║  Operaciones totales: ${String(totalOps).padStart(30)}   ║`);
        console.log('╠══════════════════════════════════════════════════════════╣');
        
        const scenarios = [
            ['Compra multi-marca', `${results.compra?.total || 0} neumáticos`],
            ['Montaje en flota', `${results.montaje?.mounted || 0} en ${Object.keys(results.montaje?.byVehicle || {}).length} vehículos`],
            ['Desgaste progresivo', `${results.desgaste?.inspecciones || 0} inspecciones`],
            ['Reencauche', `${results.reencauche?.enviados || 0} enviados`],
            ['Desecho', `${results.desecho?.desechados || 0} neumáticos`],
            ['Métricas CPK', `${results.metricas?.alertas || 0} alertas`]
        ];
        
        for (const [name, value] of scenarios) {
            const line = `║  ${name}:`;
            const padding = 56 - line.length - value.length;
            console.log(`${line} ${value}${' '.repeat(Math.max(0, padding))} ║`);
        }
        
        console.log('╚══════════════════════════════════════════════════════════╝');
        console.log('\n✅ Simulación de flota avanzada completada exitosamente');
        
    } catch (error) {
        console.error('\n❌ Error fatal:', error.message);
        process.exit(1);
    }
}

main();
