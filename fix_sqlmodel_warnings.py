#!/usr/bin/env python3
"""
Script para corregir advertencias relacionadas con SQLModel y datetime en el proyecto.
Este script actualiza los archivos CRUD para usar session.exec() en lugar de session.execute()
y corrige los métodos de manejo de resultados.
"""

import os
import re
from pathlib import Path

def fix_crud_base_file(file_path):
    """Corrige el archivo crud/base.py para usar session.exec() correctamente."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Reemplazar session.execute() con session.exec()
    content = re.sub(
        r'result = await session\.execute\(select\(self\.model\)\.where\(self\.model\.id == id\)\)',
        r'try:\n        return await session.get(self.model, id)\n    except Exception:\n        # Fallback to query if direct get fails\n        result = await session.exec(select(self.model).where(self.model.id == id))',
        content
    )
    
    # Reemplazar scalar_one_or_none() con first()
    content = re.sub(
        r'return result\.scalar_one_or_none\(\)',
        r'return result.first()',
        content
    )
    
    # Reemplazar get_multi
    content = re.sub(
        r'result = await session\.execute\(select\(self\.model\)\.offset\(skip\)\.limit\(limit\)\)',
        r'result = await session.exec(select(self.model).offset(skip).limit(limit))',
        content
    )
    
    # Reemplazar scalars().all() con all()
    content = re.sub(
        r'return result\.scalars\(\)\.all\(\)',
        r'return list(result.all())',
        content
    )
    
    # Reemplazar remove method
    content = re.sub(
        r'async def remove\(self, session: AsyncSession, \*, id: int\) -> Optional\[ModelType\]:\n.*?result = await session\.execute\(select\(self\.model\)\.where\(self\.model\.id == id\)\)\n.*?db_obj = result\.scalar_one_or_none\(\)\n.*?if db_obj:\n.*?await session\.delete\(db_obj\)\n.*?await session\.commit\(\)\n.*?return db_obj',
        r'async def remove(self, session: AsyncSession, *, id: int) -> Optional[ModelType]:\n        """\n        Delete a record by its ID.\n\n        Args:\n            session: The database session.\n            id: The ID of the record to delete.\n\n        Returns:\n            The deleted model instance if found, otherwise None.\n        """\n        try:\n            db_obj = await session.get(self.model, id)\n            if db_obj:\n                await session.delete(db_obj)\n                await session.commit()\n            return db_obj\n        except Exception:\n            # Fallback to query if direct get fails\n            result = await session.exec(select(self.model).where(self.model.id == id))\n            db_obj = result.first()\n            if db_obj:\n                await session.delete(db_obj)\n                await session.commit()\n            return db_obj',
        content,
        flags=re.DOTALL
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def fix_crud_usuario_file(file_path):
    """Corrige el archivo crud/crud_usuario.py para usar session.exec() correctamente."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Reemplazar session.execute() con session.exec() para get_by_email
    content = re.sub(
        r'result = await session\.execute\(statement\)',
        r'result = await session.exec(statement)',
        content
    )
    
    # Reemplazar scalar_one_or_none() con first()
    content = re.sub(
        r'return result\.scalar_one_or_none\(\)',
        r'return result.first()',
        content
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def fix_usuarios_router_file(file_path):
    """Corrige el archivo routers/usuarios.py para usar datetime.UTC correctamente."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Actualizar importación de datetime
    content = re.sub(
        r'from datetime import datetime, timezone',
        r'from datetime import datetime',
        content
    )
    
    # Reemplazar timezone.UTC con datetime.UTC
    content = re.sub(
        r'datetime\.now\(timezone\.UTC\)',
        r'datetime.now(datetime.UTC)',
        content
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def find_and_fix_files(project_dir):
    """Encuentra y corrige los archivos relevantes en el proyecto."""
    fixed_files = []
    
    # Corregir base.py
    base_py_path = os.path.join(project_dir, 'crud', 'base.py')
    if os.path.exists(base_py_path):
        if fix_crud_base_file(base_py_path):
            fixed_files.append(base_py_path)
    
    # Corregir crud_usuario.py
    crud_usuario_py_path = os.path.join(project_dir, 'crud', 'crud_usuario.py')
    if os.path.exists(crud_usuario_py_path):
        if fix_crud_usuario_file(crud_usuario_py_path):
            fixed_files.append(crud_usuario_py_path)
    
    # Corregir usuarios.py
    usuarios_py_path = os.path.join(project_dir, 'routers', 'usuarios.py')
    if os.path.exists(usuarios_py_path):
        if fix_usuarios_router_file(usuarios_py_path):
            fixed_files.append(usuarios_py_path)
    
    return fixed_files

if __name__ == '__main__':
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"Buscando archivos para corregir advertencias en {project_dir}...")
    fixed_files = find_and_fix_files(project_dir)
    
    print(f"Se corrigieron {len(fixed_files)} archivos:")
    for file in fixed_files:
        print(f"  - {file}")
    
    print("\nCorrecciones completadas. Ejecuta las pruebas para verificar que todo funciona correctamente.")
