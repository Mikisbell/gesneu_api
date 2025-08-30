#!/bin/bash

# Crear estructura de directorios necesaria
echo "Creando estructura de directorios..."
mkdir -p ges_neu_api/ges_neu_api

# Mover archivos principales
echo "Moviendo archivos principales..."
mv ges_neu_api/main.py ges_neu_api/ges_neu_api/

# Mover directorios principales
echo "Moviendo directorios..."
mv ges_neu_api/core ges_neu_api/ges_neu_api/
mv ges_neu_api/modules ges_neu_api/ges_neu_api/

echo "Estructura reorganizada exitosamente."
echo "Puedes verificar la nueva estructura con: tree ges_neu_api/ges_neu_api"
