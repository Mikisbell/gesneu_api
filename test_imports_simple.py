"""
Test simple de sintaxis de modelos sin crear tablas SQLAlchemy
"""
import ast
import os

def test_python_syntax(file_path):
    """Test syntax of Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return True, None
    except Exception as e:
        return False, str(e)

def main():
    """Test syntax of all model files."""
    model_files = [
        'ges_neu_api/modules/auth/models.py',
        'ges_neu_api/modules/vehiculos/models.py', 
        'ges_neu_api/modules/catalogos/models.py',
        'ges_neu_api/modules/neumaticos/models.py',
        'ges_neu_api/modules/inventario/models.py',
        'ges_neu_api/modules/eventos/models.py',
        'ges_neu_api/modules/garantias/models.py',
        'ges_neu_api/modules/alertas/models.py'
    ]
    
    results = []
    for file_path in model_files:
        if os.path.exists(file_path):
            success, error = test_python_syntax(file_path)
            module_name = file_path.split('/')[2]
            if success:
                print(f"✅ {module_name}: Sintaxis correcta")
                results.append(True)
            else:
                print(f"❌ {module_name}: Error - {error}")
                results.append(False)
        else:
            print(f"⚠️  {file_path}: Archivo no encontrado")
            results.append(False)
    
    passed = sum(results)
    total = len(results)
    print(f"\n📊 Resultado: {passed}/{total} archivos con sintaxis correcta")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
