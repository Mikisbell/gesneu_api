import { defineConfig } from 'prisma/config'
import 'dotenv/config'

console.log('Prisma Config - DATABASE_URL:', process.env.DATABASE_URL);
console.log('Prisma Config - DIRECT_URL:', process.env.DIRECT_URL);

export default defineConfig({
    datasource: {
        url: process.env.DATABASE_URL!,
        directUrl: process.env.DIRECT_URL
    } as any
})
