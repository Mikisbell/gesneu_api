#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Configurando el entorno de desarrollo para GES_NEU API...${NC}"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || [ "$PYTHON_MINOR" -lt 10 ]; then
    echo -e "❌ Se requiere Python 3.10 o superior. Versión actual: $PYTHON_VERSION"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION detectado${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creando entorno virtual...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "❌ Error al crear el entorno virtual"
        exit 1
    fi
    echo -e "${GREEN}✓ Entorno virtual creado${NC}"
else
    echo -e "${GREEN}✓ Entorno virtual ya existe${NC}"
fi

# Activate virtual environment
echo -e "\n${YELLOW}Activando el entorno virtual...${NC}"
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo -e "❌ Error al activar el entorno virtual"
    exit 1
fi

# Upgrade pip
echo -e "\n${YELLOW}Actualizando pip...${NC}"
pip install --upgrade pip
if [ $? -ne 0 ]; then
    echo -e "❌ Error al actualizar pip"
    exit 1
fi

# Install dependencies
echo -e "\n${YELLOW}Instalando dependencias...${NC}"
pip install -e ".[dev]"
if [ $? -ne 0 ]; then
    echo -e "❌ Error al instalar dependencias"
    exit 1
fi

# Set up pre-commit hooks
echo -e "\n${YELLOW}Configurando pre-commit hooks...${NC}"
pre-commit install
if [ $? -ne 0 ]; then
    echo -e "❌ Error al configurar pre-commit hooks"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "\n${YELLOW}Creando archivo .env...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ Archivo .env creado a partir de .env.example${NC}"
    echo -e "⚠️  Por favor, configura las variables de entorno en el archivo .env"
else
    echo -e "${GREEN}✓ El archivo .env ya existe${NC}"
fi

# Run database migrations
echo -e "\n${YELLOW}Ejecutando migraciones de la base de datos...${NC}"
alembic upgrade head
if [ $? -ne 0 ]; then
    echo -e "❌ Error al ejecutar migraciones"
    exit 1
fi

# Run tests
echo -e "\n${YELLOW}Ejecutando pruebas...${NC}"
pytest
if [ $? -ne 0 ]; then
    echo -e "⚠️  Algunas pruebas fallaron"
else
    echo -e "${GREEN}✓ ¡Todas las pruebas pasaron!${NC}"
fi

echo -e "\n${GREEN}✅ ¡Entorno de desarrollo configurado correctamente!${NC}"
echo -e "\nPara activar el entorno virtual en el futuro, ejecuta:"
echo -e "  source venv/bin/activate"
echo -e "\nPara iniciar el servidor de desarrollo:"
echo -e "  uvicorn ges_neu_api.main:app --reload"

# Make the script executable
chmod +x setup_dev_env.sh
