#!/usr/bin/env python3
"""
Script para actualizar la clase Config obsoleta de Pydantic a model_config con ConfigDict.
Este script busca todos los archivos Python en el proyecto que utilizan la clase Config
y los actualiza al nuevo formato sin afectar la funcionalidad existente.
"""

import os
import re
import sys
from pathlib import Path

# Patrón para encontrar la clase Config
CONFIG_PATTERN = re.compile(r'(\s+)class Config:(\s+)([^\n]+)(\s+)([^\n]+)?', re.MULTILINE)

# Patrón para verificar si ya se importó ConfigDict
CONFIG_DICT_IMPORT_PATTERN = re.compile(r'from pydantic import .*ConfigDict.*', re.MULTILINE)

# Patrón para verificar si ya se importaron ClassVar, Dict, Any
TYPE_IMPORTS_PATTERN = re.compile(r'from typing import .*ClassVar.*Dict.*Any.*', re.MULTILINE)

def update_file(file_path):
    """Actualiza un archivo para reemplazar la clase Config por model_config."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar si el archivo contiene la clase Config
    if 'class Config:' not in content:
        return False
    
    # Verificar si ya se importó ConfigDict
    config_dict_imported = bool(CONFIG_DICT_IMPORT_PATTERN.search(content))
    
    # Verificar si ya se importaron ClassVar, Dict, Any
    types_imported = bool(TYPE_IMPORTS_PATTERN.search(content))
    
    # Añadir las importaciones necesarias si no existen
    if not config_dict_imported:
        if 'from pydantic import ' in content:
            content = re.sub(
                r'from pydantic import (.*)',
                r'from pydantic import \1, ConfigDict',
                content
            )
        else:
            content = content.replace(
                'import ',
                'import \nfrom pydantic import ConfigDict',
                1
            )
    
    # Añadir las importaciones de typing si no existen
    if not types_imported:
        if 'from typing import ' in content:
            content = re.sub(
                r'from typing import (.*)',
                r'from typing import \1, ClassVar, Dict, Any',
                content
            )
        else:
            content = content.replace(
                'import ',
                'import \nfrom typing import ClassVar, Dict, Any',
                1
            )
    
    # Reemplazar la clase Config por model_config
    def replace_config(match):
        indent = match.group(1)
        newline = match.group(2)
        config_line1 = match.group(3)
        newline2 = match.group(4)
        config_line2 = match.group(5) if match.group(5) else None
        
        # Extraer los valores de configuración
        config_values = []
        if 'from_attributes' in config_line1:
            config_values.append('from_attributes=True')
        elif 'orm_mode' in config_line1:
            config_values.append('from_attributes=True  # Reemplaza orm_mode=True')
        
        if config_line2 and 'from_attributes' in config_line2:
            config_values.append('from_attributes=True')
        elif config_line2 and 'orm_mode' in config_line2:
            config_values.append('from_attributes=True  # Reemplaza orm_mode=True')
        
        # Si no se encontraron valores específicos, usar un valor predeterminado
        if not config_values:
            config_values.append('from_attributes=True')
        
        # Construir la nueva configuración
        new_config = f"{indent}# Configuración moderna usando model_config con ConfigDict{newline}"
        new_config += f"{indent}model_config: ClassVar[Dict[str, Any]] = ConfigDict({newline}"
        new_config += f"{indent}    {', '.join(config_values)}{newline}"
        new_config += f"{indent})"
        
        return new_config
    
    updated_content = CONFIG_PATTERN.sub(replace_config, content)
    
    # Guardar el archivo actualizado
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    return True

def find_and_update_files(directory):
    """Encuentra y actualiza todos los archivos Python en el directorio."""
    updated_files = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                # Excluir directorios de entorno virtual y migraciones
                if '/venv/' in file_path or '/.venv/' in file_path or '/migrations/' in file_path:
                    continue
                
                try:
                    if update_file(file_path):
                        updated_files.append(file_path)
                except Exception as e:
                    print(f"Error al actualizar {file_path}: {e}")
    
    return updated_files

if __name__ == '__main__':
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"Buscando archivos para actualizar en {project_dir}...")
    updated_files = find_and_update_files(project_dir)
    
    print(f"Se actualizaron {len(updated_files)} archivos:")
    for file in updated_files:
        print(f"  - {file}")
    
    print("\nActualización completada. Ejecuta las pruebas para verificar que todo funciona correctamente.")
