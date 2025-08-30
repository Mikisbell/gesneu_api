#!/bin/bash

# Colores para la salida
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Configurando el entorno de desarrollo de GES_NEU_API...${NC}"

# Verificar si se tiene permisos de superusuario
if [ "$EUID" -ne 0 ]; then 
    echo -e "${YELLOW}Se requieren permisos de superusuario para continuar.${NC}"
    exit 1
fi

# Actualizar paquetes del sistema
echo -e "\n${GREEN}🔄 Actualizando paquetes del sistema...${NC}"
apt-get update && apt-get upgrade -y

# Instalar dependencias del sistema
echo -e "\n${GREEN}📦 Instalando dependencias del sistema...${NC}"
apt-get install -y \
    python3.10 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    libpq-dev \
    curl \
    git \
    docker.io \
    docker-compose

# Instalar Poetry
echo -e "\n${GREEN}🐍 Instalando Poetry...${NC}"
curl -sSL https://install.python-poetry.org | python3 - --version 1.5.1

# Configurar variables de entorno para Poetry
echo -e "\n${GREEN}⚙️  Configurando variables de entorno de Poetry...${NC}"
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# Verificar instalación de Docker
echo -e "\n${GREEN}🐳 Verificando instalación de Docker...${NC}"
systemctl enable --now docker
docker --version
docker-compose --version

# Crear entorno virtual de Python
echo -e "\n${GREEN}🔧 Creando entorno virtual de Python...${NC}"
python3 -m venv venv
source venv/bin/activate

# Actualizar pip
echo -e "\n${GREEN}🔄 Actualizando pip...${NC}"
pip install --upgrade pip

# Instalar dependencias de Python
echo -e "\n${GREEN}📦 Instalando dependencias de Python...${NC}"
pip install -r requirements.txt

# Instalar dependencias de desarrollo si se especifica
if [ "$1" = "--dev" ] || [ "$1" = "-d" ]; then
    echo -e "\n${GREEN}🔧 Instalando dependencias de desarrollo...${NC}"
    pip install -r requirements-dev.txt
fi

# Iniciar contenedores de Docker
echo -e "\n${GREEN}🐳 Iniciando contenedores de Docker...${NC}"
docker-compose up -d

# Esperar a que los servicios estén listos
echo -e "\n${GREEN}⏳ Esperando a que los servicios estén listos...${NC}"
sleep 10

# Ejecutar migraciones
echo -e "\n${GREEN}🔄 Ejecutando migraciones de la base de datos...${NC}"
source venv/bin/activate
export $(grep -v '^#' .env | xargs)
alembic upgrade head

# Crear usuario administrador por defecto
echo -e "\n${GREEN}👤 Creando usuario administrador por defecto...${NC}"
python3 -c "
import asyncio
from core.config import settings
from ges_neu_api.auth.service import create_user
from ges_neu_api.modules.auth.schemas import UserCreate

async def create_admin():
    admin = UserCreate(
        email=settings.FIRST_SUPERUSER,
        password=settings.FIRST_SUPERUSER_PASSWORD,
        is_superuser=True,
        is_active=True
    )
    try:
        await create_user(admin)
        print(f'✅ Usuario administrador {settings.FIRST_SUPERUSER} creado exitosamente')
    except Exception as e:
        print(f'⚠️  Error al crear el usuario administrador: {e}')

asyncio.run(create_admin())
"

echo -e "\n${GREEN}✨ ${YELLOW}¡Configuración completada con éxito!${GREEN} ✨${NC}"
echo -e "\nPuedes acceder a los siguientes servicios:"
echo -e "- API: ${YELLOW}http://localhost:8000${NC}"
echo -e "- Documentación: ${YELLOW}http://localhost:8000/docs${NC}"
echo -e "- PgAdmin: ${YELLOW}http://localhost:5050${NC} (admin@example.com/admin)"
echo -e "- Prometheus: ${YELLOW}http://localhost:9090${NC}"
echo -e "- Grafana: ${YELLOW}http://localhost:3000${NC} (admin/admin)"
echo -e "\nPara detener los servicios, ejecuta: ${YELLOW}docker-compose down${NC}"

# Hacer el script ejecutable
chmod +x setup.sh
chmod +x setup_dev_env.sh
