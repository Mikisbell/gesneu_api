# 🚀 Plan de Migración: FastAPI → Next.js + Supabase

**Fecha:** 14 de Noviembre, 2025  
**Proyecto:** GesNeu API - Sistema de Gestión de Neumáticos  
**Objetivo:** Migrar de FastAPI/Python a Next.js/TypeScript con Supabase PostgreSQL

---

## 📊 Estado Actual

### ✅ **Completado:**
- [x] **Base de datos Supabase** configurada con 37 tablas
- [x] **Esquemas SQL** migrados y funcionando
- [x] **Credenciales** actualizadas (contraseña sin espacios)
- [x] **Proyecto Next.js** inicializado con TypeScript
- [x] **Prisma ORM** configurado
- [x] **Dependencias** instaladas (Next.js, Prisma, Auth)

### 🔄 **En Progreso:**
- [ ] **API Routes** básicos creados
- [ ] **Deploy en Vercel** desde GitHub
- [ ] **Variables de entorno** configuradas

---

## 🎯 Stack Tecnológico

| Componente | Tecnología | Estado |
|------------|------------|---------|
| **Frontend** | Next.js 14 + TypeScript | ✅ |
| **Backend** | Next.js API Routes | 🔄 |
| **Base de Datos** | Supabase PostgreSQL | ✅ |
| **ORM** | Prisma | ✅ |
| **Autenticación** | NextAuth.js + JWT | ⏳ |
| **Deploy** | Vercel | ⏳ |
| **Repositorio** | GitHub | ✅ |

---

## 🛠️ Pasos de Implementación

### **FASE 1: Configuración Base** ✅
1. ✅ Limpiar proyecto FastAPI
2. ✅ Inicializar Next.js con TypeScript
3. ✅ Configurar Prisma
4. ✅ Actualizar credenciales Supabase

### **FASE 2: API Routes Básicos** 🔄
1. ✅ Crear estructura `/src/app/api/`
2. ✅ Endpoint de health check `/api/health`
3. ✅ Página principal con información del proyecto
4. ⏳ Endpoints de catálogos básicos

### **FASE 3: Deploy y Configuración** ⏳
1. ⏳ Commit y push a GitHub
2. ⏳ Conectar Vercel automáticamente
3. ⏳ Configurar variables de entorno en Vercel
4. ⏳ Verificar funcionamiento

### **FASE 4: Endpoints Principales** ⏳
1. ⏳ `/api/v1/catalogos/proveedores`
2. ⏳ `/api/v1/catalogos/almacenes`
3. ⏳ `/api/v1/vehiculos`
4. ⏳ `/api/v1/neumaticos`
5. ⏳ `/api/v1/inventario`

### **FASE 5: Autenticación** ⏳
1. ⏳ Configurar NextAuth.js
2. ⏳ JWT tokens
3. ⏳ Middleware de protección
4. ⏳ Roles y permisos

---

## 🗄️ Estructura de Base de Datos

### **37 Tablas Migradas:**
- **Autenticación:** usuarios, roles, permisos
- **Catálogos:** proveedores, almacenes, fabricantes
- **Vehículos:** vehiculos, modelos, tipos
- **Neumáticos:** neumaticos, modelos, estados
- **Inventario:** movimientos, alertas, parámetros
- **Auditoría:** logs, cambios, eventos

### **Credenciales Supabase:**
```
Host: db.mdefuvnibcwvnwubksun.supabase.co
Port: 5432
Database: postgres
User: postgres
Password: M1k1sB3llR1v3ra
```

---

## 🔗 URLs y Endpoints

### **Desarrollo Local:**
- **Frontend:** http://localhost:3000
- **API Health:** http://localhost:3000/api/health
- **Documentación:** http://localhost:3000/api/docs (futuro)

### **Producción (Vercel):**
- **Frontend:** https://gesneu-api.vercel.app
- **API Health:** https://gesneu-api.vercel.app/api/health
- **API Base:** https://gesneu-api.vercel.app/api/v1/

---

## 📋 Endpoints a Implementar

### **Core Endpoints:**
```
GET  /api/health                           # Health check
GET  /api/v1/catalogos/proveedores         # Lista proveedores
GET  /api/v1/catalogos/almacenes           # Lista almacenes
GET  /api/v1/vehiculos                     # Lista vehículos
GET  /api/v1/neumaticos                    # Lista neumáticos
GET  /api/v1/inventario/movimientos        # Movimientos
POST /api/v1/auth/login                    # Autenticación
```

### **CRUD Completo:**
- **Proveedores:** GET, POST, PUT, DELETE
- **Almacenes:** GET, POST, PUT, DELETE
- **Vehículos:** GET, POST, PUT, DELETE
- **Neumáticos:** GET, POST, PUT, DELETE
- **Inventario:** GET, POST, PUT, DELETE

---

## ⚙️ Variables de Entorno

### **Desarrollo (.env.local):**
```env
DATABASE_URL="postgresql://postgres:M1k1sB3llR1v3ra@db.mdefuvnibcwvnwubksun.supabase.co:5432/postgres"
APP_SECRET_KEY="gesneu_secret_key_2024_super_secure_mikisbell_production"
JWT_SECRET_KEY="jwt_gesneu_2024_very_secure_key_mikisbell_production_token"
NEXTAUTH_SECRET="nextauth_gesneu_2024_super_secret_key"
NEXTAUTH_URL="http://localhost:3000"
NODE_ENV="development"
```

### **Producción (Vercel):**
```env
DATABASE_URL="postgresql://postgres:M1k1sB3llR1v3ra@db.mdefuvnibcwvnwubksun.supabase.co:5432/postgres"
APP_SECRET_KEY="gesneu_secret_key_2024_super_secure_mikisbell_production"
JWT_SECRET_KEY="jwt_gesneu_2024_very_secure_key_mikisbell_production_token"
NEXTAUTH_SECRET="nextauth_gesneu_2024_super_secret_key"
NEXTAUTH_URL="https://gesneu-api.vercel.app"
NODE_ENV="production"
```

---

## 🎯 Próximos Pasos Inmediatos

1. **Ejecutar comandos Git:**
   ```bash
   git add .
   git commit -m "🚀 Convert to Next.js + Prisma + Supabase"
   git push origin main
   ```

2. **Conectar Vercel:**
   - Ir a https://vercel.com/dashboard
   - Import Project desde GitHub
   - Configurar variables de entorno

3. **Verificar funcionamiento:**
   - Probar `/api/health`
   - Verificar conexión con Supabase
   - Crear primeros endpoints

---

## 📈 Ventajas de la Migración

### **Técnicas:**
- ✅ **Vercel nativo** para Next.js (vs problemas con FastAPI)
- ✅ **TypeScript** end-to-end
- ✅ **Prisma ORM** con generación automática
- ✅ **API Routes** integradas
- ✅ **Deploy automático** desde GitHub

### **Operativas:**
- ✅ **Menos complejidad** de infraestructura
- ✅ **Mejor performance** en Vercel
- ✅ **Escalabilidad** automática
- ✅ **Mantenimiento** simplificado

---

## 🔄 Estado del Proyecto

**Progreso General:** 60% completado  
**Tiempo estimado restante:** 2-3 horas  
**Próxima sesión:** Implementar endpoints principales

---

*Documento actualizado: 14/11/2025 00:02 AM*
