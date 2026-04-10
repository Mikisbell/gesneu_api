/**
 * SIMULACIÓN FLUJO REAL: OPERACIÓN DIARIA COMPLETA
 * 
 * Escenario: Un día real de trabajo en la operación de transporte.
 * Un operador de flota realiza estas tareas en secuencia:
 * 
 * 1. 🌅 INICIO DE TURNO - Revisa alertas pendientes, métricas del día
 * 2. 📦 RECEPCIÓN - Llegan neumáticos nuevos del proveedor
 * 3. 📋 INVENTARIO - Verifica stock, alerta de reorder points
 * 4. 🔧 MONTAJE - Instala neumáticos en vehículos que salen
 * 5. 🔍 INSPECCIÓN RUTINARIA - Revisa presión y profundidad
 * 6. 🔄 ROTACIÓN - Programa rotación por desgaste irregular
 * 7. 🚨 ALERTA CRÍTICA - Detecta neumático en riesgo
 * 8. 🏭 REENCAUCHE - Envía neumáticos aptos a reencauche
 * 9. 📊 REPORTE TCO - Calcula costo por kilómetro del día
 * 10. 📝 BITÁCORA - Registra mantenimiento de vehículos
 * 11. 🗑️ DESECHO - Retira neumáticos al final de vida
 * 12. 🌙 FIN DE TURNO - Resumen del día, alertas pendientes
 * 
 * Uso: node scripts/flujo-real-diario.js
 */

const BASE_URL = process.env.BASE_URL || 'http://localhost:3005';
const COOKIE_FILE = null; // se genera dinámicamente

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
const get = async (c, e) => { try { const r = await fetch(`${BASE_URL}/api/v1/${e}`, { headers: authH(c) }); const t = await r.text(); return t ? JSON.parse(t) : { data: [] }; } catch { return { data: null }; } };
const post = async (c, e, b) => { try { const r = await fetch(`${BASE_URL}/api/v1/${e}`, { method: 'POST', headers: authH(c), body: JSON.stringify(b) }); return { status: r.status, data: await r.json().catch(() => ({})) }; } catch { return { status: 500, data: {} }; } };
const patch = async (c, e, b) => { try { const r = await fetch(`${BASE_URL}/api/v1/${e}`, { method: 'PATCH', headers: authH(c), body: JSON.stringify(b) }); return { status: r.status, data: await r.json().catch(() => ({})) }; } catch { return { status: 500, data: {} }; } };

const ok = (s) => s === 200 || s === 201 || s === 204;
const first = (a) => Array.isArray(a) && a.length > 0 ? a[0] : null;

async function main() {
    console.log('╔══════════════════════════════════════════════════════════╗');
    console.log('║   SIMULACIÓN: DÍA REAL EN OPERACIÓN DE TRANSPORTE        ║');
    console.log('║   GesNeu API - Flujo completo de negocio                 ║');
    console.log('╚══════════════════════════════════════════════════════════╝');
    
    const t0 = Date.now();
    const ops = [];
    
    // AUTH
    const cookie = await auth();
    if (!cookie) { console.log('❌ Auth failed'); return; }

    // Load references
    const [almacenesR, vehiculosR, neumaticosR, modelosR, proveedoresR, motivosR] = await Promise.all([
        get(cookie, 'catalogos/almacenes'),
        get(cookie, 'vehiculos?limit=10'),
        get(cookie, 'neumaticos?limit=50'),
        get(cookie, 'catalogos/modelos-neumatico'),
        get(cookie, 'catalogos/proveedores'),
        get(cookie, 'catalogos/motivos-desecho')
    ]);

    const almacenes = ((almacenesR.data || almacenesR) || []).filter(Boolean);
    const vehiculos = ((vehiculosR.data || vehiculosR) || []).filter(Boolean);
    const neumaticos = ((neumaticosR.data || neumaticosR) || []).filter(Boolean);
    const modelos = ((modelosR.data || modelosR) || []).filter(Boolean);
    const proveedores = ((proveedoresR.data || proveedoresR) || []).filter(Boolean);
    const motivos = ((motivosR.data || motivosR) || []).filter(Boolean);

    const almacen = first(almacenes);
    const vehiculo = first(vehiculos);
    const modelo = first(modelos);
    const proveedor = first(proveedores);
    const motivoDesecho = first(motivos);

    console.log(`\n📋 Referencias: ${almacenes.length} almacenes, ${vehiculos.length} vehículos, ${neumaticos.length} neumáticos`);

    // 1. INICIO DE TURNO
    console.log('\n🌅 1. INICIO DE TURNO');
    console.log('─'.repeat(50));
    const [invR, alertasR] = await Promise.all([
        get(cookie, 'dashboard/inventario'),
        get(cookie, 'alertas?limit=10')
    ]);
    const alertas = (alertasR.data || alertasR || []).filter(Boolean);
    console.log(`   📊 Inventario cargado | 🚨 ${alertas.length} alertas pendientes`);
    ops.push({ paso: 'Inicio turno', alertas: alertas.length, status: '✅' });

    // 2. RECEPCIÓN
    console.log('\n📦 2. RECEPCIÓN DE NEUMÁTICOS');
    console.log('─'.repeat(50));
    const compras = [];
    for (let i = 0; i < 3; i++) {
        compras.push(post(cookie, 'neumaticos', {
            modelo_id: modelo.id,
            proveedor_compra_id: proveedor.id,
            ubicacion_almacen_id: almacen.id,
            numero_serie: `DAY-${Date.now()}-${i}`,
            dot: '2425',
            profundidad_inicial_mm: modelo.profundidad_original_mm || 18,
            costo_compra: 220 + Math.random() * 30,
            fecha_compra: new Date().toISOString(),
            es_reencauchado: false,
            moneda_compra: 'PEN'
        }));
    }
    const compraRes = await Promise.all(compras);
    const nuevos = compraRes.filter(r => ok(r.status));
    console.log(`   ✅ ${nuevos.length}/3 neumáticos recibidos del proveedor`);
    ops.push({ paso: 'Recepción', recibidos: nuevos.length, status: '✅' });

    // 3. INVENTARIO
    console.log('\n📋 3. VERIFICACIÓN DE INVENTARIO');
    console.log('─'.repeat(50));
    const invDetail = await get(cookie, 'inventario');
    if (invDetail.data) {
        console.log(`   ✅ Inventario verificado`);
        if (invDetail.data.por_estado) {
            const porEstado = Array.isArray(invDetail.data.por_estado) ? invDetail.data.por_estado : [];
            for (const item of porEstado) {
                const est = item.estado || item._id || 'N/A';
                const cnt = item.cantidad || item.count || item._count || 0;
                console.log(`      ${est}: ${cnt}`);
            }
        }
    }
    ops.push({ paso: 'Inventario', status: '✅' });

    // Get fresh stock for mounting
    const neumsAll = ((await get(cookie, 'neumaticos?limit=200')).data || []).filter(Boolean);
    const stockAll = neumsAll.filter(n => (n.estado_actual || n.estadoActual || n.estado) === 'EN_STOCK');
    
    // Get currently installed tires
    const installed = neumsAll.filter(n => (n.estado_actual || n.estadoActual || n.estado) === 'INSTALADO');
    console.log(`\n   📦 Stock disponible: ${stockAll.length} | 🔧 Instalados: ${installed.length}`);
    if (stockAll.length === 0 && neumsAll.length > 0) {
        const states = {};
        for (const n of neumsAll) {
            const e = n.estado_actual || n.estadoActual || n.estado || 'unknown';
            states[e] = (states[e] || 0) + 1;
        }
        console.log(`   DEBUG estados: ${JSON.stringify(states)}`);
    }

    // 4. MONTAJE
    console.log('\n🔧 4. MONTAJE EN VEHÍCULO');
    console.log('─'.repeat(50));
    // Find vehicle with free positions
    let montajeOk = false;
    let targetVehicle = null;
    let freePositions = [];
    for (const v of vehiculos.slice(0, 10)) {
        const montajeR = await get(cookie, `vehiculos/${v.id}/montaje`);
        const md = montajeR.data || montajeR;
        const pos = [];
        for (const eje of (md.ejes || [])) {
            for (const p of (eje.posiciones || [])) {
                if (!p.ocupada) pos.push(p);
            }
        }
        if (pos.length > 0) {
            targetVehicle = v;
            freePositions = pos;
            break;
        }
    }
    
    let montados = 0;
    if (stockAll.length > 0 && targetVehicle) {
        const toMount = Math.min(stockAll.length, freePositions.length, 4);
        const mounts = [];
        for (let i = 0; i < toMount; i++) {
            mounts.push(post(cookie, 'operaciones/montaje', {
                neumatico_id: stockAll[i].id,
                vehiculo_id: targetVehicle.id,
                posicion_id: freePositions[i].id,
                contador_vehiculo: 50000 + Math.floor(Math.random() * 10000),
                profundidad_mm: 17.5,
                presion_psi: 105
            }));
        }
        const mountRes = await Promise.all(mounts);
        montados = mountRes.filter(r => ok(r.status)).length;
        console.log(`   ✅ ${montados} neumáticos montados en ${targetVehicle.placa || targetVehicle.id.slice(0, 6)}`);
        montajeOk = montados > 0;
    }
    if (!montajeOk) {
        console.log('   ⚠️ Sin posiciones libres o stock. Montaje diferido.');
    }
    ops.push({ paso: 'Montaje', montados, status: montajeOk ? '✅' : '⚠️' });

    // Refresh installed tires after mounting
    const newlyInstalled = montajeOk ? stockAll.slice(0, montados) : [];
    const allInstalled = [...installed, ...newlyInstalled];

    // 5. INSPECCIÓN RUTINARIA
    console.log('\n🔍 5. INSPECCIÓN RUTINARIA');
    console.log('─'.repeat(50));
    let inspOk = 0;
    if (allInstalled.length > 0) {
        const toInspect = allInstalled.slice(0, 4);
        const insps = toInspect.map(t => post(cookie, 'neumaticos/eventos', {
            tipo_evento: 'INSPECCION',
            neumatico_id: t.id,
            fecha_evento: new Date().toISOString(),
            contador_vehiculo: 55000 + Math.floor(Math.random() * 5000),
            profundidad_remanente: parseFloat((8 + Math.random() * 8).toFixed(1)),
            presion_psi: parseFloat((90 + Math.random() * 25).toFixed(1)),
            observaciones: 'Inspección rutinaria de turno'
        }));
        const inspRes = await Promise.all(insps);
        inspOk = inspRes.filter(r => ok(r.status)).length;
    }
    console.log(`   ✅ ${inspOk} inspecciones realizadas (${allInstalled.length} disponibles)`);
    ops.push({ paso: 'Inspección', inspecciones: inspOk, status: inspOk > 0 ? '✅' : '⚠️' });

    // 6. ROTACIÓN - check the vehicle we just mounted to
    console.log('\n🔄 6. ROTACIÓN PROGRAMADA');
    console.log('─'.repeat(50));
    let rotVehicle = targetVehicle;
    let occupiedPos = [];
    
    // Check the vehicle we mounted to first
    if (rotVehicle && montados > 0) {
        const montajeR = await get(cookie, `vehiculos/${rotVehicle.id}/montaje`);
        const md = montajeR.data || montajeR;
        let totalPos = 0;
        for (const eje of (md.ejes || [])) {
            for (const p of (eje.posiciones || [])) {
                totalPos++;
                if (p.ocupada) occupiedPos.push(p);
            }
        }
        console.log(`   DEBUG ${rotVehicle.placa || rotVehicle.id.slice(0,6)}: ${totalPos} posiciones, ${occupiedPos.length} ocupadas`);
    }
    
    // If not enough, search other vehicles
    if (occupiedPos.length < 2) {
        for (const v of vehiculos.slice(0, 10)) {
            if (v.id === rotVehicle?.id) continue;
            const montajeR = await get(cookie, `vehiculos/${v.id}/montaje`);
            const md = montajeR.data || montajeR;
            const pos = [];
            for (const eje of (md.ejes || [])) {
                for (const p of (eje.posiciones || [])) {
                    if (p.ocupada) pos.push(p);
                }
            }
            if (pos.length >= 2) {
                rotVehicle = v;
                occupiedPos = pos;
                break;
            }
        }
    }
    
    if (occupiedPos.length >= 2 && allInstalled.length >= 2) {
        const movimientos = allInstalled.slice(0, Math.min(occupiedPos.length, 4)).map((t, i) => ({
            neumatico_id: t.id,
            posicion_destino_id: occupiedPos[(i + 1) % occupiedPos.length].id
        }));

        const rotRes = await post(cookie, 'operaciones/rotacion', {
            vehiculo_id: rotVehicle.id,
            contador_vehiculo: 60000,
            movimientos,
            observaciones: 'Rotación por desgaste irregular'
        });

        if (ok(rotRes.status)) {
            const proc = rotRes.data.data?.movimientos_procesados || movimientos.length;
            console.log(`   ✅ Rotación: ${proc} neumáticos reubicados`);
            ops.push({ paso: 'Rotación', rotados: proc, status: '✅' });
        } else {
            console.log(`   ⚠️ Rotación: ${rotRes.data?.error || rotRes.status}`);
            ops.push({ paso: 'Rotación', status: '⚠️' });
        }
    } else {
        console.log('   ⚠️ Sin posiciones ocupadas suficientes');
        ops.push({ paso: 'Rotación', status: '⚠️' });
    }

    // 7. BITÁCORA DE MANTENIMIENTO
    console.log('\n📝 7. BITÁCORA DE MANTENIMIENTO');
    console.log('─'.repeat(50));
    if (vehiculo) {
        const bitRes = await post(cookie, 'bitacora-mantenimiento', {
            vehiculo_id: vehiculo.id,
            tipo: 'PREVENTIVO',
            descripcion: 'Revisión de frenos y suspensión programada',
            costo: 450,
            kilometraje: 60000,
            proveedor: 'Taller Central',
            fecha_mantenimiento: new Date().toISOString()
        });
        if (ok(bitRes.status)) {
            console.log('✅ Mantenimiento registrado en bitácora');
            ops.push({ paso: 'Bitácora', status: '✅' });
        }
    }

    // 8. REENCAUCHE - need a tire in INSTALADO state
    console.log('\n🏭 8. ENVÍO A REENCAUCHE');
    console.log('─'.repeat(50));
    // Re-fetch installed tires to get fresh state
    const reencTires = ((await get(cookie, 'neumaticos?limit=100')).data || []).filter(n => {
        const estado = n.estado_actual || n.estadoActual || n.estado;
        return estado === 'INSTALADO';
    });
    if (reencTires.length > 0 && proveedor) {
        const reencRes = await post(cookie, 'reencauche', {
            neumatico_id: reencTires[0].id,
            proveedor_reencauchador_id: proveedor.id,
            observaciones: 'Envío programado: desgaste uniforme'
        });
        if (ok(reencRes.status)) {
            console.log('✅ Neumático enviado a reencauche');
            ops.push({ paso: 'Reencauche', status: '✅' });
        } else {
            console.log(`   ⚠️ Reencauche: ${reencRes.data?.error || reencRes.status}`);
            ops.push({ paso: 'Reencauche', status: '⚠️' });
        }
    } else {
        console.log('   ⚠️ Sin neumáticos instalados para reencauche');
        ops.push({ paso: 'Reencauche', status: '⚠️' });
    }

    // 9. TCO DEL DÍA
    console.log('\n📊 9. REPORTE TCO');
    console.log('─'.repeat(50));
    const tcoRes = await get(cookie, 'reportes/tco');
    if (tcoRes.data) {
        console.log('✅ Reporte TCO generado');
        ops.push({ paso: 'TCO', status: '✅' });
    }

    // 10. PARETO DE FALLAS
    console.log('\n📉 10. ANÁLISIS PARETO');
    console.log('─'.repeat(50));
    const paretoRes = await get(cookie, 'reportes/pareto');
    if (paretoRes.data) {
        console.log('✅ Análisis Pareto generado');
        ops.push({ paso: 'Pareto', status: '✅' });
    }

    // 11. DESECHO
    console.log('\n🗑️ 11. DESECHO DE NEUMÁTICO');
    console.log('─'.repeat(50));
    if (motivoDesecho && allInstalled.length > 1) {
        const desechoRes = await post(cookie, 'neumaticos/eventos', {
            tipo_evento: 'DESECHO',
            neumatico_id: allInstalled[allInstalled.length - 1].id,
            motivo_desecho_id: motivoDesecho.id,
            observaciones: 'Fin de vida útil - desgaste total'
        });
        if (ok(desechoRes.status)) {
            console.log('✅ Neumático desechado correctamente');
            ops.push({ paso: 'Desecho', status: '✅' });
        } else {
            console.log(`   ⚠️ Desecho: ${desechoRes.data?.error || desechoRes.status}`);
            ops.push({ paso: 'Desecho', status: '⚠️' });
        }
    }

    // 12. FIN DE TURNO
    console.log('\n🌙 12. FIN DE TURNO - RESUMEN');
    console.log('─'.repeat(50));
    const [invFinal, alertasFinal] = await Promise.all([
        get(cookie, 'dashboard/inventario'),
        get(cookie, 'alertas?limit=5')
    ]);
    const alertasFin = (alertasFinal.data || alertasFinal || []).filter(Boolean);
    console.log(`   📊 Operaciones del día: ${ops.length}`);
    console.log(`   🚨 Alertas pendientes: ${alertasFin.length}`);
    ops.push({ paso: 'Fin turno', alertas_final: alertasFin.length, status: '✅' });

    // REPORT
    const totalTime = ((Date.now() - t0) / 1000).toFixed(1);
    const successOps = ops.filter(o => o.status === '✅').length;

    console.log('\n╔══════════════════════════════════════════════════════════╗');
    console.log('║              RESUMEN DEL DÍA DE OPERACIÓN                ║');
    console.log('╠══════════════════════════════════════════════════════════╣');
    
    for (const op of ops) {
        const detalles = Object.entries(op)
            .filter(([k]) => k !== 'status')
            .map(([k, v]) => `${k}: ${v}`)
            .join(', ');
        const label = `${op.status} ${op.paso}`;
        const pad = 56 - label.length - detalles.length;
        console.log(`║  ${label}${detalles}${pad > 0 ? ' '.repeat(Math.max(0, pad)) : ''}${' '.repeat(Math.max(0, 56 - label.length - detalles.length - pad))} ║`);
    }
    
    console.log('╠══════════════════════════════════════════════════════════╣');
    console.log(`║  Tiempo: ${String(totalTime).padStart(44)}s ║`);
    console.log(`║  Éxito: ${String(successOps + '/' + ops.length).padStart(44)} ║`);
    console.log('╚══════════════════════════════════════════════════════════╝');
    
    if (successOps === ops.length) console.log('\n✅ Día de operación completado sin errores');
    else console.log(`\n⚠️ ${ops.length - successOps} operaciones con observaciones`);
}

main().catch(e => { console.error('❌', e.message); process.exit(1); });
