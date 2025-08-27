#!/bin/bash

# Colores para la salida
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Configuración del entorno de desarrollo local para GES_NEU_API${NC}"

# Función para verificar comandos
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}❌ Error: $1 no está instalado. Por favor instálalo y vuelve a intentarlo.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ $1 encontrado${NC}"
}

# Verificar dependencias
echo -e "\n${YELLOW}Verificando dependencias...${NC}"
check_command python3
check_command pip3
check_command psql

# Verificar versión de Python
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || [ "$PYTHON_MINOR" -lt 10 ]; then
    echo -e "${RED}❌ Se requiere Python 3.10 o superior. Versión actual: $PYTHON_VERSION${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $PYTHON_VERSION compatible${NC}"

# Configurar entorno virtual
echo -e "\n${YELLOW}Configurando entorno virtual...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Entorno virtual creado${NC}"
else
    echo -e "${GREEN}✓ Entorno virtual ya existe${NC}"
fi

# Activar entorno virtual
echo -e "\n${YELLOW}Activando entorno virtual...${NC}"
source venv/bin/activate

# Actualizar pip
echo -e "\n${YELLOW}Actualizando pip...${NC}"
pip install --upgrade pip

# Instalar dependencias
echo -e "\n${YELLOW}Instalando dependencias de Python...${NC}"
pip install -r requirements.txt

# Instalar dependencias de desarrollo si se especifica
if [ "$1" = "--dev" ] || [ "$1" = "-d" ]; then
    echo -e "\n${YELLOW}Instalando dependencias de desarrollo...${NC}"
    pip install -r requirements-dev.txt
    
    # Configurar pre-commit
    echo -e "\n${YELLOW}Configurando pre-commit...${NC}"
    pre-commit install
fi

# Configurar base de datos local
echo -e "\n${YELLOW}Configurando base de datos local...${NC}"
if ! command -v createdb &> /dev/null; then
    echo -e "${YELLOW}⚠️  El comando 'createdb' no está disponible. Asegúrate de tener PostgreSQL instalado.${NC}"
else
    if psql -lqt | cut -d \| -f 1 | grep -qw ges_neu_db; then
        echo -e "${GREEN}✓ La base de datos 'ges_neu_db' ya existe${NC}"
    else
        echo -e "${YELLOW}Creando base de datos 'ges_neu_db'...${NC}"
        createdb ges_neu_db
        echo -e "${GREEN}✓ Base de datos creada${NC}"
    fi
fi

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    echo -e "\n${YELLOW}Creando archivo .env...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ Archivo .env creado a partir de .env.example${NC}"
    echo -e "${YELLOW}⚠️  Por favor, revisa el archivo .env y configura las variables según tu entorno${NC}"
else
    echo -e "\n${GREEN}✓ El archivo .env ya existe${NC}"
fi

# Aplicar migraciones
echo -e "\n${YELLOW}Aplicando migraciones...${NC}"
alembic upgrade head

# Mensaje final
echo -e "\n${GREEN}✅ Configuración del entorno de desarrollo completada con éxito${NC}"
echo -e "\nPara activar el entorno virtual, ejecuta:"
echo -e "${YELLOW}source venv/bin/activate${NC}"

echo -e "\nPara ejecutar la aplicación en modo desarrollo:"
echo -e "${YELLOW}uvicorn ges_neu_api.main:app --reload${NC}"

echo -e "\nAccede a la documentación en: ${YELLOW}http://localhost:8000/docs${NC}"
