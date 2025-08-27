#!/bin/bash

# Colores para la salida
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para mostrar ayuda
show_help() {
    echo -e "${GREEN}Uso: $0 [comando]${NC}"
    echo ""
    echo "Comandos disponibles:"
    echo "  init          Inicializa Alembic (solo la primera vez)"
    echo "  create [name] Crea una nueva migración con el nombre dado"
    echo "  up [revision] Aplica todas las migraciones o hasta una revisión específica"
    echo "  down [n]      Revierte las últimas 'n' migraciones (por defecto: 1)"
    echo "  status        Muestra el estado actual de las migraciones"
    echo "  help          Muestra esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0 create agregar_campo_nuevo"
    echo "  $0 up"
    echo "  $0 down 2"
}

# Verificar si se proporcionó un comando
if [ $# -eq 0 ]; then
    show_help
    exit 1
fi

# Función para verificar si el entorno virtual está activado
check_virtualenv() {
    if [ -z "$VIRTUAL_ENV" ]; then
        echo -e "${YELLOW}⚠️  No hay un entorno virtual activo. Activando...${NC}"
        if [ -f "venv/bin/activate" ]; then
            source venv/bin/activate
        else
            echo -e "${RED}❌ No se encontró el entorno virtual. Crea uno con 'python -m venv venv'${NC}"
            exit 1
        fi
    fi
}

# Función para verificar si Alembic está instalado
check_alembic() {
    if ! command -v alembic &> /dev/null; then
        echo -e "${YELLOW}⚠️  Alembic no está instalado. Instalando...${NC}"
        pip install alembic
        if [ $? -ne 0 ]; then
            echo -e "${RED}❌ Error al instalar Alembic${NC}"
            exit 1
        fi
    fi
}

# Función para inicializar Alembic
init_alembic() {
    echo -e "${GREEN}🚀 Inicializando Alembic...${NC}"
    
    if [ -d "alembic" ]; then
        echo -e "${YELLOW}⚠️  El directorio 'alembic' ya existe. No se realizará ninguna acción.${NC}"
        return
    fi
    
    alembic init alembic
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Alembic inicializado correctamente${NC}"
        echo -e "\n${YELLOW}⚠️  Recuerda configurar el archivo alembic/env.py según las necesidades de tu proyecto.${NC}"
    else
        echo -e "${RED}❌ Error al inicializar Alembic${NC}"
        exit 1
    fi
}

# Función para crear una nueva migración
create_migration() {
    if [ -z "$1" ]; then
        echo -e "${RED}❌ Debes proporcionar un nombre para la migración${NC}"
        echo "Ejemplo: $0 create nombre_de_la_migracion"
        exit 1
    fi
    
    echo -e "${GREEN}🚀 Creando migración: $1${NC}"
    alembic revision --autogenerate -m "$1"
    
    if [ $? -eq 0 ]; then
        echo -e "\n${GREEN}✓ Migración creada correctamente${NC}"
        echo -e "${YELLOW}⚠️  Revisa el archivo generado antes de aplicar los cambios.${NC}"
    else
        echo -e "${RED}❌ Error al crear la migración${NC}"
        exit 1
    fi
}

# Función para aplicar migraciones
upgrade_migrations() {
    local revision="${1:-head}"
    echo -e "${GREEN}🚀 Aplicando migraciones hasta: $revision${NC}"
    
    alembic upgrade "$revision"
    
    if [ $? -eq 0 ]; then
        echo -e "\n${GREEN}✓ Migraciones aplicadas correctamente${NC}"
    else
        echo -e "${RED}❌ Error al aplicar las migraciones${NC}"
        exit 1
    fi
}

# Función para revertir migraciones
downgrade_migrations() {
    local steps="${1:--1}"
    echo -e "${YELLOW}⚠️  Revirtiendo $steps migración(es)...${NC}"
    
    alembic downgrade "$steps"
    
    if [ $? -eq 0 ]; then
        echo -e "\n${GREEN}✓ Migración(es) revertida(s) correctamente${NC}"
    else
        echo -e "${RED}❌ Error al revertir las migraciones${NC}"
        exit 1
    fi
}

# Función para mostrar el estado de las migraciones
show_status() {
    echo -e "${GREEN}📊 Estado actual de las migraciones:${NC}"
    alembic current
    
    echo -e "\n${GREEN}📜 Historial de migraciones:${NC}"
    alembic history
}

# Procesar el comando
case "$1" in
    init)
        check_virtualenv
        check_alembic
        init_alembic
        ;;
    create)
        check_virtualenv
        check_alembic
        create_migration "$2"
        ;;
    up)
        check_virtualenv
        check_alembic
        upgrade_migrations "$2"
        ;;
    down)
        check_virtualenv
        check_alembic
        downgrade_migrations "${2:--1}"
        ;;
    status)
        check_virtualenv
        check_alembic
        show_status
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}❌ Comando no reconocido: $1${NC}"
        show_help
        exit 1
        ;;
esac

exit 0
