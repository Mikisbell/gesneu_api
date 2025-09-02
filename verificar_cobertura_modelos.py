#!/usr/bin/env python3
"""
Verificar cobertura de modelos vs esquema de BD
"""

# Tablas del esquema (37 total)
TABLAS_ESQUEMA = {
    "alembic_version", "alertas", "auditoria_log", "auditoria_roles_usuarios",
    "almacenes", "proveedores", "motivos_desecho", "parametros_inventario",
    "fabricantes_neumatico", "modelos_neumatico", "neumaticos", "modelos_posiciones_permitidas",
    "vehiculos", "tipos_vehiculo", "configuraciones_eje", "posiciones_neumatico", "registros_odometro",
    "eventos_neumaticos", "historial_estados_neumaticos", "mediciones_profundidad",
    "bitacora_operaciones", "bitacora_operaciones_neumaticos", "bitacora_mantenimiento",
    "garantias_neumaticos", "parametros_rendimiento_esperado_modelo", "especificaciones_desgaste",
    "parametros_sistema", "configuracion_auditoria", "errores_aplicacion", "tareas_programadas",
    "usuarios", "roles", "permisos", "usuarios_roles", "roles_permisos",
    "rutas", "tipos_ruta"
}

# Modelos implementados por módulo (estimado)
MODELOS_IMPLEMENTADOS = {
    "auth": {"usuarios", "roles", "permisos", "usuarios_roles", "roles_permisos"},
    "catalogos": {"proveedores", "almacenes", "motivos_desecho", "parametros_inventario"},
    "neumaticos": {"fabricantes_neumatico", "modelos_neumatico", "neumaticos"},
    "vehiculos": {"vehiculos", "tipos_vehiculo", "configuraciones_eje", "posiciones_neumatico", "registros_odometro"},
    "eventos": {"eventos_neumaticos", "historial_estados_neumaticos", "mediciones_profundidad"},
    "garantias": {"garantias_neumaticos"},
    "alertas": {"alertas"},
    "bitacoras": {"bitacora_operaciones", "bitacora_operaciones_neumaticos", "bitacora_mantenimiento", "auditoria_log"},
    "sistema": {"parametros_sistema", "configuracion_auditoria", "errores_aplicacion", "tareas_programadas"},
    "inventario": {}  # Posiblemente vacío o con tablas relacionadas
}

def main():
    print("🔍 VERIFICACIÓN DE COBERTURA DE MODELOS")
    print("=" * 50)
    
    # Aplanar modelos implementados
    implementados = set()
    for modulo, tablas in MODELOS_IMPLEMENTADOS.items():
        implementados.update(tablas)
    
    # Encontrar faltantes
    faltantes = TABLAS_ESQUEMA - implementados
    
    print(f"📊 Tablas en esquema: {len(TABLAS_ESQUEMA)}")
    print(f"✅ Modelos implementados: {len(implementados)}")
    print(f"❌ Tablas faltantes: {len(faltantes)}")
    
    if faltantes:
        print(f"\n🚨 TABLAS FALTANTES ({len(faltantes)}):")
        for tabla in sorted(faltantes):
            print(f"   • {tabla}")
    
    # Verificar por módulo
    print(f"\n📋 COBERTURA POR MÓDULO:")
    for modulo, tablas in MODELOS_IMPLEMENTADOS.items():
        print(f"   🔸 {modulo}: {len(tablas)} modelos")
        for tabla in sorted(tablas):
            print(f"      • {tabla}")
    
    # Tablas especiales que pueden no necesitar modelos
    especiales = {"alembic_version", "auditoria_roles_usuarios"}
    faltantes_criticos = faltantes - especiales
    
    print(f"\n⚠️  TABLAS CRÍTICAS FALTANTES: {len(faltantes_criticos)}")
    for tabla in sorted(faltantes_criticos):
        print(f"   • {tabla}")

if __name__ == "__main__":
    main()
