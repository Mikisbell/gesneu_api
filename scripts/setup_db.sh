#!/bin/bash

# Colores para la salida
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Configuración de la base de datos PostgreSQL local${NC}"

# Verificar si PostgreSQL está instalado
if ! command -v psql &> /dev/null; then
    echo -e "${RED}❌ PostgreSQL no está instalado. Por favor instálalo primero.${NC}"
    echo -e "En Ubuntu/Debian: ${YELLOW}sudo apt-get install postgresql postgresql-contrib${NC}"
    echo -e "En macOS (con Homebrew): ${YELLOW}brew install postgresql${NC}"
    exit 1
fi

# Verificar si el servicio de PostgreSQL está en ejecución
if ! pg_isready &> /dev/null; then
    echo -e "${YELLOW}⚠️  El servicio de PostgreSQL no está en ejecución. Iniciando...${NC}"
    
    # Intentar iniciar el servicio (el comando puede variar según el sistema operativo)
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo service postgresql start
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew services start postgresql
    else
        echo -e "${RED}❌ No se pudo determinar cómo iniciar PostgreSQL en tu sistema.${NC}"
        echo -e "Por favor inicia el servicio de PostgreSQL manualmente y vuelve a intentarlo."
        exit 1
    fi
    
    # Esperar a que el servicio esté listo
    sleep 5
    
    if ! pg_isready &> /dev/null; then
        echo -e "${RED}❌ No se pudo iniciar PostgreSQL. Por favor inicia el servicio manualmente.${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✓ PostgreSQL está instalado y en ejecución${NC}"

# Verificar si el usuario postgres existe
if ! psql -U postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='postgres'" | grep -q 1; then
    echo -e "${YELLOW}⚠️  El usuario 'postgres' no existe. Creando...${NC}"
    
    # Crear el usuario postgres con contraseña 'postgres' (SOLO PARA DESARROLLO)
    sudo -u postgres psql -c "CREATE USER postgres WITH PASSWORD 'postgres' SUPERUSER;"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ No se pudo crear el usuario 'postgres'. Ya puede existir.${NC}"
    else
        echo -e "${GREEN}✓ Usuario 'postgres' creado con contraseña 'postgres'${NC}"
    fi
fi

# Verificar si la base de datos ya existe
if psql -U postgres -lqt | cut -d \| -f 1 | grep -qw ges_neu_db; then
    echo -e "${GREEN}✓ La base de datos 'ges_neu_db' ya existe${NC}"
else
    echo -e "${YELLOW}Creando base de datos 'ges_neu_db'...${NC}"
    createdb -U postgres ges_neu_db
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Base de datos 'ges_neu_db' creada exitosamente${NC}"
    else
        echo -e "${RED}❌ Error al crear la base de datos 'ges_neu_db'${NC}"
        echo -e "Intenta crearla manualmente con: ${YELLOW}createdb -U postgres ges_neu_db${NC}"
        exit 1
    fi
fi

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    echo -e "\n${YELLOW}Creando archivo .env...${NC}"
    
    # Crear un archivo .env con la configuración de desarrollo
    cat > .env <<EOL
# Configuración de la aplicación
DEBUG=True

# Configuración de la base de datos (PostgreSQL local)
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=ges_neu_db
POSTGRES_PORT=5432

# Configuración de autenticación
SECRET_KEY=tu_super_secreto_aqui_cambiar_en_produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 horas

# Usuario administrador por defecto
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=admin

# CORS (orígenes permitidos, separados por coma)
BACKEND_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Configuración de OpenTelemetry (opcional)
OTEL_ENABLED=False
OTEL_SERVICE_NAME=ges-neu-api
OTEL_EXPORTER_OTLP_ENDPOINT=
EOL
    
    echo -e "${GREEN}✓ Archivo .env creado${NC}"
    echo -e "${YELLOW}⚠️  Por favor, revisa el archivo .env y configura las variables según tu entorno${NC}"
else
    echo -e "\n${GREEN}✓ El archivo .env ya existe${NC}"
fi

echo -e "\n${GREEN}✅ Configuración de la base de datos completada con éxito${NC}"
echo -e "\nPuedes continuar con la configuración del entorno de desarrollo."
echo -e "Ejecuta: ${YELLOW}source venv/bin/activate && pip install -r requirements.txt && alembic upgrade head${NC}"
