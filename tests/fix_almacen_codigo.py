#!/usr/bin/env python3
"""
Script para corregir las instancias de creación de Almacen en los tests.
Agrega el campo 'codigo' que es obligatorio.
"""

import re

def fix_almacen_creation(file_path):
    # Leer el archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patrón para encontrar la creación de Almacen
    pattern = r'(almacen\s*=\s*Almacen\s*\(\s*id\s*=\s*uuid\.uuid4\(\)\s*,\s*\n\s*)nombre\s*='
    
    # Reemplazar con el campo codigo añadido
    replacement = r'\1codigo="ALM-TEST-1",\n        nombre='
    
    # Aplicar el reemplazo
    new_content = re.sub(pattern, replacement, content)
    
    # Escribir el archivo si hay cambios
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Archivo {file_path} actualizado correctamente.")
    else:
        print("No se encontraron coincidencias para actualizar.")

if __name__ == "__main__":
    file_path = "/home/belico/gesneu_api/tests/test_alert_service.py"
    fix_almacen_creation(file_path)
