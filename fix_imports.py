#!/usr/bin/env python3
"""
Script para corregir problemas específicos de importación en archivos Python
que fueron modificados por el script update_config.py.
"""

import os
import re
from pathlib import Path

def fix_file(file_path):
    """Corrige problemas específicos de importación en un archivo."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Corregir importaciones problemáticas
    if 'import \n' in content:
        content = content.replace('import \n', 'import uuid\n')
    
    if 'from pydantic import ConfigDict
import uuid' in content:
        content = content.replace(
            'from pydantic import ConfigDict
import uuid',
            'from pydantic import ConfigDict\nimport uuid'
        )
    
    # Corregir duplicados en las importaciones de typing
    if re.search(r'from typing import .*ClassVar.*Dict.*Any.*ClassVar.*Dict.*Any', content):
        content = re.sub(
            r'from typing import (.*), ClassVar, Dict, Any(.*)',
            r'from typing import \1, ClassVar, Dict, Any\2',
            content
        )
    
    # Corregir configuración duplicada
    if 'from_attributes=True' in content:
        content = content.replace(
            'from_attributes=True',
            'from_attributes=True'
        )
    
    # Corregir espacios extra en la configuración
    content = re.sub(
        r'model_config: ClassVar\[Dict\[str, Any\]\] = ConfigDict\(\s+\s+\s+from_attributes=True\s+\s+\s+\)',
        r'model_config: ClassVar[Dict[str, Any]] = ConfigDict(\n        from_attributes=True\n    )',
        content
    )
    
    # Guardar el archivo corregido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def find_and_fix_files(directory):
    """Encuentra y corrige todos los archivos Python en el directorio."""
    fixed_files = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                # Excluir directorios de entorno virtual y migraciones
                if '/venv/' in file_path or '/.venv/' in file_path or '/migrations/' in file_path:
                    continue
                
                try:
                    if fix_file(file_path):
                        fixed_files.append(file_path)
                except Exception as e:
                    print(f"Error al corregir {file_path}: {e}")
    
    return fixed_files

if __name__ == '__main__':
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"Buscando archivos para corregir en {project_dir}...")
    fixed_files = find_and_fix_files(project_dir)
    
    print(f"Se corrigieron {len(fixed_files)} archivos:")
    for file in fixed_files:
        print(f"  - {file}")
    
    print("\nCorrecciones completadas. Ejecuta las pruebas para verificar que todo funciona correctamente.")
