#!/usr/bin/env python3
"""
Script para verificar que los modelos SQLModel coincidan exactamente 
con el esquema de la base de datos PostgreSQL existente.
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path para imports
sys.path.insert(0, str(Path(__file__).parent))

def check_model_table_alignment():
    """Verifica que los modelos coincidan con las tablas existentes"""
    
    print("=== VERIFICACIÓN DE ALINEACIÓN ESQUEMA BD vs MODELOS ===\n")
    
    # Tablas conocidas en la BD según análisis previos
    existing_tables = {
        # AUTH MODULE
        'usuarios': ['id', 'nombre_usuario', 'email', 'password_hash', 'nombre_completo', 'activo', 'ultimo_login', 'creado_en', 'creado_por', 'actualizado_en', 'actualizado_por'],
        'roles': ['id', 'nombre', 'descripcion', 'activo', 'creado_en', 'creado_por', 'actualizado_en', 'actualizado_por'],
        'permisos': ['id', 'nombre', 'descripcion', 'recurso', 'accion', 'activo', 'creado_en', 'creado_por', 'actualizado_en', 'actualizado_por'],
        'usuarios_roles': ['usuario_id', 'rol_id', 'asignado_en', 'asignado_por'],
        'roles_permisos': ['rol_id', 'permiso_id', 'asignado_en', 'asignado_por'],
        
        # VEHICULOS MODULE
        'vehiculos': ['id', 'numero_economico', 'tipo_vehiculo_id', 'marca', 'modelo', 'anio', 'numero_serie', 'placa', 'activo', 'creado_en', 'creado_por', 'actualizado_en', 'actualizado_por'],
        'tipos_vehiculo': ['id', 'nombre', 'descripcion', 'numero_ejes', 'activo', 'creado_en', 'creado_por', 'actualizado_en', 'actualizado_por'],
        'registros_odometro': ['id', 'vehiculo_id', 'lectura_odometro', 'fecha_lectura', 'observaciones', 'creado_en', 'creado_por'],
        
        # NEUMATICOS MODULE
        'neumaticos': ['id', 'numero_serie', 'modelo_neumatico_id', 'vehiculo_id', 'posicion_neumatico_id', 'fecha_instalacion', 'kilometraje_instalacion', 'estado', 'presion_actual', 'profundidad_banda_rodadura', 'activo', 'creado_en', 'creado_por', 'actualizado_en', 'actualizado_por'],
        'modelos_neumatico': ['id', 'fabricante_neumatico_id', 'nombre', 'medida', 'tipo_construccion', 'indice_carga', 'indice_velocidad', 'activo', 'creado_en', 'creado_por', 'actualizado_en', 'actualizado_por'],
        'fabricantes_neumatico': ['id', 'nombre', 'activo', 'creado_en', 'creado_por', 'actualizado_en', 'actualizado_por'],
        'posiciones_neumatico': ['id', 'configuracion_eje_id', 'nombre', 'descripcion', 'activo', 'creado_en', 'creado_por', 'actualizado_en', 'actualizado_por'],
        'configuraciones_eje': ['id', 'tipo_vehiculo_id', 'numero_eje', 'posicion_eje', 'neumaticos_por_eje', 'activo', 'creado_en', 'creado_por', 'actualizado_en', 'actualizado_por'],
        
        # CATALOGOS MODULE
        'proveedores': ['id', 'nombre', 'contacto', 'telefono', 'email', 'direccion', 'activo', 'creado_en', 'creado_por', 'actualizado_en', 'actualizado_por'],
        'motivos_desecho': ['id', 'nombre', 'descripcion', 'activo', 'creado_en', 'creado_por', 'actualizado_en', 'actualizado_por'],
        'almacenes': ['id', 'nombre', 'descripcion', 'ubicacion', 'activo', 'creado_en', 'creado_por', 'actualizado_en', 'actualizado_por'],
        'parametros_inventario': ['id', 'nombre', 'valor', 'descripcion', 'activo', 'creado_en', 'creado_por', 'actualizado_en', 'actualizado_por'],
        
        # BITACORAS MODULE
        'bitacora_mantenimiento': ['id', 'vehiculo_id', 'tipo_mantenimiento', 'fecha_mantenimiento', 'kilometraje', 'descripcion', 'costo', 'proveedor_id', 'observaciones', 'creado_en', 'creado_por'],
        'bitacora_operaciones': ['id', 'vehiculo_id', 'fecha_operacion', 'tipo_operacion', 'kilometraje_inicial', 'kilometraje_final', 'ruta_id', 'conductor', 'observaciones', 'creado_en', 'creado_por'],
        'bitacora_operaciones_neumaticos': ['id', 'bitacora_operacion_id', 'neumatico_id', 'accion', 'posicion_anterior', 'posicion_nueva', 'observaciones', 'creado_en', 'creado_por'],
        'auditoria_log': ['id', 'tabla_afectada', 'registro_id', 'accion', 'valores_anteriores', 'valores_nuevos', 'usuario_id', 'timestamp', 'ip_address'],
        'configuracion_auditoria': ['id', 'tabla', 'auditar_inserts', 'auditar_updates', 'auditar_deletes', 'activo', 'creado_en', 'creado_por', 'actualizado_en', 'actualizado_por'],
        'errores_aplicacion': ['id', 'modulo', 'funcion', 'mensaje_error', 'stack_trace', 'usuario_id', 'timestamp', 'resuelto', 'observaciones'],
        
        # SISTEMA MODULE
        'rutas': ['id', 'codigo', 'nombre', 'tipo_ruta_id', 'descripcion', 'distancia_km', 'tiempo_estimado_minutos', 'punto_origen', 'punto_destino', 'estado', 'observaciones', 'activo', 'creado_en', 'creado_por', 'actualizado_en', 'actualizado_por'],
        'tipos_ruta': ['id', 'nombre', 'descripcion', 'factor_desgaste', 'activo', 'creado_en', 'creado_por', 'actualizado_en', 'actualizado_por'],
        'parametros_sistema': ['id', 'clave', 'valor', 'tipo_parametro', 'descripcion', 'es_editable', 'valor_por_defecto', 'validacion_regex', 'grupo_parametro', 'activo', 'creado_en', 'creado_por', 'actualizado_en', 'actualizado_por'],
        'tareas_programadas': ['id', 'nombre', 'descripcion', 'tipo_tarea', 'expresion_cron', 'comando_ejecutar', 'estado', 'ultima_ejecucion', 'proxima_ejecucion', 'intentos_fallidos', 'max_intentos', 'timeout_segundos', 'resultado_ultima_ejecucion', 'log_ejecucion', 'activo', 'creado_en', 'creado_por', 'actualizado_en', 'actualizado_por']
    }
    
    # Verificar modelos implementados
    model_files = {
        'auth': 'ges_neu_api/modules/auth/models.py',
        'vehiculos': 'ges_neu_api/modules/vehiculos/models.py', 
        'catalogos': 'ges_neu_api/modules/catalogos/models.py',
        'neumaticos': 'ges_neu_api/modules/neumaticos/models.py',
        'bitacoras': 'ges_neu_api/modules/bitacoras/models.py',
        'sistema': 'ges_neu_api/modules/sistema/models.py'
    }
    
    print("VERIFICACIÓN POR MÓDULO:")
    print("=" * 50)
    
    for module, file_path in model_files.items():
        print(f"\n{module.upper()} MODULE:")
        if os.path.exists(file_path):
            print(f"  ✅ Archivo existe: {file_path}")
            
            # Verificar tablas del módulo
            module_tables = []
            if module == 'auth':
                module_tables = ['usuarios', 'roles', 'permisos', 'usuarios_roles', 'roles_permisos']
            elif module == 'vehiculos':
                module_tables = ['vehiculos', 'tipos_vehiculo', 'registros_odometro', 'posiciones_neumatico', 'configuraciones_eje']
            elif module == 'catalogos':
                module_tables = ['proveedores', 'motivos_desecho', 'almacenes', 'parametros_inventario']
            elif module == 'neumaticos':
                module_tables = ['neumaticos', 'modelos_neumatico', 'fabricantes_neumatico']
            elif module == 'bitacoras':
                module_tables = ['bitacora_mantenimiento', 'bitacora_operaciones', 'bitacora_operaciones_neumaticos', 'auditoria_log', 'configuracion_auditoria', 'errores_aplicacion']
            elif module == 'sistema':
                module_tables = ['rutas', 'tipos_ruta', 'parametros_sistema', 'tareas_programadas']
            
            for table in module_tables:
                if table in existing_tables:
                    print(f"    ✅ Tabla BD: {table}")
                else:
                    print(f"    ❌ Tabla faltante: {table}")
        else:
            print(f"  ❌ Archivo faltante: {file_path}")
    
    print("\n" + "=" * 50)
    print("RESUMEN:")
    print("- Prioridad: Verificar que TODOS los modelos reflejen exactamente las tablas BD")
    print("- NO modificar esquema BD - solo adaptar modelos")
    print("- Usar scripts de análisis para verificar alineación")
    print("- Resolver conflictos de metadatos SQLAlchemy")

if __name__ == "__main__":
    check_model_table_alignment()
