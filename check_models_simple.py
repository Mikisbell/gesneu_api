"""
Script simple para verificar la sintaxis de los nuevos modelos
sin importar dependencias de base de datos.
"""

def check_model_syntax():
    """Verifica la sintaxis de los archivos de modelos."""
    import ast
    import os
    
    model_files = [
        'ges_neu_api/modules/inventario/models.py',
        'ges_neu_api/modules/eventos/models.py', 
        'ges_neu_api/modules/garantias/models.py',
        'ges_neu_api/modules/alertas/models.py'
    ]
    
    results = []
    
    for file_path in model_files:
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse the AST to check syntax
                ast.parse(content)
                print(f"✅ {file_path}: Sintaxis correcta")
                results.append(True)
            else:
                print(f"❌ {file_path}: Archivo no encontrado")
                results.append(False)
                
        except SyntaxError as e:
            print(f"❌ {file_path}: Error de sintaxis en línea {e.lineno}: {e.msg}")
            results.append(False)
        except Exception as e:
            print(f"❌ {file_path}: Error: {e}")
            results.append(False)
    
    return results

def check_table_names():
    """Verifica que los nombres de tablas coincidan con el esquema real."""
    expected_tables = {
        'inventario_neumaticos': 'ges_neu_api/modules/inventario/models.py',
        'movimientos_inventario': 'ges_neu_api/modules/inventario/models.py',
        'eventos_neumaticos': 'ges_neu_api/modules/eventos/models.py',
        'historial_estados_neumaticos': 'ges_neu_api/modules/eventos/models.py',
        'mediciones_profundidad': 'ges_neu_api/modules/eventos/models.py',
        'garantias_neumaticos': 'ges_neu_api/modules/garantias/models.py',
        'alertas': 'ges_neu_api/modules/alertas/models.py'
    }
    
    for table_name, file_path in expected_tables.items():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if f"__tablename__ = '{table_name}'" in content:
                print(f"✅ Tabla '{table_name}' definida correctamente")
            else:
                print(f"❌ Tabla '{table_name}' no encontrada en {file_path}")
                
        except Exception as e:
            print(f"❌ Error verificando {table_name}: {e}")

if __name__ == "__main__":
    print("🔍 Verificación de sintaxis de modelos...")
    print("=" * 60)
    
    syntax_results = check_model_syntax()
    
    print("\n🔍 Verificación de nombres de tablas...")
    print("=" * 60)
    
    check_table_names()
    
    print("\n📊 Resumen:")
    print("=" * 60)
    passed = sum(syntax_results)
    total = len(syntax_results)
    
    if passed == total:
        print(f"🎉 ÉXITO: Todos los archivos ({passed}/{total}) tienen sintaxis correcta")
        print("📋 Modelos creados:")
        print("   • Inventario: InventarioNeumaticos, MovimientosInventario")
        print("   • Eventos: EventosNeumaticos, HistorialEstadosNeumaticos, MedicionesProfundidad")
        print("   • Garantías: GarantiasNeumaticos")
        print("   • Alertas: Alertas")
    else:
        print(f"⚠️  {passed}/{total} archivos con sintaxis correcta")
