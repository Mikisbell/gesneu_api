#!/usr/bin/env python3
"""
Debug simple para configuraciones-eje
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ges_neu_api.modules.vehiculos.models import ConfiguracionesEje
from ges_neu_api.modules.vehiculos.service import VehiculosService
from ges_neu_api.core.database import get_session

async def test_config_eje():
    """Test directo del modelo ConfiguracionesEje"""
    try:
        print("🔍 Probando importación de ConfiguracionesEje...")
        print(f"✅ Modelo importado: {ConfiguracionesEje}")
        print(f"✅ Tabla: {ConfiguracionesEje.__tablename__}")
        
        print("\n🔍 Probando servicio...")
        async for session in get_session():
            service = VehiculosService(session)
            print(f"✅ Servicio creado: {service}")
            
            print("\n🔍 Ejecutando consulta...")
            result = await service.get_multi_configuraciones_eje()
            print(f"✅ Resultado: {len(result)} configuraciones encontradas")
            
            for config in result:
                print(f"  - ID: {config.id}, Tipo: {config.tipo_eje}, Eje: {config.numero_eje}")
            
            break
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_config_eje())
