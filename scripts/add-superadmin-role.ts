
import 'dotenv/config';
import { Client } from 'pg';

async function main() {
    console.log(`🚀 Adding SUPERADMIN role using DIRECT connection...`);

    // Extract Project Ref and Password from env
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
    const projectRef = supabaseUrl.match(/https:\/\/([^.]+)\.supabase\.co/)?.[1];

    // Parse password from DATABASE_URL (handling potential encoded chars)
    // Format: postgres://[user]:[password]@[host]...
    const dbUrl = process.env.DATABASE_URL || '';
    const match = dbUrl.match(/postgres:\/\/([^:]+):([^@]+)@/);
    const password = match ? match[2] : '';

    if (!projectRef || !password) {
        console.error('❌ Could not derive Direct URL components');
        console.log('Project Ref:', projectRef);
        console.log('Password found:', !!password);
        return;
    }

    // Construct Direct Connection String
    // User is just 'postgres' for direct connection, distinct from pooler 'postgres.projectref'
    const directUrl = `postgres://postgres:${password}@db.${projectRef}.supabase.co:5432/postgres`;

    console.log('Target Host:', `db.${projectRef}.supabase.co`);

    const client = new Client({
        connectionString: directUrl,
        ssl: { rejectUnauthorized: false } // Supabase direct execution requires SSL
    });

    try {
        await client.connect();
        console.log('✅ Connected via Direct URL');

        // Execute Alter Enum
        console.log('➡ Executing ALTER TYPE...');
        await client.query(`ALTER TYPE "RolEnum" ADD VALUE IF NOT EXISTS 'SUPERADMIN'`);
        console.log('✅ ALTER TYPE executed successfully');

    } catch (e: any) {
        console.error('❌ Migration failed:', e.message);
        if (e.code) console.error('Error Code:', e.code);
    } finally {
        await client.end();
    }
}

main();
