const BASE = 'http://localhost:3005';

async function auth() {
    const csrfRes = await fetch(`${BASE}/api/auth/csrf`);
    const { csrfToken } = await csrfRes.json();
    const cookies = csrfRes.headers.get('set-cookie');
    const params = new URLSearchParams();
    params.append('identifier', 'admin');
    params.append('password', 'admin123');
    params.append('csrfToken', csrfToken);
    params.append('json', 'true');
    const r = await fetch(`${BASE}/api/auth/callback/credentials`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'Cookie': cookies || '' },
        body: params.toString(), redirect: 'manual'
    });
    const m = r.headers.get('set-cookie')?.match(/authjs\.session-token=([^;]+)/);
    return m ? `authjs.session-token=${m[1]}` : null;
}

const H = (c) => ({ 'Content-Type': 'application/json', 'Cookie': c });
const post = async (c, e, b) => {
    const r = await fetch(`${BASE}/api/v1/${e}`, { method: 'POST', headers: H(c), body: JSON.stringify(b) });
    return { status: r.status, data: await r.json().catch(() => ({})) };
};
const get = async (c, e) => {
    const r = await fetch(`${BASE}/api/v1/${e}`, { headers: H(c) });
    const t = await r.text();
    return t ? JSON.parse(t) : { data: null };
};

(async () => {
    const cookie = await auth();
    console.log('Auth OK\n');

    // DEBUG 1: CentroCosto
    console.log('=== CENTRO COSTO ===');
    const cc = await post(cookie, 'centros-costo', { codigo: `DBG-${Date.now()}`, nombre: 'Test CC', area_negocio: 'Test' });
    console.log('Status:', cc.status);
    console.log('Response:', JSON.stringify(cc.data, null, 2).slice(0, 500));

    // DEBUG 2: Tarea
    console.log('\n=== TAREA PROGRAMADA ===');
    // First check what tipo values are accepted
    const tarea = await post(cookie, 'tareas', {
        nombre: `Test ${Date.now()}`,
        tipo: 'GENERAR_REPORTE',
        cron_exp: '0 8 * * 1',
        activo: true,
        parametros: { formato: 'pdf' }
    });
    console.log('Status:', tarea.status);
    console.log('Response:', JSON.stringify(tarea.data, null, 2).slice(0, 500));

    // DEBUG 3: Check mounted tires on first vehicle
    console.log('\n=== VEHICULO MONTAJE ===');
    const vehiculos = (await get(cookie, 'vehiculos?limit=3')).data || [];
    if (vehiculos.length > 0) {
        const v = vehiculos[0];
        console.log('Vehiculo:', v.placa || v.id);
        const montaje = await get(cookie, `vehiculos/${v.id}/montaje`);
        const md = montaje.data || montaje;
        let occupied = 0, free = 0;
        for (const eje of (md.ejes || [])) {
            for (const p of (eje.posiciones || [])) {
                if (p.ocupada) occupied++; else free++;
            }
        }
        console.log(`Ocupadas: ${occupied}, Libres: ${free}`);
    }
})();
