"""
Verificar que los modelos SQLModel coinciden exactamente con las tablas existentes
en la base de datos según backup_completo.dump (ESQUEMA_BD_REAL.md)
"""

def verify_models_alignment():
    """Verificar alineación de modelos con BD existente."""
    
    # Tablas existentes según ESQUEMA_BD_REAL.md
    existing_tables = {
        # Auth module
        'usuarios', 'roles', 'permisos', 'usuarios_roles', 'roles_permisos',
        
        # Vehiculos module  
        'vehiculos', 'tipos_vehiculo', 'configuraciones_eje', 'posiciones_neumatico', 'registros_odometro',
        
        # Catalogos module
        'almacenes', 'proveedores', 'motivos_desecho', 'parametros_inventario',
        
        # Neumaticos module
        'neumaticos', 'modelos_neumatico', 'fabricantes_neumatico',
        
        # Inventario module (NUEVOS MODELOS PARA TABLAS EXISTENTES)
        'inventario_neumaticos', 'movimientos_inventario',
        
        # Eventos module (NUEVOS MODELOS PARA TABLAS EXISTENTES)
        'eventos_neumaticos', 'historial_estados_neumaticos', 'mediciones_profundidad',
        
        # Garantias module (NUEVOS MODELOS PARA TABLAS EXISTENTES)
        'garantias_neumaticos',
        
        # Alertas module (NUEVOS MODELOS PARA TABLAS EXISTENTES)
        'alertas',
        
        # Bitacoras module
        'bitacora_mantenimiento', 'bitacora_operaciones',
        'auditoria_log', 'auditoria_roles_usuarios', 'configuracion_auditoria',
        'errores_aplicacion',
        
        # Sistema module  
        'parametros_sistema', 'tareas_programadas', 'rutas', 'tipos_ruta'
    }
    
    # Modelos SQLModel implementados
    implemented_models = {
        # Auth - EXISTENTES
        'usuarios': 'ges_neu_api.modules.auth.models.Usuario',
        'roles': 'ges_neu_api.modules.auth.models.Rol', 
        'permisos': 'ges_neu_api.modules.auth.models.Permiso',
        'usuarios_roles': 'ges_neu_api.modules.auth.models.UsuariosRoles',
        'roles_permisos': 'ges_neu_api.modules.auth.models.RolesPermisos',
        
        # Vehiculos - EXISTENTES
        'vehiculos': 'ges_neu_api.modules.vehiculos.models.Vehiculos',
        'tipos_vehiculo': 'ges_neu_api.modules.vehiculos.models.TiposVehiculo',
        'configuraciones_eje': 'ges_neu_api.modules.vehiculos.models.ConfiguracionesEje',
        'posiciones_neumatico': 'ges_neu_api.modules.vehiculos.models.PosicionesNeumatico',
        'registros_odometro': 'ges_neu_api.modules.vehiculos.models.RegistrosOdometro',
        
        # Catalogos - EXISTENTES
        'almacenes': 'ges_neu_api.modules.catalogos.models.Almacen',
        'proveedores': 'ges_neu_api.modules.catalogos.models.Proveedor',
        'motivos_desecho': 'ges_neu_api.modules.catalogos.models.MotivoDesecho',
        'parametros_inventario': 'ges_neu_api.modules.catalogos.models.ParametroInventario',
        
        # Neumaticos - EXISTENTES
        'neumaticos': 'ges_neu_api.modules.neumaticos.models.Neumatico',
        'modelos_neumatico': 'ges_neu_api.modules.neumaticos.models.ModeloNeumatico',
        'fabricantes_neumatico': 'ges_neu_api.modules.neumaticos.models.FabricanteNeumatico',
        
        # Inventario - NUEVOS MODELOS PARA TABLAS EXISTENTES
        'inventario_neumaticos': 'ges_neu_api.modules.inventario.models.InventarioNeumaticos',
        'movimientos_inventario': 'ges_neu_api.modules.inventario.models.MovimientosInventario',
        
        # Eventos - NUEVOS MODELOS PARA TABLAS EXISTENTES  
        'eventos_neumaticos': 'ges_neu_api.modules.eventos.models.EventosNeumaticos',
        'historial_estados_neumaticos': 'ges_neu_api.modules.eventos.models.HistorialEstadosNeumaticos',
        'mediciones_profundidad': 'ges_neu_api.modules.eventos.models.MedicionesProfundidad',
        
        # Garantias - NUEVOS MODELOS PARA TABLAS EXISTENTES
        'garantias_neumaticos': 'ges_neu_api.modules.garantias.models.GarantiasNeumaticos',
        
        # Alertas - NUEVOS MODELOS PARA TABLAS EXISTENTES
        'alertas': 'ges_neu_api.modules.alertas.models.Alertas',
        
        # Bitacoras - EXISTENTES
        'bitacora_mantenimiento': 'ges_neu_api.modules.bitacoras.models.BitacoraMantenimiento',
        'bitacora_operaciones': 'ges_neu_api.modules.bitacoras.models.BitacoraOperaciones',
        'auditoria_log': 'ges_neu_api.modules.bitacoras.models.AuditoriaLog',
        'auditoria_roles_usuarios': 'ges_neu_api.modules.bitacoras.models.AuditoriaRolesUsuarios',
        'configuracion_auditoria': 'ges_neu_api.modules.bitacoras.models.ConfiguracionAuditoria',
        'errores_aplicacion': 'ges_neu_api.modules.bitacoras.models.ErroresAplicacion',
        
        # Sistema - EXISTENTES
        'parametros_sistema': 'ges_neu_api.modules.bitacoras.models.ParametrosSistema',
        'tareas_programadas': 'ges_neu_api.modules.bitacoras.models.TareasProgramadas',
        'rutas': 'ges_neu_api.modules.bitacoras.models.Rutas',
        'tipos_ruta': 'ges_neu_api.modules.bitacoras.models.TiposRuta'
    }
    
    print(f"📊 ANÁLISIS DE ALINEACIÓN:")
    print(f"   Tablas en BD existente: {len(existing_tables)}")
    print(f"   Modelos SQLModel implementados: {len(implemented_models)}")
    
    # Verificar cobertura
    covered_tables = set(implemented_models.keys())
    missing_models = existing_tables - covered_tables
    extra_models = covered_tables - existing_tables
    
    print(f"\n✅ Tablas con modelos: {len(covered_tables)}")
    print(f"❌ Tablas sin modelos: {len(missing_models)}")
    print(f"⚠️  Modelos extra: {len(extra_models)}")
    
    if missing_models:
        print(f"\n📋 TABLAS SIN MODELOS (requieren implementación):")
        for table in sorted(missing_models):
            print(f"   - {table}")
    
    if extra_models:
        print(f"\n⚠️  MODELOS SIN TABLA EN BD:")
        for model in sorted(extra_models):
            print(f"   - {model}")
    
    # Estado final
    coverage_percent = (len(covered_tables) / len(existing_tables)) * 100
    print(f"\n📈 COBERTURA: {coverage_percent:.1f}%")
    
    if coverage_percent >= 80:
        print("🎉 EXCELENTE - API casi completamente alineada")
        return True
    elif coverage_percent >= 60:
        print("⚠️  BUENO - Faltan algunos modelos")
        return False
    else:
        print("❌ INSUFICIENTE - Muchos modelos faltantes")
        return False

if __name__ == "__main__":
    verify_models_alignment()
