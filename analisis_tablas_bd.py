#!/usr/bin/env python3
"""
Script para extraer y analizar todas las tablas del ESQUEMA_COMPLETO_BD.md
"""
import re

def extract_tables_from_schema():
    """Extraer todas las tablas del esquema de BD"""
    
    # Leer el archivo del esquema
    with open('ESQUEMA_COMPLETO_BD.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar todas las tablas usando regex
    table_pattern = r'^### ([a-z_][a-z0-9_]*)\s*$'
    tables = []
    
    lines = content.split('\n')
    in_tables_section = False
    
    for line in lines:
        if line.strip() == "## Tablas":
            in_tables_section = True
            continue
            
        if in_tables_section and line.startswith('### '):
            table_name = line.replace('### ', '').strip()
            # Filtrar enums y secciones que no son tablas
            if not any(x in table_name.lower() for x in ['enum', 'columnas', 'restricciones', 'índices']):
                tables.append(table_name)
    
    return sorted(tables)

def get_current_api_modules():
    """Módulos actualmente implementados en la API"""
    return {
        'auth': ['usuarios', 'roles', 'permisos', 'usuarios_roles', 'roles_permisos', 'auditoria_roles_usuarios'],
        'vehiculos': ['vehiculos', 'tipos_vehiculo', 'configuraciones_eje', 'posiciones_neumatico', 'registros_odometro'],
        'catalogos': ['proveedores', 'almacenes', 'motivos_desecho', 'parametros_inventario'],
        'neumaticos': ['neumaticos', 'fabricantes_neumatico', 'modelos_neumatico'],
        'inventario': ['inventario_neumaticos', 'movimientos_inventario'],
        'eventos': ['eventos_neumaticos', 'historial_estados_neumaticos', 'mediciones_profundidad'],
        'garantias': ['garantias_neumaticos'],
        'alertas': ['alertas'],
        'bitacoras': ['bitacora_operaciones', 'bitacora_mantenimiento', 'auditoria_log', 'errores_aplicacion', 'configuracion_auditoria'],
        'sistema': ['tipos_ruta', 'rutas', 'parametros_sistema', 'tareas_programadas']
    }

def analyze_missing_tables():
    """Analizar qué tablas faltan por implementar"""
    
    print("🔍 ANÁLISIS DE TABLAS EN BASE DE DATOS")
    print("=" * 50)
    
    # Extraer tablas del esquema
    bd_tables = extract_tables_from_schema()
    print(f"\n📊 Total de tablas en BD: {len(bd_tables)}")
    
    # Tablas implementadas en API
    api_modules = get_current_api_modules()
    implemented_tables = []
    for module, tables in api_modules.items():
        implemented_tables.extend(tables)
    
    print(f"✅ Tablas implementadas en API: {len(implemented_tables)}")
    
    # Encontrar tablas faltantes
    missing_tables = []
    for table in bd_tables:
        if table not in implemented_tables:
            missing_tables.append(table)
    
    print(f"❌ Tablas faltantes: {len(missing_tables)}")
    
    # Mostrar resultados detallados
    print(f"\n📋 TODAS LAS TABLAS EN BD ({len(bd_tables)}):")
    for i, table in enumerate(bd_tables, 1):
        status = "✅" if table in implemented_tables else "❌"
        print(f"{i:2d}. {status} {table}")
    
    if missing_tables:
        print(f"\n🚨 TABLAS FALTANTES ({len(missing_tables)}):")
        for i, table in enumerate(missing_tables, 1):
            print(f"{i:2d}. ❌ {table}")
            
        print(f"\n💡 SUGERENCIAS DE MÓDULOS:")
        # Agrupar tablas faltantes por posibles módulos
        suggested_modules = {}
        
        for table in missing_tables:
            if 'bitacora' in table or 'operacion' in table:
                suggested_modules.setdefault('bitacoras_extended', []).append(table)
            elif 'especificacion' in table or 'parametro' in table or 'rendimiento' in table:
                suggested_modules.setdefault('especificaciones', []).append(table)
            elif 'modelo' in table and 'posicion' in table:
                suggested_modules.setdefault('configuraciones', []).append(table)
            else:
                suggested_modules.setdefault('otros', []).append(table)
        
        for module, tables in suggested_modules.items():
            print(f"\n📦 {module.upper()}:")
            for table in tables:
                print(f"   - {table}")
    
    else:
        print(f"\n🎉 ¡TODAS LAS TABLAS ESTÁN IMPLEMENTADAS!")
    
    print(f"\n📊 RESUMEN:")
    print(f"   Total tablas BD: {len(bd_tables)}")
    print(f"   Implementadas: {len(implemented_tables)}")
    print(f"   Faltantes: {len(missing_tables)}")
    print(f"   Porcentaje completado: {(len(implemented_tables)/len(bd_tables))*100:.1f}%")

if __name__ == "__main__":
    analyze_missing_tables()
