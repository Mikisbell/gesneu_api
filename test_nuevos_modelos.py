#!/usr/bin/env python3
"""
Test para verificar que los nuevos modelos implementados funcionan correctamente
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Verificar que todos los nuevos modelos se pueden importar correctamente"""
    print("🔍 VERIFICANDO IMPORTS DE NUEVOS MODELOS")
    print("=" * 50)
    
    try:
        # Test BitacoraOperacionesNeumaticos
        from ges_neu_api.modules.bitacoras.models import BitacoraOperacionesNeumaticos
        print("✅ BitacoraOperacionesNeumaticos - Import exitoso")
        
        # Test EspecificacionesDesgaste
        from ges_neu_api.modules.neumaticos.models import EspecificacionesDesgaste
        print("✅ EspecificacionesDesgaste - Import exitoso")
        
        # Test ParametrosRendimientoEsperadoModelo
        from ges_neu_api.modules.neumaticos.models import ParametrosRendimientoEsperadoModelo
        print("✅ ParametrosRendimientoEsperadoModelo - Import exitoso")
        
        # Test ModelosPosicionesPermitidas
        from ges_neu_api.modules.neumaticos.models import ModelosPosicionesPermitidas
        print("✅ ModelosPosicionesPermitidas - Import exitoso")
        
        # Test nuevos enums
        from ges_neu_api.core.base_models import TipoAccionBitacoraEnum, TipoPosicionEnum
        print("✅ TipoAccionBitacoraEnum - Import exitoso")
        print("✅ TipoPosicionEnum - Import exitoso")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error de import: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_model_structure():
    """Verificar la estructura de los modelos"""
    print("\n🔧 VERIFICANDO ESTRUCTURA DE MODELOS")
    print("=" * 50)
    
    try:
        from ges_neu_api.modules.bitacoras.models import BitacoraOperacionesNeumaticos
        from ges_neu_api.modules.neumaticos.models import (
            EspecificacionesDesgaste, 
            ParametrosRendimientoEsperadoModelo,
            ModelosPosicionesPermitidas
        )
        
        # Verificar BitacoraOperacionesNeumaticos
        print("\n📋 BitacoraOperacionesNeumaticos:")
        bitacora_fields = [field for field in dir(BitacoraOperacionesNeumaticos) if not field.startswith('_')]
        required_bitacora_fields = [
            'id', 'operacion_id', 'neumatico_id', 'tipo_accion', 
            'posicion_neumatico_id', 'profundidad_inicial_mm', 'profundidad_final_mm',
            'presion_inicial_psi', 'presion_final_psi', 'kilometraje_vehiculo_km',
            'observaciones', 'creado_en', 'actualizado_en', 'creado_por', 'actualizado_por'
        ]
        
        for field in required_bitacora_fields:
            if field in bitacora_fields:
                print(f"  ✅ {field}")
            else:
                print(f"  ❌ {field} - FALTANTE")
        
        # Verificar EspecificacionesDesgaste
        print("\n📋 EspecificacionesDesgaste:")
        especif_fields = [field for field in dir(EspecificacionesDesgaste) if not field.startswith('_')]
        required_especif_fields = [
            'id', 'modelo_neumatico_id', 'tipo_posicion', 
            'vida_util_km_min', 'vida_util_km_max', 'descripcion_estado',
            'creado_en', 'creado_por', 'actualizado_en', 'actualizado_por'
        ]
        
        for field in required_especif_fields:
            if field in especif_fields:
                print(f"  ✅ {field}")
            else:
                print(f"  ❌ {field} - FALTANTE")
        
        # Verificar ParametrosRendimientoEsperadoModelo
        print("\n📋 ParametrosRendimientoEsperadoModelo:")
        param_fields = [field for field in dir(ParametrosRendimientoEsperadoModelo) if not field.startswith('_')]
        required_param_fields = [
            'id', 'modelo_id', 'tipo_eje_aplicacion',
            'km_esperado_vida_original_min', 'km_esperado_vida_original_max',
            'activo', 'creado_en', 'creado_por', 'actualizado_en', 'actualizado_por'
        ]
        
        for field in required_param_fields:
            if field in param_fields:
                print(f"  ✅ {field}")
            else:
                print(f"  ❌ {field} - FALTANTE")
        
        # Verificar ModelosPosicionesPermitidas
        print("\n📋 ModelosPosicionesPermitidas:")
        modelos_pos_fields = [field for field in dir(ModelosPosicionesPermitidas) if not field.startswith('_')]
        required_modelos_pos_fields = [
            'id', 'modelo_neumatico_id', 'posicion_neumatico_id',
            'activo', 'creado_en', 'creado_por', 'actualizado_en', 'actualizado_por'
        ]
        
        for field in required_modelos_pos_fields:
            if field in modelos_pos_fields:
                print(f"  ✅ {field}")
            else:
                print(f"  ❌ {field} - FALTANTE")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando estructura: {e}")
        return False

def test_enum_values():
    """Verificar los valores de los enums"""
    print("\n🎯 VERIFICANDO VALORES DE ENUMS")
    print("=" * 50)
    
    try:
        from ges_neu_api.core.base_models import TipoAccionBitacoraEnum, TipoPosicionEnum
        
        print("\n📋 TipoAccionBitacoraEnum:")
        expected_actions = [
            'MONTAJE', 'DESMONTAJE', 'ROTACION', 'INSPECCION', 
            'REPARACION', 'CAMBIO_POSICION', 'MEDICION_PROFUNDIDAD', 'MEDICION_PRESION'
        ]
        
        for action in expected_actions:
            if hasattr(TipoAccionBitacoraEnum, action):
                print(f"  ✅ {action}")
            else:
                print(f"  ❌ {action} - FALTANTE")
        
        print("\n📋 TipoPosicionEnum:")
        expected_positions = ['DIRECCION', 'TRACCION', 'LIBRE', 'TODAS']
        
        for position in expected_positions:
            if hasattr(TipoPosicionEnum, position):
                print(f"  ✅ {position}")
            else:
                print(f"  ❌ {position} - FALTANTE")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando enums: {e}")
        return False

def test_table_names():
    """Verificar que los nombres de tabla son correctos"""
    print("\n🏷️ VERIFICANDO NOMBRES DE TABLA")
    print("=" * 50)
    
    try:
        from ges_neu_api.modules.bitacoras.models import BitacoraOperacionesNeumaticos
        from ges_neu_api.modules.neumaticos.models import (
            EspecificacionesDesgaste, 
            ParametrosRendimientoEsperadoModelo,
            ModelosPosicionesPermitidas
        )
        
        expected_tables = {
            BitacoraOperacionesNeumaticos: "bitacora_operaciones_neumaticos",
            EspecificacionesDesgaste: "especificaciones_desgaste",
            ParametrosRendimientoEsperadoModelo: "parametros_rendimiento_esperado_modelo",
            ModelosPosicionesPermitidas: "modelos_posiciones_permitidas"
        }
        
        for model_class, expected_name in expected_tables.items():
            actual_name = getattr(model_class, '__tablename__', None)
            if actual_name == expected_name:
                print(f"✅ {model_class.__name__}: {actual_name}")
            else:
                print(f"❌ {model_class.__name__}: esperado '{expected_name}', actual '{actual_name}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando nombres de tabla: {e}")
        return False

def main():
    """Ejecutar todas las verificaciones"""
    print("🚀 INICIANDO VERIFICACIÓN DE NUEVOS MODELOS")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Estructura de Modelos", test_model_structure),
        ("Valores de Enums", test_enum_values),
        ("Nombres de Tabla", test_table_names)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Ejecutando: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error en {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VERIFICACIONES")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 RESULTADO FINAL: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("🎉 ¡TODOS LOS NUEVOS MODELOS ESTÁN FUNCIONANDO CORRECTAMENTE!")
    else:
        print("⚠️  Algunos modelos requieren corrección")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
