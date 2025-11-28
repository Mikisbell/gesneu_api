const { Client } = require('pg');

const regions = [
    'us-east-1',
    'us-east-2',
    'us-west-1',
    'us-west-2',
    'ca-central-1',
    'sa-east-1',
    'eu-central-1',
    'eu-west-1',
    'eu-west-2',
    'eu-west-3',
    'ap-northeast-1',
    'ap-northeast-2',
    'ap-southeast-1',
    'ap-southeast-2',
    'ap-south-1'
];

const projectRef = 'hwefuosgihhgzhjqajnx';
const password = 'M1k1sB3ll.$';

async function checkRegion(region) {
    const host = `aws-0-${region}.pooler.supabase.com`;
    const connectionString = `postgres://postgres.${projectRef}:${password}@${host}:6543/postgres`;

    console.log(`Testing ${region}...`);

    const client = new Client({
        connectionString,
        connectionTimeoutMillis: 5000,
        ssl: {
            rejectUnauthorized: false
        }
    });

    try {
        await client.connect();
        console.log(`✅ SUCCESS: Connected to ${region}`);
        await client.end();
        return region;
    } catch (err) {
        if (err.message.includes('Tenant or user not found')) {
            console.log(`❌ ${region}: Tenant not found`);
        } else if (err.message.includes('password authentication failed')) {
            console.log(`✅ FOUND REGION (Auth Error): ${region} (Password might be wrong or special chars issue)`);
            return region;
        } else {
            console.log(`❌ ${region}: ${err.message}`);
        }
        try { await client.end(); } catch (e) { }
        return null;
    }
}

async function findRegion() {
    // Install pg if needed
    try {
        require('pg');
    } catch (e) {
        console.log('Installing pg...');
        require('child_process').execSync('npm install pg', { stdio: 'inherit' });
    }

    for (const region of regions) {
        const found = await checkRegion(region);
        if (found) {
            console.log(`\n🎉 REGION FOUND: ${found}`);
            process.exit(0);
        }
    }
    console.log('\n❌ Could not find region');
    process.exit(1);
}

findRegion();
