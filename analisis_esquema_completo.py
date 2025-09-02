#!/usr/bin/env python3
"""
Análisis completo del esquema de base de datos para verificar alineación con modelos
"""

# Tablas identificadas en ESQUEMA_COMPLETO_BD.md (37 tablas total)
TABLAS_ESQUEMA = [
    # Sistema
    "alembic_version",
    
    # Alertas y Auditoría
    "alertas",
    "auditoria_log", 
    "auditoria_roles_usuarios",
    
    # Catálogos principales
    "almacenes",
    "proveedores", 
    "motivos_desecho",
    "parametros_inventario",
    
    # Neumáticos
    "fabricantes_neumatico",
    "modelos_neumatico", 
    "neumaticos",
    "modelos_posiciones_permitidas",
    
    # Vehículos
    "vehiculos",
    "tipos_vehiculo",
    "configuraciones_eje", 
    "posiciones_neumatico",
    "registros_odometro",
    
    # Eventos y Operaciones
    "eventos_neumaticos",
    "historial_estados_neumaticos",
    "mediciones_profundidad",
    "bitacora_operaciones",
    "bitacora_operaciones_neumaticos",
    "bitacora_mantenimiento",
    
    # Garantías
    "garantias_neumaticos",
    
    # Rendimiento y Especificaciones
    "parametros_rendimiento_esperado_modelo",
    "especificaciones_desgaste",
    
    # Sistema y Configuración
    "parametros_sistema",
    "configuracion_auditoria",
    "errores_aplicacion",
    "tareas_programadas",
    
    # Autenticación y Autorización
    "usuarios",
    "roles",
    "permisos", 
    "usuarios_roles",
    "roles_permisos",
    
    # Rutas
    "rutas",
    "tipos_ruta"
]

# Enums identificados en el esquema
ENUMS_ESQUEMA = {
    "estado_alerta_enum": ["NUEVA", "VISTA", "GESTIONADA"],
    "estado_neumatico_enum": ["EN_STOCK", "INSTALADO", "EN_REPARACION", "EN_REENCAUCHE", "DESECHADO", "EN_TRANSITO"],
    "estado_neumatico_enum_destino": ["EN_STOCK", "INSTALADO", "EN_REPARACION", "EN_REENCAUCHE", "DESECHADO", "PARA_REPARACION", "REPARADO", "PARA_REENCAUCHE", "REENCAUCHADO", "EN_TRANSITO"],
    "estado_operacion_enum": ["PENDIENTE", "EN_PROCESO", "COMPLETADA", "CANCELADA", "VENCIDA"],
    "estadoalerta": ["NUEVA", "VISTA", "GESTIONADA"],
    "estadoneumaticoenum": ["EN_STOCK", "INSTALADO", "EN_REPARACION", "EN_REENCAUCHE", "DESECHADO", "BAJA"],
    "lado_vehiculo_enum": ["IZQUIERDO", "DERECHO", "CENTRAL", "INDETERMINADO"],
    "nivel_severidad_enum": ["INFO", "WARN", "CRITICAL"],
    "nivelseveridad": ["INFO", "WARN", "CRITICAL"],
    "tipo_accion_operacion_enum": ["INSTALACION", "DESMONTAJE", "ROTACION", "REPARACION_NEU", "INSPECCION_NEU", "OTRO_NEU"],
    "tipo_eje_enum": ["DIRECCION", "TRACCION", "ARRASTRE", "ELEVADOR", "RETRACTIL", "OTRO"],
    "tipo_evento_neumatico_enum": ["COMPRA", "INSTALACION", "DESMONTAJE", "INSPECCION", "ROTACION", "REPARACION_ENTRADA", "REPARACION_SALIDA", "REENCAUCHE_ENTRADA", "REENCAUCHE_SALIDA", "DESECHO", "AJUSTE_INVENTARIO", "TRANSFERENCIA_UBICACION"],
    "tipo_operacion_enum": ["ROTACION", "BALANCEO", "ALINEACION", "REPARACION_GENERAL", "INSPECCION_GENERAL", "CAMBIO_ACEITE", "OTRO", "DESMONTAJE"],
    "tipo_parametro_inventario_enum": ["PROFUNDIDAD_MINIMA", "STOCK_MINIMO", "STOCK_MAXIMO", "VIDA_UTIL_KM", "VIDA_UTIL_ANIOS"],
    "tipo_parametro_inventario_gesneu_enum": ["STOCK_MINIMO", "STOCK_MAXIMO", "PROFUNDIDAD_MINIMA_RETIRO_MM", "PROFUNDIDAD_MINIMA_REENCAUCHE_MM", "TIEMPO_MAXIMO_VIDA_MESES", "MAX_ROTACIONES_PERIODO", "MAX_REPARACIONES_PERIODO", "VIDA_MAXIMA_ESTANTE_MESES_SIN_USO"],
    "tipoalertaenum": ["PROFUNDIDAD_BAJA", "STOCK_MINIMO", "LIMITE_REENCAUCHES", "PRESION_BAJA", "PRESION_ALTA", "DESGASTE_IRREGULAR", "SOBRECARGA", "FIN_VIDA_UTIL_ESTIMADO", "MANTENIMIENTO_PREVENTIVO"],
    "tipoeventoneumaticoenum": ["INSTALACION", "DESMONTAJE", "INSPECCION", "ROTACION", "REPARACION_ENTRADA", "REPARACION_SALIDA", "REENCAUCHE_ENTRADA", "REENCAUCHE_SALIDA", "DESECHO", "AJUSTE_INVENTARIO", "TRANSFERENCIA_UBICACION"],
    "tipoparametro": ["STOCK_MINIMO", "STOCK_MAXIMO", "PROFUNDIDAD_MINIMA_RETIRO_MM", "PROFUNDIDAD_MINIMA_REENCAUCHE_MM", "TIEMPO_MAXIMO_VIDA_MESES", "MAX_ROTACIONES_PERIODO"],
    "tipoproveedorenum": ["FABRICANTE", "DISTRIBUIDOR", "SERVICIO_REPARACION", "SERVICIO_REENCAUCHE", "OTRO"]
}

def main():
    print("🔍 ANÁLISIS COMPLETO DEL ESQUEMA DE BASE DE DATOS")
    print("=" * 60)
    
    print(f"📊 Total de tablas en esquema: {len(TABLAS_ESQUEMA)}")
    print(f"🏷️  Total de enums en esquema: {len(ENUMS_ESQUEMA)}")
    
    print("\n📋 TABLAS POR MÓDULO:")
    print("=" * 40)
    
    # Agrupar tablas por módulo
    modulos = {
        "Sistema": ["alembic_version"],
        "Alertas": ["alertas"],
        "Auditoría": ["auditoria_log", "auditoria_roles_usuarios"],
        "Catálogos": ["almacenes", "proveedores", "motivos_desecho", "parametros_inventario"],
        "Neumáticos": ["fabricantes_neumatico", "modelos_neumatico", "neumaticos", "modelos_posiciones_permitidas"],
        "Vehículos": ["vehiculos", "tipos_vehiculo", "configuraciones_eje", "posiciones_neumatico", "registros_odometro"],
        "Eventos": ["eventos_neumaticos", "historial_estados_neumaticos", "mediciones_profundidad"],
        "Operaciones": ["bitacora_operaciones", "bitacora_operaciones_neumaticos", "bitacora_mantenimiento"],
        "Garantías": ["garantias_neumaticos"],
        "Rendimiento": ["parametros_rendimiento_esperado_modelo", "especificaciones_desgaste"],
        "Configuración": ["parametros_sistema", "configuracion_auditoria", "errores_aplicacion", "tareas_programadas"],
        "Auth": ["usuarios", "roles", "permisos", "usuarios_roles", "roles_permisos"],
        "Rutas": ["rutas", "tipos_ruta"]
    }
    
    for modulo, tablas in modulos.items():
        print(f"\n🔸 {modulo} ({len(tablas)} tablas):")
        for tabla in tablas:
            print(f"   • {tabla}")
    
    print("\n🏷️  ENUMS CRÍTICOS PARA VERIFICAR:")
    print("=" * 40)
    
    enums_criticos = [
        "tipoproveedorenum",
        "tipo_parametro_inventario_enum", 
        "estado_neumatico_enum",
        "tipo_evento_neumatico_enum",
        "nivel_severidad_enum"
    ]
    
    for enum_name in enums_criticos:
        if enum_name in ENUMS_ESQUEMA:
            valores = ENUMS_ESQUEMA[enum_name]
            print(f"\n🔹 {enum_name}:")
            for valor in valores:
                print(f"   • {valor}")
    
    print("\n✅ ANÁLISIS COMPLETADO")
    print("📝 Próximo paso: Verificar que todos los modelos SQLAlchemy estén implementados")

if __name__ == "__main__":
    main()
