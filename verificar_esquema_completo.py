#!/usr/bin/env python3
"""
Script para verificar alineación exacta de TODOS los modelos con ESQUEMA_COMPLETO_BD.md
"""

def verificar_fabricantes_neumatico():
    """Verifica alineación de FabricanteNeumatico con esquema líneas 950-961"""
    print("=== VERIFICANDO FABRICANTES_NEUMATICO ===")
    
    # Según ESQUEMA_COMPLETO_BD.md líneas 950-961:
    esquema_esperado = {
        "id": "uuid, No, gen_random_uuid()",
        "nombre": "character varying(100), No",
        "codigo_abreviado": "character varying(10), Sí", 
        "pais_origen": "character varying(50), Sí",
        "sitio_web": "character varying(255), Sí",
        "activo": "boolean, No, true",
        "creado_en": "timestamp without time zone, No, now()",  # SIN timezone
        "creado_por": "uuid, Sí",
        "actualizado_en": "timestamp without time zone, Sí",   # SIN timezone
        "actualizado_por": "uuid, Sí"
    }
    
    try:
        from ges_neu_api.modules.neumaticos.models import FabricanteNeumatico
        print("✅ Modelo FabricanteNeumatico importado")
        
        # Verificar campos
        campos_modelo = list(FabricanteNeumatico.__fields__.keys())
        campos_esperados = list(esquema_esperado.keys())
        
        print(f"Campos en modelo: {campos_modelo}")
        print(f"Campos esperados: {campos_esperados}")
        
        faltantes = set(campos_esperados) - set(campos_modelo)
        extras = set(campos_modelo) - set(campos_esperados)
        
        if faltantes:
            print(f"❌ Campos faltantes: {faltantes}")
        if extras:
            print(f"⚠️ Campos extras: {extras}")
        
        if not faltantes and not extras:
            print("✅ Todos los campos coinciden con el esquema")
            
    except Exception as e:
        print(f"❌ Error importando FabricanteNeumatico: {e}")

def verificar_vehiculos():
    """Verifica alineación de Vehiculos con esquema líneas 2150-2169"""
    print("\n=== VERIFICANDO VEHICULOS ===")
    
    # Según ESQUEMA_COMPLETO_BD.md líneas 2150-2169:
    esquema_esperado = {
        "id": "uuid, No, gen_random_uuid()",
        "tipo_vehiculo_id": "uuid, No",
        "placa": "character varying(15), Sí",
        "vin": "character varying(17), Sí", 
        "numero_economico": "character varying(50), No",
        "marca": "character varying(50), Sí",
        "modelo_vehiculo": "character varying(50), Sí",
        "anio_fabricacion": "smallint(16), Sí",
        "fecha_alta": "date, No, CURRENT_DATE",
        "fecha_baja": "date, Sí",
        "activo": "boolean, No, true",
        "odometro_actual": "integer(32), Sí",
        "fecha_ultimo_odometro": "timestamp with time zone, Sí",  # CON timezone
        "ubicacion_actual": "character varying(100), Sí",
        "notas": "text, Sí",
        "creado_en": "timestamp with time zone, No, now()",      # CON timezone
        "creado_por": "uuid, Sí",
        "actualizado_en": "timestamp with time zone, Sí",        # CON timezone
        "actualizado_por": "uuid, Sí",
        "peso_carga_maxima_diseno_ton": "numeric(5,2), Sí"
    }
    
    try:
        from ges_neu_api.modules.vehiculos.models import Vehiculos
        print("✅ Modelo Vehiculos importado")
        
        # Verificar campos
        campos_modelo = list(Vehiculos.__fields__.keys())
        campos_esperados = list(esquema_esperado.keys())
        
        print(f"Campos en modelo: {len(campos_modelo)} - {campos_modelo}")
        print(f"Campos esperados: {len(campos_esperados)} - {campos_esperados}")
        
        faltantes = set(campos_esperados) - set(campos_modelo)
        extras = set(campos_modelo) - set(campos_esperados)
        
        if faltantes:
            print(f"❌ Campos faltantes: {faltantes}")
        if extras:
            print(f"⚠️ Campos extras: {extras}")
        
        if not faltantes and not extras:
            print("✅ Todos los campos coinciden con el esquema")
            
    except Exception as e:
        print(f"❌ Error importando Vehiculos: {e}")

def verificar_tipos_vehiculo():
    """Verifica alineación de TiposVehiculo con esquema"""
    print("\n=== VERIFICANDO TIPOS_VEHICULO ===")
    
    try:
        # Buscar esquema de tipos_vehiculo en ESQUEMA_COMPLETO_BD.md
        with open("ESQUEMA_COMPLETO_BD.md", "r", encoding="utf-8") as f:
            contenido = f.read()
            
        if "### tipos_vehiculo" in contenido:
            print("✅ Esquema tipos_vehiculo encontrado en ESQUEMA_COMPLETO_BD.md")
        else:
            print("❌ Esquema tipos_vehiculo NO encontrado en ESQUEMA_COMPLETO_BD.md")
            
        from ges_neu_api.modules.vehiculos.models import TiposVehiculo
        print("✅ Modelo TiposVehiculo importado")
        
        campos = list(TiposVehiculo.__fields__.keys())
        print(f"Campos en modelo: {campos}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("VERIFICACIÓN COMPLETA DE ALINEACIÓN CON ESQUEMA_COMPLETO_BD.md\n")
    
    verificar_fabricantes_neumatico()
    verificar_vehiculos() 
    verificar_tipos_vehiculo()
    
    print(f"\n=== CONCLUSIÓN ===")
    print("Revisar diferencias encontradas y corregir modelos para alineación exacta")
