/**
 * SIMULACIÓN COMPLETA DEL CICLO DE VIDA DE NEUMÁTICOS
 * 
 * Escenarios simulados:
 * 1. COMPRA -> Creación de neumáticos en stock
 * 2. MONTAJE -> Instalación en vehículo
 * 3. INSPECCIÓN -> Lectura de presión/profundidad
 * 4. ROTACIÓN -> Cambio de posición
 * 5. DESMONTAJE -> Retiro del vehículo
 * 6. REENCAUCHE -> Envío y retorno de reencauche
 * 7. ALERTAS -> Generación automática por umbrales
 * 8. DESECHO -> Fin de vida útil
 * 
 * Uso: node scripts/simulacion-ciclo-vida.js
 */

const BASE_URL = process.env.BASE_URL || 'http://localhost:3005';
const USERNAME = process.env.STRESS_USER || 'admin';
const PASSWORD = process.env.STRESS_PASSWORD || 'admin123';

// ============ AUTH ============
async function authenticate() {
    // Get CSRF token
    const csrfRes = await fetch(`${BASE_URL}/api/auth/csrf`);
    const { csrfToken } = await csrfRes.json();
    const cookies = csrfRes.headers.get('set-cookie');
    
    // Login with correct NextAuth Credentials format
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

// ============ SCENARIO 1: COMPRA ============
async function scenarioCompra(cookie, modeloId, almacenId, proveedorId) {
    console.log('\n📦 ESCENARIO 1: COMPRA DE NEUMÁTICOS');
    console.log('─'.repeat(50));
    
    const series = [];
    const created = [];
    
    for (let i = 0; i < 5; i++) {
        series.push(`PURCHASE-${Date.now()}-${i}`);
    }
    
    let successCount = 0;
    for (const serie of series) {
        const res = await fetch(`${BASE_URL}/api/v1/neumaticos`, {
            method: 'POST',
            headers: authHeaders(cookie),
            body: JSON.stringify({
                modelo_id: modeloId,
                proveedor_compra_id: proveedorId,
                ubicacion_almacen_id: almacenId,
                numero_serie: serie,
                dot: '2425',
                profundidad_inicial_mm: 18,
                costo_compra: 250 + Math.random() * 50,
                fecha_compra: new Date().toISOString(),
                es_reencauchado: false,
                moneda_compra: 'PEN'
            })
        });
        
        const data = await res.json();
        if (res.status === 201) {
            created.push(data.data || data);
            successCount++;
            console.log(`   ✅ Creado: ${serie}`);
        } else {
            console.log(`   ❌ Falló ${serie}: ${data.error || res.status}`);
        }
    }
    
    console.log(`   📊 Resultado: ${successCount}/${series.length} creados`);
    return created;
}

// ============ SCENARIO 2: MONTAJE ============
async function scenarioMontaje(cookie, neumaticos, vehiculoId, posiciones) {
    console.log('\n🔧 ESCENARIO 2: MONTAJE EN VEHÍCULO');
    console.log('─'.repeat(50));
    
    let successCount = 0;
    const mounted = [];
    
    for (let i = 0; i < Math.min(neumaticos.length, posiciones.length); i++) {
        const neum = neumaticos[i];
        const neumId = neum.id || neum.neumatico_id;
        const posId = posiciones[i];
        
        const res = await fetch(`${BASE_URL}/api/v1/operaciones/montaje`, {
            method: 'POST',
            headers: authHeaders(cookie),
            body: JSON.stringify({
                neumatico_id: neumId,
                vehiculo_id: vehiculoId,
                posicion_id: posId,
                contador_vehiculo: 50000,
                profundidad_mm: parseFloat((17 + Math.random() * 2).toFixed(1)),
                presion_psi: parseFloat((100 + Math.random() * 15).toFixed(1)),
                observaciones: `Montaje simulacion posicion ${i + 1}`
            })
        });
        
        const data = await res.json();
        if (res.status === 200 || res.status === 201) {
            mounted.push(neumId);
            successCount++;
            console.log(`   ✅ Montado ${neumId?.slice(0, 8)}... en posición ${posId?.slice(0, 8)}...`);
        } else {
            const errMsg = data.details ? JSON.stringify(data.details) : data.error || res.status;
            console.log(`   ❌ Falló montaje ${neumId?.slice(0, 8)}: ${res.status} - ${String(errMsg).slice(0, 250)}`);
            console.log(`      Full response: ${JSON.stringify(data).slice(0, 300)}`);
        }
    }
    
    console.log(`   📊 Resultado: ${successCount}/${neumaticos.length} montados`);
    return mounted;
}

// ============ SCENARIO 3: INSPECCIÓN ============
async function scenarioInspeccion(cookie, neumaticoIds, kilometraje) {
    console.log('\n🔍 ESCENARIO 3: INSPECCIÓN DE NEUMÁTICOS');
    console.log('─'.repeat(50));
    
    let successCount = 0;
    const alertas = [];
    
    for (const neumId of neumaticoIds) {
        // Simulate varying conditions
        const presion = 70 + Math.random() * 50; // 70-120 PSI
        const profundidad = 3 + Math.random() * 14; // 3-17mm
        
        const res = await fetch(`${BASE_URL}/api/v1/neumaticos/eventos`, {
            method: 'POST',
            headers: authHeaders(cookie),
            body: JSON.stringify({
                tipo_evento: 'INSPECCION',
                neumatico_id: neumId,
                fecha_evento: new Date().toISOString(),
                contador_vehiculo: kilometraje,
                profundidad_remanente: parseFloat(profundidad.toFixed(1)),
                presion_psi: parseFloat(presion.toFixed(1)),
                observaciones: `Inspeccion simulada - PSI: ${presion.toFixed(1)}, Prof: ${profundidad.toFixed(1)}`
            })
        });
        
        const data = await res.json();
        if (res.status === 200 || res.status === 201) {
            successCount++;
            const condition = presion < 80 ? '⚠️ BAJA PRESIÓN' : 
                            profundidad < 4 ? '🚨 PROFUNDIDAD CRÍTICA' : '✅ OK';
            console.log(`   ${condition} | Neum ${neumId?.slice(0, 8)}... | ${presion.toFixed(1)} PSI | ${profundidad.toFixed(1)}mm`);
            
            if (data.data?.alertas?.length > 0) {
                alertas.push(...data.data.alertas);
            }
        } else {
            console.log(`   ❌ Falló inspección ${neumId?.slice(0, 8)}: ${data.error || res.status}`);
        }
    }
    
    console.log(`   📊 Resultado: ${successCount}/${neumaticoIds.length} inspeccionadas`);
    if (alertas.length > 0) {
        console.log(`   🚨 Alertas generadas: ${alertas.length}`);
    }
    
    return { successCount, alertas };
}

// ============ SCENARIO 4: ROTACIÓN ============
async function scenarioRotacion(cookie, vehiculoId, movimientos, kilometraje) {
    console.log('\n🔄 ESCENARIO 4: ROTACIÓN DE POSICIONES');
    console.log('─'.repeat(50));
    
    if (movimientos.length < 2) {
        console.log('   ⚠️ Se necesitan al menos 2 movimientos para rotar');
        return 0;
    }
    
    const res = await fetch(`${BASE_URL}/api/v1/operaciones/rotacion`, {
        method: 'POST',
        headers: authHeaders(cookie),
        body: JSON.stringify({
            vehiculo_id: vehiculoId,
            contador_vehiculo: kilometraje,
            movimientos: movimientos,
            observaciones: 'Rotación simulación ciclo de vida'
        })
    });
    
    const data = await res.json();
    if (res.status === 200 || res.status === 201) {
        const result = data.data || data;
        const processed = result.movimientos_procesados || movimientos.length;
        console.log(`   ✅ Rotación completada: ${processed} neumáticos reubicados`);
        console.log(`   📋 Eventos creados: ${Array.isArray(result.eventos_creados) ? result.eventos_creados.length : 'N/A'}`);
        return processed;
    } else {
        console.log(`   ❌ Falló rotación: ${res.status} - ${data.error || JSON.stringify(data.details || data).slice(0, 200)}`);
        return 0;
    }
}

// ============ SCENARIO 5: DESMONTAJE ============
async function scenarioDesmontaje(cookie, neumaticoIds, kilometraje, destino = 'STOCK', almacenDestinoId = null) {
    console.log('\n📤 ESCENARIO 5: DESMONTAJE DE NEUMÁTICOS');
    console.log('─'.repeat(50));
    
    let successCount = 0;
    
    for (const neumId of neumaticoIds) {
        const body = {
            neumatico_id: neumId,
            destino,
            kilometraje_vehiculo: kilometraje,
            observaciones: 'Desmontaje simulación'
        };
        
        if (destino === 'STOCK' && almacenDestinoId) {
            body.almacen_destino_id = almacenDestinoId;
        }
        
        const res = await fetch(`${BASE_URL}/api/v1/operaciones/desmontaje`, {
            method: 'POST',
            headers: authHeaders(cookie),
            body: JSON.stringify(body)
        });
        
        const data = await res.json();
        if (res.status === 200 || res.status === 201) {
            successCount++;
            console.log(`   ✅ Desmontado ${neumId?.slice(0, 8)}... -> ${destino}`);
        } else {
            console.log(`   ❌ Falló desmontaje ${neumId?.slice(0, 8)}: ${data.error || res.status}`);
        }
    }
    
    console.log(`   📊 Resultado: ${successCount}/${neumaticoIds.length} desmontados`);
    return successCount;
}

// ============ SCENARIO 6: REENCAUCHE ============
async function scenarioReencauche(cookie, neumaticoIds, proveedorId) {
    console.log('\n🏭 ESCENARIO 6: ENVÍO A REENCAUCHE');
    console.log('─'.repeat(50));
    
    let successCount = 0;
    
    for (const neumId of neumaticoIds) {
        const res = await fetch(`${BASE_URL}/api/v1/reencauche`, {
            method: 'POST',
            headers: authHeaders(cookie),
            body: JSON.stringify({
                neumatico_id: neumId,
                proveedor_reencauchador_id: proveedorId,
                observaciones: 'Envío a reencauche simulación'
            })
        });
        
        const data = await res.json();
        if (res.status === 200 || res.status === 201) {
            successCount++;
            console.log(`   ✅ Enviado a reencauche: ${neumId?.slice(0, 8)}...`);
        } else {
            console.log(`   ❌ Falló envío reencauche ${neumId?.slice(0, 8)}: ${data.error || res.status}`);
        }
    }
    
    console.log(`   📊 Resultado: ${successCount}/${neumaticoIds.length} enviados`);
    return successCount;
}

// ============ SCENARIO 7: DESECHO ============
async function scenarioDesecho(cookie, neumaticoIds, motivoId) {
    console.log('\n🗑️ ESCENARIO 7: DESECHO DE NEUMÁTICOS');
    console.log('─'.repeat(50));
    
    let successCount = 0;
    
    for (const neumId of neumaticoIds) {
        const res = await fetch(`${BASE_URL}/api/v1/neumaticos/eventos`, {
            method: 'POST',
            headers: authHeaders(cookie),
            body: JSON.stringify({
                tipo_evento: 'DESECHO',
                neumatico_id: neumId,
                motivo_desecho_id: motivoId,
                observaciones: 'Desecho por simulación de ciclo completo'
            })
        });
        
        const data = await res.json();
        if (res.status === 200 || res.status === 201) {
            successCount++;
            console.log(`   ✅ Desechado: ${neumId?.slice(0, 8)}...`);
        } else {
            console.log(`   ❌ Falló desecho ${neumId?.slice(0, 8)}: ${data.error || res.status}`);
        }
    }
    
    console.log(`   📊 Resultado: ${successCount}/${neumaticoIds.length} desechados`);
    return successCount;
}

// ============ SETUP HELPERS ============
async function getCatalogData(cookie, endpoint) {
    const res = await fetch(`${BASE_URL}/api/v1/catalogos/${endpoint}`, {
        headers: authHeaders(cookie)
    });
    const data = await res.json();
    return data.data || data.items || data;
}

async function findFirstVehicle(cookie) {
    const res = await fetch(`${BASE_URL}/api/v1/vehiculos`, {
        headers: authHeaders(cookie)
    });
    const data = await res.json();
    const vehicles = data.data || data;
    return Array.isArray(vehicles) && vehicles.length > 0 ? vehicles[0] : null;
}

async function findMotivoDesecho(cookie) {
    const res = await fetch(`${BASE_URL}/api/v1/catalogos/motivos-desecho`, {
        headers: authHeaders(cookie)
    });
    const data = await res.json();
    const motivos = data.data || data;
    return Array.isArray(motivos) && motivos.length > 0 ? motivos[0].id : null;
}

async function getVehiculoMontajePositions(vehiculoId, cookie) {
    const res = await fetch(`${BASE_URL}/api/v1/vehiculos/${vehiculoId}/montaje`, {
        headers: authHeaders(cookie)
    });
    const data = await res.json();
    
    // Response structure: { data: { ejes: [{ posiciones: [{id, ocupada, ...}] }] } }
    const ejes = data.data?.ejes || [];
    const positions = [];
    
    for (const eje of ejes) {
        const ejePositions = eje.posiciones || [];
        for (const pos of ejePositions) {
            if (!pos.ocupada) {
                positions.push(pos.id);
            }
        }
    }
    
    return positions;
}

// ============ MAIN ============
async function main() {
    console.log('╔══════════════════════════════════════════════════════════╗');
    console.log('║   SIMULACIÓN COMPLETA - CICLO DE VIDA DE NEUMÁTICOS      ║');
    console.log('║   GesNeu API - Pruebas Reales                            ║');
    console.log('╚══════════════════════════════════════════════════════════╝');
    
    const startTime = Date.now();
    
    try {
        // AUTH
        console.log('\n🔐 Autenticando...');
        const cookie = await authenticate();
        console.log('   ✅ Autenticado exitosamente');
        
        // LOAD CATALOGS
        console.log('\n📋 Cargando catálogos...');
        const modelos = await getCatalogData(cookie, 'modelos-neumatico');
        let almacenes = await getCatalogData(cookie, 'almacenes');
        let proveedores = await getCatalogData(cookie, 'proveedores');
        
        // Create almacén if missing
        if (!Array.isArray(almacenes) || almacenes.length === 0) {
            console.log('   🏗️ Creando almacén...');
            const createRes = await fetch(`${BASE_URL}/api/v1/catalogos/almacenes`, {
                method: 'POST',
                headers: authHeaders(cookie),
                body: JSON.stringify({
                    codigo: `ALM-SIM-${Date.now()}`.substring(0, 20),
                    nombre: 'Almacen Simulacion',
                    tipo: 'PRINCIPAL'
                })
            });
            const createData = await createRes.json();
            console.log(`   DEBUG Almacén response (${createRes.status}): ${JSON.stringify(createData)}`);
            const almacenCreated = createData.data || createData;
            almacenes = [almacenCreated];
            console.log(`   ✅ Almacén creado: ${almacenCreated?.nombre || almacenCreated?.id?.slice(0, 8) || 'unknown'}`);
        }
        
        // Create proveedor if missing
        if (!Array.isArray(proveedores) || proveedores.length === 0) {
            console.log('   🏗️ Creando proveedor...');
            const createRes = await fetch(`${BASE_URL}/api/v1/catalogos/proveedores`, {
                method: 'POST',
                headers: authHeaders(cookie),
                body: JSON.stringify({
                    tipo: 'FABRICANTE',
                    nombre: `Proveedor Sim ${Date.now()}`.substring(0, 30),
                    ruc: `SIM${Date.now()}`.substring(0, 20)
                })
            });
            const createData = await createRes.json();
            console.log(`   DEBUG Proveedor response (${createRes.status}): ${JSON.stringify(createData)}`);
            const proveedorCreated = createData.data || createData;
            proveedores = [proveedorCreated];
            console.log(`   ✅ Proveedor creado: ${proveedorCreated?.nombre || proveedorCreated?.id?.slice(0, 8) || 'unknown'}`);
        }
        
        const modelo = Array.isArray(modelos) ? modelos[0] : modelos?.[0];
        const almacen = Array.isArray(almacenes) ? almacenes[0] : almacenes?.[0];
        const proveedor = Array.isArray(proveedores) ? proveedores[0] : proveedores?.[0];
        
        if (!modelo?.id || !almacen?.id || !proveedor?.id) {
            console.log('   ❌ Datos de catálogo insuficientes. Ejecute seed_stress.ts primero.');
            console.log(`   Modelos: ${modelo?.id || 'N/A'}`);
            console.log(`   Almacenes: ${almacen?.id || 'N/A'}`);
            console.log(`   Proveedores: ${proveedor?.id || 'N/A'}`);
            return;
        }
        
        console.log(`   ✅ Modelo: ${modelo.nombre_modelo || modelo.id.slice(0, 8)}`);
        console.log(`   ✅ Almacén: ${almacen.nombre || almacen.codigo || almacen.id.slice(0, 8)}`);
        console.log(`   ✅ Proveedor: ${proveedor.nombre || proveedor.id.slice(0, 8)}`);
        
        // LOAD VEHICLE
        console.log('\n🚗 Buscando vehículo...');
        const vehiculo = await findFirstVehicle(cookie);
        if (!vehiculo) {
            console.log('   ❌ No se encontraron vehículos. Ejecute seed_stress.ts primero.');
            return;
        }
        console.log(`   ✅ Vehículo: ${vehiculo.placa || vehiculo.id.slice(0, 8)}`);
        
        // Get available positions
        let availablePositions = await getVehiculoMontajePositions(vehiculo.id, cookie);
        console.log(`   Posiciones disponibles: ${availablePositions.length}`);
        
        // If no positions available, create axle config
        if (availablePositions.length === 0) {
            console.log('   🏗️ Configurando ejes del vehículo (2 ejes simples)...');
            
            // Create axle 1: Direccion (2 positions)
            const eje1Res = await fetch(`${BASE_URL}/api/v1/catalogos/configuraciones-eje`, {
                method: 'POST',
                headers: authHeaders(cookie),
                body: JSON.stringify({
                    tipo_vehiculo_id: vehiculo.tipo_vehiculo_id,
                    numero_eje: 1,
                    nombre_eje: 'Direccional',
                    tipo_eje: 'DIRECCION',
                    numero_posiciones: 2,
                    posiciones_duales: false,
                    permite_reencauchados: false,
                    posiciones: [
                        { codigo_posicion: '1I', lado: 'IZQUIERDO', posicion_relativa: 1, es_direccion: true },
                        { codigo_posicion: '1D', lado: 'DERECHO', posicion_relativa: 1, es_direccion: true }
                    ]
                })
            });
            const eje1Data = await eje1Res.json();
            console.log(`   ✅ Eje 1 (Direccional): ${eje1Res.status === 201 ? 'Creado' : JSON.stringify(eje1Data).slice(0, 150)}`);
            
            // Create axle 2: Traccion (2 positions)
            const eje2Res = await fetch(`${BASE_URL}/api/v1/catalogos/configuraciones-eje`, {
                method: 'POST',
                headers: authHeaders(cookie),
                body: JSON.stringify({
                    tipo_vehiculo_id: vehiculo.tipo_vehiculo_id,
                    numero_eje: 2,
                    nombre_eje: 'Traccion',
                    tipo_eje: 'TRACCION',
                    numero_posiciones: 2,
                    posiciones_duales: false,
                    posiciones: [
                        { codigo_posicion: '2I', lado: 'IZQUIERDO', posicion_relativa: 1, es_traccion: true },
                        { codigo_posicion: '2D', lado: 'DERECHO', posicion_relativa: 1, es_traccion: true }
                    ]
                })
            });
            const eje2Data = await eje2Res.json();
            console.log(`   ✅ Eje 2 (Tracción): ${eje2Res.status === 201 ? 'Creado' : JSON.stringify(eje2Data).slice(0, 150)}`);
            
            // Now get positions again
            availablePositions = await getVehiculoMontajePositions(vehiculo.id, cookie);
            console.log(`   ✅ Posiciones disponibles: ${availablePositions.length}`);
        }
        
        // ===== EXECUTE SCENARIOS =====
        const results = {};
        
        // SCENARIO 1: PURCHASE
        const neumáticosComprados = await scenarioCompra(
            cookie, modelo.id, almacen.id, proveedor.id
        );
        results.compra = { creados: neumáticosComprados.length };
        
        if (neumáticosComprados.length === 0) {
            console.log('\n⚠️ Sin neumáticos para continuar con los escenarios.');
            return;
        }
        
        // SCENARIO 2: MOUNT
        const positionsToUse = availablePositions.slice(0, neumáticosComprados.length);
        const neumáticosMontados = await scenarioMontaje(
            cookie, neumáticosComprados, vehiculo.id, positionsToUse
        );
        results.montaje = { montados: neumáticosMontados.length };
        
        // SCENARIO 3: INSPECTION
        const inspeccionKm = 55000;
        const { successCount: inspCount, alertas } = await scenarioInspeccion(
            cookie, neumáticosMontados, inspeccionKm
        );
        results.inspeccion = { inspeccionados: inspCount, alertas: alertas.length };
        
        // SCENARIO 4: ROTATION
        if (neumáticosMontados.length >= 2 && positionsToUse.length >= 2) {
            // Create swap movements: tire at pos0 -> pos1, tire at pos1 -> pos0
            const movimientos = [];
            for (let i = 0; i < Math.min(neumáticosMontados.length, positionsToUse.length); i++) {
                const nextPos = (i + 1) % Math.min(neumáticosMontados.length, positionsToUse.length);
                movimientos.push({
                    neumatico_id: neumáticosMontados[i],
                    posicion_destino_id: positionsToUse[nextPos]
                });
            }
            
            const rotados = await scenarioRotacion(
                cookie, vehiculo.id, movimientos, 60000
            );
            results.rotacion = { rotados };
        }
        
        // SCENARIO 3b: SECOND INSPECTION (after rotation)
        const insp2 = await scenarioInspeccion(
            cookie, neumáticosMontados, 65000
        );
        results['inspeccion_post_rotacion'] = { 
            inspeccionados: insp2.successCount, 
            alertas: insp2.alertas.length 
        };
        
        // SCENARIO 5: DISMOUNT
        const desmontados = await scenarioDesmontaje(
            cookie, neumáticosMontados.slice(0, 2), 70000, 'STOCK', almacen.id
        );
        results.desmontaje = { desmontados };
        
        // SCENARIO 7: DISPOSAL (for the dismounted tires with low tread simulation)
        const motivoDesecho = await findMotivoDesecho(cookie);
        if (motivoDesecho) {
            const desechados = await scenarioDesecho(
                cookie, neumáticosMontados.slice(0, 1), motivoDesecho
            );
            results.desecho = { desechados };
        }
        
        // ===== FINAL REPORT =====
        const totalTime = ((Date.now() - startTime) / 1000).toFixed(1);
        
        console.log('\n╔══════════════════════════════════════════════════════════╗');
        console.log('║                REPORTE FINAL DE SIMULACIÓN               ║');
        console.log('╠══════════════════════════════════════════════════════════╣');
        
        const totalOps = Object.values(results).reduce((sum, r) => {
            return sum + Object.values(r).reduce((s, v) => s + (typeof v === 'number' ? v : 0), 0);
        }, 0);
        
        console.log(`║  Tiempo total: ${totalTime.padStart(42)}s ║`);
        console.log(`║  Operaciones totales: ${String(totalOps).padStart(30)}   ║`);
        console.log('╠══════════════════════════════════════════════════════════╣');
        
        for (const [scenario, data] of Object.entries(results)) {
            const summary = Object.entries(data)
                .map(([k, v]) => `${k}: ${v}`)
                .join(', ');
            const label = `║  ${scenario}:`;
            const value = summary;
            const padding = 56 - label.length - value.length;
            console.log(`${label} ${value}${' '.repeat(Math.max(0, padding))} ║`);
        }
        
        console.log('╚══════════════════════════════════════════════════════════╝');
        console.log('\n✅ Simulación completa exitosamente');
        
    } catch (error) {
        console.error('\n❌ Error fatal:', error.message);
        console.error(error.stack);
        process.exit(1);
    }
}

main();
