# 🐳 GesNeu API - Guía de Deployment Docker

## 📦 Imagen Docker Hub

**Imagen pública:** `mikisbell/gesneu-api:latest`
- **URL:** https://hub.docker.com/r/mikisbell/gesneu-api
- **Digest:** `sha256:648a9e7edf3774f450e02ea71837c8b80f9964041e5913e7dc7f9df310c8857d`
- **Tamaño:** 856 MB (optimizada)

## 🚀 Deployment Rápido

### Opción 1: Ejecutar solo la API
```bash
docker run -p 8000:8000 \
  -e DB_HOST=tu_postgres_host \
  -e DB_PASSWORD=tu_password \
  mikisbell/gesneu-api:latest
```

### Opción 2: Stack completo con docker-compose
```yaml
version: '3.8'
services:
  api:
    image: mikisbell/gesneu-api:latest
    ports:
      - "8000:8000"
    environment:
      - DB_HOST=db
      - DB_PASSWORD=B3ll1c0s
      - DB_NAME=ges_neu_bd
      - DB_USER=postgres
    depends_on:
      - db
    
  db:
    image: postgres:17-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=B3ll1c0s
      - POSTGRES_DB=ges_neu_bd
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## 🔧 Variables de Entorno Requeridas

### Base de Datos
```bash
DB_HOST=db                    # Host PostgreSQL
DB_PORT=5432                  # Puerto PostgreSQL
DB_NAME=ges_neu_bd           # Nombre de la BD
DB_USER=postgres             # Usuario PostgreSQL
DB_PASSWORD=tu_password      # Password PostgreSQL
```

### API Configuration
```bash
APP_ENV=production           # Entorno
JWT_SECRET_KEY=tu_jwt_secret # Clave JWT
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

## 📋 Características Incluidas

✅ **API Completa GesNeu**
- 37 tablas PostgreSQL implementadas
- Módulos: auth, catalogos, vehiculos, neumaticos, inventario, eventos, garantias, alertas
- Alineación 100% con esquema PostgreSQL existente

✅ **Optimizaciones**
- Multi-stage Docker build
- Python 3.10-slim
- Dependencias Poetry optimizadas
- Logging estructurado JSON

✅ **Monitoreo**
- Prometheus metrics ready
- Health checks configurados
- Structured logging

## 🌐 Endpoints Disponibles

- **API Root:** http://localhost:8000/
- **Documentación:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health:** http://localhost:8000/api/v1/sistema/status

## 🔒 Seguridad

- Variables sensibles via environment variables
- JWT authentication implementado
- CORS configurado
- Password hashing con bcrypt

## 📊 Monitoreo y Logs

```bash
# Ver logs de la API
docker logs -f container_name

# Logs estructurados JSON
docker logs container_name | jq .
```

## 🚀 Deployment en Producción

### 1. Preparar variables de entorno
```bash
# Crear archivo .env.production
cat > .env.production << EOF
APP_ENV=production
DB_HOST=tu_postgres_host
DB_PASSWORD=tu_secure_password
JWT_SECRET_KEY=tu_jwt_super_secret
BACKEND_CORS_ORIGINS=["https://tu-dominio.com"]
EOF
```

### 2. Ejecutar con variables de producción
```bash
docker run -p 8000:8000 --env-file .env.production mikisbell/gesneu-api:latest
```

### 3. Con reverse proxy (nginx)
```nginx
server {
    listen 80;
    server_name api.tu-dominio.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔄 Actualizaciones

```bash
# Descargar nueva versión
docker pull mikisbell/gesneu-api:latest

# Reiniciar con nueva imagen
docker-compose up -d --force-recreate api
```

## 📞 Soporte

- **Repositorio:** https://github.com/mikisbell/gesneu_api
- **Docker Hub:** https://hub.docker.com/r/mikisbell/gesneu-api
- **Documentación API:** http://localhost:8000/docs

---
*Generado automáticamente - GesNeu API v1.0.0*
