#!/usr/bin/env python3
"""
Script para adaptar modelos SQLAlchemy al esquema existente de PostgreSQL
PRINCIPIO: La API se adapta a la BD, NO al revés
"""

import os
import sys
from pathlib import Path

# Esquema extraído de ESQUEMA_COMPLETO_BD.md
SCHEMA_INFO = {
    "enums": {
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
        "tipoalertaenum": ["PROFUNDIDAD_BAJA", "STOCK_MINIMO", "LIMITE_REENCAUCHES", "PRESION_BAJA", "PRESION_ALTA", "DESGASTE_IRREGULAR", "SOBRECARGA", "FIN_VIDA_UTIL_ESTIMADO", "MANTENIMIENTO_PREVENTIVO", "OTRO"],
        "tipoeventoneumaticoenum": ["INSTALACION", "DESMONTAJE", "ROTACION", "INSPECCION", "REPARACION", "REENCAUCHE_ENTRADA", "REENCAUCHE_SALIDA", "DESECHO", "MOVIMIENTO_ALMACEN", "AJUSTE_INVENTARIO", "CAMBIO_ESTADO"],
        "tipoparametro": ["STOCK_MINIMO", "STOCK_MAXIMO", "PUNTO_REORDEN", "VIDA_UTIL", "PRESION_OPTIMA", "TEMPERATURA_MAXIMA"],
        "tipoproveedorenum": ["FABRICANTE", "DISTRIBUIDOR", "SERVICIO_REPARACION", "SERVICIO_REENCAUCHE", "OTRO"]
    },
    "tables": {
        "alertas": {
            "columns": {
                "id": "uuid PRIMARY KEY DEFAULT gen_random_uuid()",
                "tipo_alerta": "varchar(50) NOT NULL",
                "mensaje": "text NOT NULL",
                "nivel_severidad": "varchar(20) NOT NULL DEFAULT 'INFO'",
                "estado_alerta": "varchar(20) NOT NULL DEFAULT 'NUEVA'",
                "timestamp_generacion": "timestamp with time zone NOT NULL DEFAULT now()",
                "timestamp_gestion": "timestamp with time zone",
                "usuario_gestion_id": "uuid",
                "neumatico_id": "uuid",
                "vehiculo_id": "uuid",
                "modelo_id": "uuid",
                "almacen_id": "uuid",
                "parametro_id": "uuid",
                "datos_contexto": "jsonb"
            }
        }
    }
}

def analyze_current_models():
    """Analiza los modelos actuales en la API"""
    print("🔍 ANALIZANDO MODELOS ACTUALES")
    print("=" * 50)
    
    models_dir = Path("ges_neu_api/modules")
    
    if not models_dir.exists():
        print("❌ Directorio de módulos no encontrado")
        return
    
    modules = []
    for module_dir in models_dir.iterdir():
        if module_dir.is_dir() and (module_dir / "models.py").exists():
            modules.append(module_dir.name)
    
    print(f"📊 Módulos encontrados: {len(modules)}")
    for module in modules:
        print(f"   - {module}")
    
    return modules

def check_enum_alignment():
    """Verifica alineación de ENUMs"""
    print("\n🔍 VERIFICANDO ALINEACIÓN DE ENUMS")
    print("=" * 50)
    
    print(f"📊 ENUMs en esquema BD: {len(SCHEMA_INFO['enums'])}")
    
    critical_enums = [
        "estado_neumatico_enum",
        "nivel_severidad_enum", 
        "tipo_evento_neumatico_enum",
        "estado_operacion_enum"
    ]
    
    print("\n🎯 ENUMs críticos para verificar:")
    for enum_name in critical_enums:
        if enum_name in SCHEMA_INFO['enums']:
            values = SCHEMA_INFO['enums'][enum_name]
            print(f"✅ {enum_name}: {len(values)} valores")
            print(f"   Valores: {', '.join(values[:3])}{'...' if len(values) > 3 else ''}")
        else:
            print(f"❌ {enum_name}: No encontrado")

def check_table_structure():
    """Verifica estructura de tablas críticas"""
    print("\n🔍 VERIFICANDO ESTRUCTURA DE TABLAS")
    print("=" * 50)
    
    # Tablas críticas según el diagnóstico
    critical_tables = [
        "usuarios", "roles", "permisos",
        "vehiculos", "tipos_vehiculo", 
        "neumaticos", "fabricantes_neumatico",
        "proveedores", "almacenes",
        "alertas"
    ]
    
    print("🎯 Tablas críticas que causan errores 500:")
    for table in critical_tables:
        print(f"   - {table}")
    
    print("\n💡 Tabla 'alertas' (ejemplo del esquema):")
    if "alertas" in SCHEMA_INFO['tables']:
        columns = SCHEMA_INFO['tables']['alertas']['columns']
        print(f"   Columnas: {len(columns)}")
        for col, definition in list(columns.items())[:5]:
            print(f"   - {col}: {definition}")

def generate_adaptation_plan():
    """Genera plan de adaptación"""
    print("\n🔧 PLAN DE ADAPTACIÓN")
    print("=" * 50)
    
    print("1. VERIFICAR MODELOS ACTUALES:")
    print("   - Revisar cada modelo en ges_neu_api/modules/*/models.py")
    print("   - Comparar con esquema en ESQUEMA_COMPLETO_BD.md")
    
    print("\n2. ADAPTAR ENUMS:")
    print("   - Crear ENUMs Python que coincidan exactamente")
    print("   - Usar nombres y valores idénticos al esquema BD")
    
    print("\n3. ADAPTAR TABLAS:")
    print("   - Nombres de tabla exactos (ej: 'alertas', no 'Alertas')")
    print("   - Tipos de columna exactos (uuid, varchar, timestamp)")
    print("   - Constraints y defaults exactos")
    
    print("\n4. VERIFICAR RELACIONES:")
    print("   - Foreign keys según esquema BD")
    print("   - Índices definidos en BD")
    
    print("\n5. TESTING:")
    print("   - Probar conexión sin errores 500")
    print("   - Verificar que endpoints respondan correctamente")

def recommend_scripts():
    """Recomienda scripts para usar"""
    print("\n📋 SCRIPTS RECOMENDADOS")
    print("=" * 50)
    
    print("1. ANÁLISIS:")
    print("   python analyze_complete_db.py")
    print("   python verify_models_schema.py")
    
    print("\n2. CORRECCIÓN:")
    print("   python fix_models_with_schema.py")
    print("   python compare_models_with_backup.py")
    
    print("\n3. VERIFICACIÓN:")
    print("   python diagnose_api.py")
    print("   python test_complete_functionality.py")

def main():
    print("🚀 ADAPTACIÓN DE MODELOS AL ESQUEMA EXISTENTE")
    print("=" * 60)
    print("⚠️  PRINCIPIO: La API se adapta a la BD, NO al revés")
    print("📋 Fuente: ESQUEMA_COMPLETO_BD.md (37 tablas)")
    
    # Análisis
    analyze_current_models()
    check_enum_alignment()
    check_table_structure()
    
    # Plan de acción
    generate_adaptation_plan()
    recommend_scripts()
    
    print("\n" + "=" * 60)
    print("🎯 PRÓXIMO PASO: Ejecutar analyze_complete_db.py")
    print("💡 Objetivo: Identificar diferencias específicas entre modelos y BD")

if __name__ == "__main__":
    main()
