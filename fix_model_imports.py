#!/usr/bin/env python3
"""
Script para corregir específicamente las importaciones en archivos de modelos
para asegurar que ClassVar, Dict y Any estén correctamente importados.
"""

import os
import re
from pathlib import Path

def fix_model_file(file_path):
    """Corrige las importaciones en un archivo de modelo."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Eliminar importaciones duplicadas de uuid
    if content.count('import uuid') > 1:
        content = re.sub(r'import uuid\nimport uuid', 'import uuid', content)
    
    # Asegurar que ClassVar, Dict y Any estén importados
    if 'ClassVar[Dict[str, Any]]' in content:
        if 'from typing import' in content:
            # Verificar si ya están importados
            typing_import = re.search(r'from typing import (.*)', content)
            if typing_import:
                typing_imports = typing_import.group(1)
                needed_imports = []
                
                if 'ClassVar' not in typing_imports:
                    needed_imports.append('ClassVar')
                if 'Dict' not in typing_imports:
                    needed_imports.append('Dict')
                if 'Any' not in typing_imports:
                    needed_imports.append('Any')
                
                if needed_imports:
                    new_typing_import = f"from typing import {typing_imports}, {', '.join(needed_imports)}"
                    content = re.sub(r'from typing import .*', new_typing_import, content)
        else:
            # Añadir la importación si no existe
            content = content.replace(
                'import uuid',
                'import uuid\nfrom typing import ClassVar, Dict, Any',
                1
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

def find_and_fix_model_files(directory):
    """Encuentra y corrige todos los archivos de modelos en el directorio."""
    fixed_files = []
    
    models_dir = os.path.join(directory, 'models')
    if os.path.exists(models_dir):
        for file in os.listdir(models_dir):
            if file.endswith('.py'):
                file_path = os.path.join(models_dir, file)
                
                try:
                    if fix_model_file(file_path):
                        fixed_files.append(file_path)
                except Exception as e:
                    print(f"Error al corregir {file_path}: {e}")
    
    return fixed_files

if __name__ == '__main__':
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"Buscando archivos de modelos para corregir en {project_dir}...")
    fixed_files = find_and_fix_model_files(project_dir)
    
    print(f"Se corrigieron {len(fixed_files)} archivos de modelos:")
    for file in fixed_files:
        print(f"  - {file}")
    
    print("\nCorrecciones completadas. Ejecuta las pruebas para verificar que todo funciona correctamente.")
