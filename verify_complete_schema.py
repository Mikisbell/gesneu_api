"""
Script para verificar que todos los modelos estan completos y alineados con el esquema real.
"""
import os

def check_all_models():
    """Verifica que todos los modelos necesarios existen."""
    
    # Modelos que deben existir segun ESQUEMA_BD_REAL.md
    expected_models = {
        'auth': ['Usuario', 'Rol', 'Permiso', 'UsuariosRoles', 'RolesPermisos', 'AuditoriaRolUsuario'],
        'vehiculos': ['TiposVehiculo', 'ConfiguracionesEje', 'PosicionesNeumatico', 'Vehiculos', 'RegistrosOdometro'],
        'catalogos': ['Proveedor', 'MotivoDesecho', 'Almacen', 'ParametroInventario'],
        'neumaticos': ['FabricanteNeumatico', 'ModeloNeumatico', 'Neumatico'],
        'bitacoras': ['BitacoraOperaciones', 'BitacoraMantenimiento', 'ErroresAplicacion', 'AuditoriaLog', 'ConfiguracionAuditoria'],
        'sistema': ['TiposRuta', 'Rutas', 'ParametrosSistema', 'TareasProgramadas'],
        'inventario': ['InventarioNeumaticos', 'MovimientosInventario'],
        'eventos': ['EventosNeumaticos', 'HistorialEstadosNeumaticos', 'MedicionesProfundidad'],
        'garantias': ['GarantiasNeumaticos'],
        'alertas': ['Alertas']
    }
    
    # Tablas que deben existir segun el esquema real
    expected_tables = {
        'usuarios', 'roles', 'permisos', 'usuarios_roles', 'roles_permisos', 'auditoria_roles_usuarios',
        'tipos_vehiculo', 'configuraciones_eje', 'posiciones_neumatico', 'vehiculos', 'registros_odometro',
        'proveedores', 'motivos_desecho', 'almacenes', 'parametros_inventario',
        'fabricantes_neumatico', 'modelos_neumatico', 'neumaticos',
        'bitacora_operaciones', 'bitacora_mantenimiento', 'errores_aplicacion', 'auditoria_log', 'configuracion_auditoria',
        'tipos_ruta', 'rutas', 'parametros_sistema', 'tareas_programadas',
        'inventario_neumaticos', 'movimientos_inventario',
        'eventos_neumaticos', 'historial_estados_neumaticos', 'mediciones_profundidad',
        'garantias_neumaticos',
        'alertas'
    }
    
    print("🔍 Verificando modelos existentes...")
    print("=" * 60)
    
    total_models = 0
    found_models = 0
    
    for module, models in expected_models.items():
        model_file = f'ges_neu_api/modules/{module}/models.py'
        
        if os.path.exists(model_file):
            print(f"✅ {module}/models.py existe")
            
            try:
                with open(model_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                module_found = 0
                for model in models:
                    total_models += 1
                    if f'class {model}(' in content:
                        module_found += 1
                        found_models += 1
                    else:
                        print(f"   ❌ Modelo {model} no encontrado")
                
                print(f"   📊 {module}: {module_found}/{len(models)} modelos encontrados")
                
            except Exception as e:
                print(f"   ❌ Error leyendo {model_file}: {e}")
        else:
            print(f"❌ {model_file} no existe")
    
    print("\n🔍 Verificando nombres de tablas...")
    print("=" * 60)
    
    found_tables = set()
    
    for module in expected_models.keys():
        model_file = f'ges_neu_api/modules/{module}/models.py'
        
        if os.path.exists(model_file):
            try:
                with open(model_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Buscar definiciones de tablename
                lines = content.split('\n')
                for line in lines:
                    if '__tablename__' in line and '=' in line:
                        # Extraer nombre de tabla
                        table_name = line.split('=')[1].strip().strip("'\"")
                        found_tables.add(table_name)
                        
            except Exception as e:
                print(f"❌ Error procesando {model_file}: {e}")
    
    missing_tables = expected_tables - found_tables
    extra_tables = found_tables - expected_tables
    
    print(f"📊 Tablas encontradas: {len(found_tables)}")
    print(f"📊 Tablas esperadas: {len(expected_tables)}")
    
    if missing_tables:
        print(f"\n❌ Tablas faltantes ({len(missing_tables)}):")
        for table in sorted(missing_tables):
            print(f"   - {table}")
    
    if extra_tables:
        print(f"\n⚠️  Tablas extra ({len(extra_tables)}):")
        for table in sorted(extra_tables):
            print(f"   - {table}")
    
    print("\n📊 RESUMEN FINAL:")
    print("=" * 60)
    print(f"Modelos: {found_models}/{total_models} encontrados")
    print(f"Tablas: {len(found_tables)}/{len(expected_tables)} definidas")
    
    if found_models == total_models and len(missing_tables) == 0:
        print("🎉 ÉXITO: Todos los modelos y tablas están completos")
        return True
    else:
        print("⚠️  PENDIENTE: Algunos modelos o tablas faltan")
        return False

if __name__ == "__main__":
    check_all_models()
