
import { execSync } from 'child_process';

const BASE_URL = 'http://localhost:3005';
const USERNAME = 'admin@stress.test';
const PASSWORD = 'StressPassword123!';

async function authenticate() {
    console.log('🔐 Authenticating...');
    const cookieJar = new Map();

    // 1. Get CSRF Token
    const csrfRes = await fetch(`${BASE_URL}/api/auth/csrf`, {
        headers: { 'Content-Type': 'application/json' }
    });

    // Parse cookies from first response
    const setCookie1 = csrfRes.headers.get('set-cookie');
    if (setCookie1) updateCookieJar(cookieJar, setCookie1);

    const csrfData = await csrfRes.json();
    const csrfToken = csrfData.csrfToken;
    console.log('✅ CSRF Token:', csrfToken);

    // 2. Login
    const params = new URLSearchParams();
    params.append('csrfToken', csrfToken);
    params.append('identifier', USERNAME);
    params.append('password', PASSWORD);
    params.append('json', 'true');

    const loginRes = await fetch(`${BASE_URL}/api/auth/callback/credentials`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': serializeCookieJar(cookieJar)
        },
        body: params
    });

    const setCookie2 = loginRes.headers.get('set-cookie');
    if (setCookie2) updateCookieJar(cookieJar, setCookie2);

    if (loginRes.ok) {
        console.log('✅ Login Successful');
    } else {
        console.error('❌ Login Failed:', loginRes.status, await loginRes.text());
        process.exit(1);
    }

    return serializeCookieJar(cookieJar);
}

function updateCookieJar(jar: Map<string, string>, setCookieHeader: string) {
    const cookies = setCookieHeader.split(/,(?=\s*[^;]+=[^;]+)/); // Split multiple cookies roughly
    cookies.forEach(c => {
        const [pair] = c.split(';');
        const [key, value] = pair.split('=');
        if (key && value) jar.set(key.trim(), value.trim());
    });
}

function serializeCookieJar(jar: Map<string, string>) {
    return Array.from(jar.entries()).map(([k, v]) => `${k}=${v}`).join('; ');
}

function runAutocannon(url: string, cookie: string, name: string) {
    console.log(`\n🚀 Starting Stress Test: ${name}`);
    console.log(`   Target: ${url}`);

    const cmd = `npx autocannon -c 10 -d 5 -j -H "Cookie=${cookie}" ${url}`;

    try {
        const output = execSync(cmd, { stdio: 'pipe' }).toString();
        const result = JSON.parse(output);

        console.log(`   📊 Results for ${name}:`);
        console.log(`      RPS (Avg): ${result.requests.average}`);
        console.log(`      Latency (Avg): ${result.latency.average} ms`);
        console.log(`      Latency (99%): ${result.latency.p99} ms`);
        console.log(`      Errors: ${result.errors}`);
        console.log(`      Timeouts: ${result.timeouts}`);

        return result;
    } catch (e) {
        console.error(`❌ Error running autocannon for ${name}`, e);
        return null; // Continue testing
    }
}

async function main() {
    try {
        // 1. Authenticate
        const sessionCookie = await authenticate();

        const results = [];

        // 2. Test Scenarios
        // A. Public Health (Baseline)
        results.push(runAutocannon(`${BASE_URL}/api/v1/health`, sessionCookie, 'Public API Check (Health)'));

        // B. Protected API Read (Neumaticos) - Database Read
        results.push(runAutocannon(`${BASE_URL}/api/v1/neumaticos`, sessionCookie, 'Protected API (DB Read)'));

        // C. Protected SSR Page (Dashboard) - Server Rendering
        results.push(runAutocannon(`${BASE_URL}/dashboard`, sessionCookie, 'SSR Page (Frontend)'));

        // 3. Summary
        console.log('\n🏁 STRESS TEST SUMMARY 🏁');
        console.table(results.map((r, i) => ({
            Test: ['Health', 'DB Read', 'SSR'][i],
            RPS: r?.requests.average.toFixed(2),
            'Latency(ms)': r?.latency.average.toFixed(2),
            Errors: r?.errors
        })));

    } catch (e) {
        console.error('Test Suite Failed', e);
        process.exit(1);
    }
}

main();
