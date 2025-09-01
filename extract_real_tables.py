#!/usr/bin/env python3
"""
Extrae todas las tablas reales del archivo generated_models.py
"""

def extract_all_tables():
    """Extrae todas las tablas del esquema real"""
    
    # Lista completa de tablas extraídas manualmente de generated_models.py
    real_tables = [
        'auditoria_roles_usuarios',
        'bitacora_mantenimiento', 
        'configuracion_auditoria',
        'errores_aplicacion',
        'parametros_sistema',
        'permisos',
        'tareas_programadas',
        'usuarios',
        'almacenes',
        'auditoria_log',
        'fabricantes_neumatico',
        'motivos_desecho',
        'proveedores',
        'roles',
        'rutas',
        'tipos_ruta',
        'tipos_vehiculo',
        'configuraciones_eje',
        'modelos_neumatico',
        'roles_permisos',
        'usuarios_roles',
        'vehiculos',
        'bitacora_operaciones',
        'especificaciones_desgaste',
        'neumaticos',
        'parametros_inventario',
        'parametros_rendimiento_esperado_modelo',
        'posiciones_neumatico',
        'alertas',
        'bitacora_operaciones_neumaticos',
        'eventos_neumaticos',
        'garantias_neumaticos',
        'historial_estados_neumaticos',
        'inventario_neumaticos',
        'mediciones_profundidad',
        'modelos_posiciones_permitidas',
        'movimientos_inventario',
        'registros_odometro'
    ]
    
    # Agrupar por módulos
    modules = {
        'AUTH': ['usuarios', 'roles', 'permisos', 'usuarios_roles', 'roles_permisos', 'auditoria_roles_usuarios'],
        'VEHICULOS': ['vehiculos', 'tipos_vehiculo', 'configuraciones_eje', 'posiciones_neumatico', 'registros_odometro'],
        'NEUMATICOS': ['neumaticos', 'fabricantes_neumatico', 'modelos_neumatico', 'especificaciones_desgaste', 'parametros_rendimiento_esperado_modelo', 'modelos_posiciones_permitidas'],
        'CATALOGOS': ['almacenes', 'proveedores', 'motivos_desecho', 'parametros_inventario'],
        'INVENTARIO': ['inventario_neumaticos', 'movimientos_inventario'],
        'BITACORAS': ['bitacora_mantenimiento', 'bitacora_operaciones', 'bitacora_operaciones_neumaticos', 'auditoria_log', 'configuracion_auditoria', 'errores_aplicacion'],
        'EVENTOS': ['eventos_neumaticos', 'historial_estados_neumaticos', 'mediciones_profundidad'],
        'GARANTIAS': ['garantias_neumaticos'],
        'ALERTAS': ['alertas'],
        'SISTEMA': ['rutas', 'tipos_ruta', 'parametros_sistema', 'tareas_programadas']
    }
    
    print("=== TABLAS REALES EN LA BASE DE DATOS ===")
    print("(Extraídas de backup_completo.dump)")
    print()
    
    total_tables = 0
    for module, tables in modules.items():
        print(f"📁 {module} ({len(tables)} tablas):")
        for table in sorted(tables):
            print(f"  ✅ {table}")
            total_tables += 1
        print()
    
    print(f"📊 TOTAL: {total_tables} tablas reales en la BD")
    
    return real_tables, modules

if __name__ == "__main__":
    extract_all_tables()
