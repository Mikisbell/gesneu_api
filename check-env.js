require('dotenv').config();
console.log('DATABASE_URL:', process.env.DATABASE_URL ? 'Defined' : 'Undefined');
if (process.env.DATABASE_URL) {
    console.log('Length:', process.env.DATABASE_URL.length);
    console.log('First 10 chars:', process.env.DATABASE_URL.substring(0, 10));
}
