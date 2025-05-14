#!/usr/bin/env python3
"""
Script mejorado para corregir las importaciones en archivos de modelos
para asegurar que ClassVar, Dict y Any estén correctamente importados.
"""

import os
import re
from pathlib import Path

def fix_model_file(file_path):
    """Corrige las importaciones en un archivo de modelo."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar si el archivo contiene model_config
    if 'model_config' in content and 'ConfigDict' in content:
        # Eliminar importaciones duplicadas de uuid
        if content.count('import uuid') > 1:
            content = re.sub(r'import uuid\nimport uuid', 'import uuid', content)
        
        # Verificar si ClassVar, Dict y Any están siendo utilizados
        needs_classvar = 'ClassVar' in content and 'from typing import' in content and 'ClassVar' not in content.split('from typing import')[1].split('\n')[0]
        needs_dict = 'Dict' in content and 'from typing import' in content and 'Dict' not in content.split('from typing import')[1].split('\n')[0]
        needs_any = 'Any' in content and 'from typing import' in content and 'Any' not in content.split('from typing import')[1].split('\n')[0]
        
        # Corregir la línea de importación typing
        if needs_classvar or needs_dict or needs_any:
            typing_import_match = re.search(r'from typing import ([^\n]*)', content)
            if typing_import_match:
                current_imports = typing_import_match.group(1).strip()
                new_imports = current_imports
                
                if needs_classvar and 'ClassVar' not in current_imports:
                    new_imports += ', ClassVar'
                if needs_dict and 'Dict' not in current_imports:
                    new_imports += ', Dict'
                if needs_any and 'Any' not in current_imports:
                    new_imports += ', Any'
                
                content = content.replace(
                    f'from typing import {current_imports}',
                    f'from typing import {new_imports}'
                )
            else:
                # Si no hay importación de typing, agregarla
                additional_imports = []
                if needs_classvar:
                    additional_imports.append('ClassVar')
                if needs_dict:
                    additional_imports.append('Dict')
                if needs_any:
                    additional_imports.append('Any')
                
                if additional_imports:
                    content = re.sub(
                        r'(from pydantic import ConfigDict)',
                        f'\\1\nfrom typing import {", ".join(additional_imports)}',
                        content
                    )
        
        # Si el archivo usa ClassVar[Dict[str, Any]] pero no importa alguno de estos tipos
        if 'ClassVar[Dict[str, Any]]' in content:
            if 'from typing import' not in content:
                content = re.sub(
                    r'(from pydantic import ConfigDict)',
                    '\\1\nfrom typing import ClassVar, Dict, Any',
                    content
                )
            else:
                typing_imports = re.search(r'from typing import ([^\n]*)', content).group(1)
                missing_imports = []
                
                if 'ClassVar' not in typing_imports:
                    missing_imports.append('ClassVar')
                if 'Dict' not in typing_imports:
                    missing_imports.append('Dict')
                if 'Any' not in typing_imports:
                    missing_imports.append('Any')
                
                if missing_imports:
                    content = re.sub(
                        r'from typing import ([^\n]*)',
                        f'from typing import \\1, {", ".join(missing_imports)}',
                        content
                    )
        
        # Corregir espacios extra en la configuración
        content = re.sub(
            r'model_config: ClassVar\[Dict\[str, Any\]\] = ConfigDict\(\s+\s+\s+from_attributes=True\s+\s+\s+\)',
            r'model_config: ClassVar[Dict[str, Any]] = ConfigDict(\n        from_attributes=True\n    )',
            content
        )
        
        # Corregir espacios extra en la configuración (versión alternativa)
        content = re.sub(
            r'model_config: ClassVar\[Dict\[str, Any\]\] = ConfigDict\(\s+from_attributes=True\s+\)',
            r'model_config: ClassVar[Dict[str, Any]] = ConfigDict(\n        from_attributes=True\n    )',
            content
        )
        
        # Corregir cualquier formato extraño en la configuración
        content = re.sub(
            r'model_config:\s+ClassVar\[Dict\[str,\s+Any\]\]\s+=\s+ConfigDict\(\s+from_attributes=True\s+\)',
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
