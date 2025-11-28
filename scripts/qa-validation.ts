import { spawn } from 'child_process';

const BASE_URL = 'http://localhost:3005/api/v1';
const AUTH_URL = 'http://localhost:3005/api/auth';

async function delay(ms: number) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function runQA() {
    console.log('🚀 Starting QA Validation...');

    // Debug: Check if auth endpoint exists
    const checkRes = await fetch(`${AUTH_URL}/signin`);
    console.log('Check /signin status:', checkRes.status);

    if (checkRes.status === 404) {
        console.log('⚠️ /api/auth/signin is 404. Trying /api/auth/providers');
        const provRes = await fetch(`${AUTH_URL}/providers`);
        console.log('Check /providers status:', provRes.status);
    }

    // 1. Get CSRF Token
    console.log('\n1️⃣  Getting CSRF Token...');
    const csrfRes = await fetch(`${AUTH_URL}/csrf`);
    const csrfData = await csrfRes.json();
    const csrfToken = csrfData.csrfToken;
    const csrfCookie = csrfRes.headers.get('set-cookie');
    console.log('CSRF Token:', csrfToken);
    console.log('CSRF Cookie:', csrfCookie);

    // 2. Login
    console.log('\n2️⃣  Testing Authentication...');

    // NextAuth v5 expects form-data or x-www-form-urlencoded for credentials usually, 
    // but let's try JSON first as some configs allow it, or fallback to URLSearchParams.
    // Actually, standard NextAuth credentials provider expects form data.

    const params = new URLSearchParams();
    params.append('username', 'admin_qa'); // or admin
    params.append('password', 'admin123'); // or admin123
    params.append('csrfToken', csrfToken);
    params.append('callbackUrl', '/dashboard');
    params.append('redirect', 'false'); // Tell NextAuth not to redirect

    const loginRes = await fetch(`${AUTH_URL}/callback/credentials`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': csrfRes.headers.get('set-cookie') || '',
            'Accept': 'application/json'
        },
        body: params,
        redirect: 'manual'
    });

    console.log('Login Status:', loginRes.status);

    const cookies = loginRes.headers.get('set-cookie');
    if (cookies) {
        console.log('✅ Login successful (or redirected). Cookies received.');
        console.log('Cookies:', cookies);
    } else if (loginRes.status === 302 || loginRes.status === 303) {
        console.log('Redirected to:', loginRes.headers.get('location'));
        // If redirected without cookies, it might be a failure redirecting to /login
        if (loginRes.headers.get('location')?.includes('error')) {
            console.error('❌ Login failed (Redirected to error)');
            process.exit(1);
        }
        // If redirected to callbackUrl, it might be success, but we need cookies!
        // Sometimes cookies are set on the redirect response.
    } else {
        console.error('❌ Login failed: No cookies received and not redirected');
        const text = await loginRes.text();
        console.log('Response text preview:', text.substring(0, 500));
        process.exit(1);
    }

    // Parse cookies to construct valid Cookie header
    // Set-Cookie header contains attributes like Path, HttpOnly which should not be sent back
    // And multiple cookies are separated by comma in headers.get()

    let cookieHeader = '';
    if (cookies) {
        cookieHeader = cookies.split(',')
            .map(c => c.split(';')[0].trim()) // Take only name=value part
            .join('; ');
    }
    console.log('Constructed Cookie Header:', cookieHeader);

    const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        'Cookie': cookieHeader
    };

    // 2. Testing Neumaticos (List)
    console.log('\n2️⃣  Testing Neumaticos (List)...');
    const neumaticosRes = await fetch(`${BASE_URL}/neumaticos`, { headers });

    if (neumaticosRes.ok) {
        const data = await neumaticosRes.json();
        console.log(`✅ Neumaticos list retrieved. Count: ${data.data?.length || 0}`);
    } else {
        console.error(`❌ Failed to list neumaticos: ${neumaticosRes.status}`);
        console.log(await neumaticosRes.text());
    }

    // 3. Create Proveedor
    console.log('\n3️⃣  Testing Proveedor Creation...');
    const proveedorData = {
        tipo: 'INTERNO',
        nombre: 'Proveedor QA Auto ' + Date.now(),
        ruc: '20' + Date.now(),
        email: 'qa@test.com',
        telefono: '999888777'
    };
    const fabRes = await fetch(`${BASE_URL}/catalogos/proveedores`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
            nombre: `Proveedor QA ${Date.now()}`,
            tipo: 'FABRICANTE', // Assuming schema
            contacto: 'Test Contact',
            telefono: '1234567890',
            email: 'test@provider.com'
        })
    });

    let proveedorId;
    if (fabRes.status === 201 || fabRes.status === 200) {
        const data = await fabRes.json();
        proveedorId = data.data?.id || data.id;
        console.log('✅ Create Proveedor successful:', proveedorId);
    } else {
        console.error('⚠️ Create Proveedor failed (might be schema mismatch):', fabRes.status, await fabRes.text());
    }

    // 4. Test Health/Status
    console.log('\n4️⃣  Testing System Health...');
    // Assuming there might be a health endpoint or just checking root
    try {
        const healthRes = await fetch('http://localhost:3005/api/health');
        if (healthRes.ok) console.log('✅ Health check passed');
        else console.log('⚠️ Health check returned:', healthRes.status);
    } catch (e) {
        console.log('⚠️ No health endpoint found or failed');
    }

    console.log('\n✨ QA Validation Complete!');
}

runQA().catch(console.error);
