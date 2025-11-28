#!/bin/bash

# Script para configurar variables de entorno en Vercel
# Ejecuta este script si necesitas reconfigurar en el futuro

echo "🔧 Configurando variables de entorno en Vercel..."

# DATABASE_URL (Supabase Cloud)
echo "📊 Agregando DATABASE_URL..."
echo "postgresql://postgres.mdefuvnibcwvnwubksun:M1k1sB3llR1v3ra@aws-0-us-east-1.pooler.supabase.com:6543/postgres?pgbouncer=true&connection_limit=1" | vercel env add DATABASE_URL production

# NEXTAUTH_SECRET
echo "🔐 Agregando NEXTAUTH_SECRET..."
echo "nextauth_gesneu_2024_super_secret_key" | vercel env add NEXTAUTH_SECRET production

# NEXTAUTH_URL
echo "🌐 Agregando NEXTAUTH_URL..."
echo "https://gesneu.vercel.app" | vercel env add NEXTAUTH_URL production

# APP_SECRET_KEY
echo "🔑 Agregando APP_SECRET_KEY..."
echo "gesneu_secret_key_2024_super_secure_mikisbell_production" | vercel env add APP_SECRET_KEY production

# JWT_SECRET_KEY
echo "🎫 Agregando JWT_SECRET_KEY..."
echo "jwt_gesneu_2024_very_secure_key_mikisbell_production_token" | vercel env add JWT_SECRET_KEY production

# NODE_ENV
echo "⚙️  Agregando NODE_ENV..."
echo "production" | vercel env add NODE_ENV production

echo ""
echo "✅ Variables configuradas exitosamente!"
echo ""
echo "🚀 Iniciando redeploy..."
vercel --prod --yes

echo ""
echo "✅ ¡Listo! Verificando conexión..."
sleep 30
curl -s https://gesneu.vercel.app/api/health | jq .
