#!/usr/bin/env python3
"""
Test directo del endpoint fabricantes para diagnosticar error 422
"""
import sys
sys.path.append('.')

import asyncio
from ges_neu_api.core.database import get_session
from ges_neu_api.modules.neumaticos.service import NeumaticoService
from ges_neu_api.modules.neumaticos.models import FabricanteNeumatico
from ges_neu_api.modules.neumaticos.schemas import FabricanteResponse
from sqlalchemy import select

async def test_fabricantes_directo():
    """Test directo del servicio de fabricantes"""
    print("=== TEST DIRECTO FABRICANTES ===")
    
    async for session in get_session():
        try:
            # 1. Consulta directa a BD
            result = await session.execute(select(FabricanteNeumatico))
            fabricantes_bd = result.scalars().all()
            print(f"Fabricantes en BD: {len(fabricantes_bd)}")
            
            if fabricantes_bd:
                fab = fabricantes_bd[0]
                print(f"Primer fabricante BD:")
                print(f"  id: {fab.id}")
                print(f"  nombre: {fab.nombre}")
                print(f"  codigo_abreviado: {fab.codigo_abreviado}")
                print(f"  activo: {fab.activo}")
                print(f"  creado_en: {fab.creado_en}")
                
                # 2. Probar conversión a schema
                try:
                    response_obj = FabricanteResponse.model_validate(fab)
                    print("✅ Conversión a schema exitosa")
                    print(f"Response: {response_obj.model_dump()}")
                except Exception as e:
                    print(f"❌ Error en conversión schema: {e}")
            
            # 3. Probar servicio completo
            service = NeumaticoService(session)
            try:
                fabricantes_service = await service.get_fabricantes()
                print(f"✅ Servicio retorna: {len(fabricantes_service)} fabricantes")
            except Exception as e:
                print(f"❌ Error en servicio: {e}")
                import traceback
                traceback.print_exc()
                
        except Exception as e:
            print(f"❌ Error general: {e}")
            import traceback
            traceback.print_exc()
        break

if __name__ == "__main__":
    asyncio.run(test_fabricantes_directo())
