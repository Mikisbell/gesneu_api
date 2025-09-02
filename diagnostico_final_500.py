#!/usr/bin/env python3
"""
Diagnóstico final del error 500 - Verificar todos los componentes
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def diagnosticar_error_completo():
    try:
        print("🔍 DIAGNÓSTICO FINAL ERROR 500")
        print("=" * 40)
        
        # 1. Verificar importaciones básicas
        print("1️⃣ Verificando importaciones...")
        from ges_neu_api.modules.catalogos.models import Proveedor, TipoProveedorEnum
        from ges_neu_api.modules.catalogos.schemas import ProveedorRead
        from ges_neu_api.core.database import get_session
        print("   ✅ Importaciones OK")
        
        # 2. Verificar enum corregido
        print("\n2️⃣ Verificando enum TipoProveedorEnum...")
        valores_enum = [e.value for e in TipoProveedorEnum]
        print(f"   📋 Valores: {valores_enum}")
        
        # 3. Probar conexión directa a BD
        print("\n3️⃣ Probando conexión directa...")
        async for session in get_session():
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1"))
            print("   ✅ Conexión BD OK")
            
            # 4. Verificar tabla proveedores existe
            print("\n4️⃣ Verificando tabla proveedores...")
            result = await session.execute(text("SELECT COUNT(*) FROM proveedores"))
            count = result.scalar()
            print(f"   📊 Registros: {count}")
            
            # 5. Probar consulta con modelo
            print("\n5️⃣ Probando consulta con modelo...")
            from sqlalchemy import select
            try:
                result = await session.execute(select(Proveedor).limit(1))
                proveedores = result.scalars().all()
                print(f"   ✅ Consulta modelo OK: {len(proveedores)} registros")
            except Exception as e:
                print(f"   ❌ Error en consulta modelo: {e}")
                return False
            
            # 6. Probar servicio
            print("\n6️⃣ Probando servicio...")
            from ges_neu_api.modules.catalogos.service import CatalogService
            service = CatalogService()
            try:
                proveedores = await service.get_proveedores(session)
                print(f"   ✅ Servicio OK: {len(proveedores)} proveedores")
            except Exception as e:
                print(f"   ❌ Error en servicio: {e}")
                import traceback
                traceback.print_exc()
                return False
            
            break
        
        print("\n✅ TODOS LOS COMPONENTES FUNCIONAN")
        print("🤔 El error 500 debe estar en el router o autenticación")
        
        # 7. Verificar router
        print("\n7️⃣ Verificando router...")
        from ges_neu_api.modules.catalogos.router import router
        print(f"   📋 Router cargado: {len(router.routes)} rutas")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(diagnosticar_error_completo())
