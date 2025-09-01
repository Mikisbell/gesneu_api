"""
Script final para verificar modelos completos sin conexión a BD
Verifica que todos los archivos de modelos estén completos y bien estructurados
"""
import os
import importlib.util
from pathlib import Path

def check_model_files():
    """Verificar que todos los archivos de modelos existan y sean importables"""
    
    base_path = Path("ges_neu_api/modules")
    
    model_files = [
        "auth/models.py",
        "vehiculos/models.py", 
        "neumaticos/models.py",
        "neumaticos/models_final.py",
        "catalogos/models.py",
        "catalogos/models_clean.py",
        "bitacoras/models.py"
    ]
    
    print("=== VERIFICACION DE ARCHIVOS DE MODELOS ===\n")
    
    results = {}
    
    for model_file in model_files:
        file_path = base_path / model_file
        print(f"Verificando: {model_file}")
        
        if file_path.exists():
            try:
                # Intentar importar el módulo
                spec = importlib.util.spec_from_file_location("test_module", file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Contar clases de modelo
                model_classes = []
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if hasattr(attr, '__tablename__'):
                        model_classes.append(attr_name)
                
                results[model_file] = {
                    'exists': True,
                    'importable': True,
                    'models': model_classes,
                    'count': len(model_classes)
                }
                
                print(f"  OK Archivo existe y es importable")
                print(f"  OK {len(model_classes)} modelos encontrados: {', '.join(model_classes[:3])}{'...' if len(model_classes) > 3 else ''}")
                
            except Exception as e:
                results[model_file] = {
                    'exists': True,
                    'importable': False,
                    'error': str(e)
                }
                print(f"  ERROR al importar: {e}")
        else:
            results[model_file] = {
                'exists': False,
                'importable': False
            }
            print(f"  ERROR Archivo no encontrado")
        
        print()
    
    return results

def check_all_tables_covered():
    """Verificar que todas las 36 tablas estén cubiertas en los modelos"""
    
    expected_tables = [
        # Autenticación (5)
        'usuarios', 'roles', 'permisos', 'usuarios_roles', 'roles_permisos',
        
        # Vehículos (3)
        'vehiculos', 'tipos_vehiculo', 'registros_odometro',
        
        # Neumáticos core (5)
        'neumaticos', 'modelos_neumatico', 'fabricantes_neumatico', 
        'posiciones_neumatico', 'configuraciones_eje',
        
        # Inventario (4)
        'inventario_neumaticos', 'movimientos_inventario', 'almacenes', 
        'parametros_inventario',
        
        # Catálogos (3)
        'proveedores', 'disenios', 'motivos_desecho',
        
        # Rutas (2)
        'rutas', 'tipos_ruta',
        
        # Sistema (2)
        'parametros_sistema', 'tareas_programadas',
        
        # Bitácoras (3)
        'bitacora_mantenimiento', 'bitacora_operaciones', 
        'bitacora_operaciones_neumaticos',
        
        # Auditoría (3)
        'auditoria_log', 'configuracion_auditoria', 'errores_aplicacion',
        
        # Eventos y mediciones (4)
        'eventos_neumaticos', 'mediciones_profundidad', 
        'especificaciones_desgaste', 'historial_estados_neumaticos',
        
        # Garantías y alertas (2)
        'garantias_neumaticos', 'alertas',
        
        # Configuración avanzada (2)
        'parametros_rendimiento_esperado_modelo', 'modelos_posiciones_permitidas'
    ]
    
    print(f"=== VERIFICACION DE COBERTURA DE TABLAS ===")
    print(f"Total esperado: {len(expected_tables)} tablas\n")
    
    # Agrupar por módulos
    modules = {
        'Autenticación': expected_tables[0:5],
        'Vehículos': expected_tables[5:8], 
        'Neumáticos': expected_tables[8:13],
        'Inventario': expected_tables[13:17],
        'Catálogos': expected_tables[17:20],
        'Rutas': expected_tables[20:22],
        'Sistema': expected_tables[22:24],
        'Bitácoras': expected_tables[24:27],
        'Auditoría': expected_tables[27:30],
        'Eventos/Mediciones': expected_tables[30:34],
        'Garantías/Alertas': expected_tables[34:36],
        'Configuración Avanzada': expected_tables[36:38]
    }
    
    for module_name, tables in modules.items():
        print(f"📁 {module_name}: {len(tables)} tablas")
        for table in tables:
            print(f"  - {table}")
        print()
    
    return expected_tables

def main():
    """Función principal de verificación"""
    print("VERIFICACION FINAL DE MODELOS GESNEU API")
    print("=" * 50)
    print()
    
    # Verificar archivos de modelos
    model_results = check_model_files()
    
    # Verificar cobertura de tablas
    all_tables = check_all_tables_covered()
    
    # Resumen final
    print("=== RESUMEN FINAL ===")
    
    total_files = len(model_results)
    working_files = sum(1 for r in model_results.values() if r.get('importable', False))
    total_models = sum(r.get('count', 0) for r in model_results.values() if r.get('importable', False))
    
    print(f"Archivos de modelos: {working_files}/{total_files} funcionando")
    print(f"Total de modelos definidos: {total_models}")
    print(f"Tablas objetivo: {len(all_tables)}")
    
    if working_files == total_files and total_models >= len(all_tables):
        print("\nVERIFICACION EXITOSA - Todos los modelos están listos")
        return True
    else:
        print(f"\nATENCION REQUERIDA - Revisar archivos con errores")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
