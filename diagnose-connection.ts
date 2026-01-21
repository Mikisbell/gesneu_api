
import 'dotenv/config';
import { Pool } from 'pg';

const connectionString = process.env.DATABASE_URL;

async function diagnose() {
    console.log('🔌 Testing raw PG connection...');
    console.log('URL:', connectionString?.replace(/:[^:]*@/, ':****@')); // Hide password

    const pool = new Pool({
        connectionString,
        ssl: connectionString?.includes('localhost') ? false : { rejectUnauthorized: false },
    });

    try {
        const client = await pool.connect();
        console.log('✅ Connected to Pool');

        try {
            const res = await client.query('SELECT 1 as val');
            console.log('✅ SELECT 1 result:', res.rows[0]);

            // Try setting session var
            await client.query("SET app.current_user_id = '00000000-0000-0000-0000-000000000000'");
            console.log('✅ SET app.current_user_id Success');

        } catch (queryErr) {
            console.error('❌ Query Failed:', queryErr);
        } finally {
            client.release();
        }
    } catch (err) {
        console.error('❌ Connection Failed:', err);
    } finally {
        await pool.end();
    }
}

diagnose();
