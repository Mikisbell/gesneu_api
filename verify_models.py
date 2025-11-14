"""
Verificación de modelos SQLModel sin ejecutar código.
"""
import sys
from pathlib import Path
from typing import List, Dict, Any, NoReturn

# Configuración básica
MODEL_FILES: List[str] = [
    "ges_neu_api/modules/auth/models.py",
    "ges_neu_api/modules/vehiculos/models.py",
    "ges_neu_api/modules/neumaticos/models.py",
    "ges_neu_api/modules/inventario/models.py",
    "ges_neu_api/modules/eventos/models.py",
    "ges_neu_api/modules/garantias/models.py",
    "ges_neu_api/modules/alertas/models.py",
    "ges_neu_api/modules/catalogos/models.py",
    "ges_neu_api/modules/bitacoras/models.py",
    "ges_neu_api/modules/sistema/models.py"
]

def check_file(file_path: Path) -> None:
    """Muestra información básica del archivo de modelos.
    
    Args:
        file_path: Ruta al archivo de modelos a verificar.
    
    Returns:
        None
    """
    print(f"\n{'='*80}")
    print(f"ARCHIVO: {file_path}")
    print("="*80)
    
    try:
        content = file_path.read_text(encoding='utf-8')
        # Contar clases que heredan de SQLModel
        models: List[str] = [
            line.split('class ')[1].split('(')[0].strip() 
            for line in content.split('\n') 
            if 'class ' in line and 'SQLModel' in line
        ]
        
        if models:
            print(f"Modelos encontrados ({len(models)}):")
            for model in sorted(models):
                print(f"  - {model}")
        else:
            print("No se encontraron modelos SQLModel en este archivo.")
            
    except Exception as e:
        print(f"Error al procesar el archivo: {e}")

def main() -> None:
    """Función principal que ejecuta la verificación de modelos.
    
    Recorre todos los archivos de modelos definidos en MODEL_FILES y verifica
    las clases SQLModel que contienen.
    
    Returns:
        None
    """
    project_root = Path(__file__).parent.resolve()
    print(f"Directorio del proyecto: {project_root}")
    
    for rel_path in MODEL_FILES:
        file_path = project_root / rel_path
        if file_path.exists():
            check_file(file_path)
        else:
            print(f"\n[ADVERTENCIA] Archivo no encontrado: {file_path}")

def run_script() -> NoReturn:
    """Punto de entrada principal del script.
    
    Returns:
        NoReturn: Finaliza la ejecución del script con código de salida 0
    """
    main()
    raise SystemExit(0)

if __name__ == "__main__":
    run_script()