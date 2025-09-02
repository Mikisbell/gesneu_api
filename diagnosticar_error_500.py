#!/usr/bin/env python3
"""
Diagnóstico específico del error 500 en endpoints de catálogos
"""
import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def diagnosticar_proveedores():
    """Diagnostica el problema específico con el endpoint de proveedores"""
    try:
        print("🔍 DIAGNÓSTICO DEL ERROR 500 - PROVEEDORES")
        print("=" * 50)
        
        # 1. Verificar importación de modelos
        print("1️⃣ Verificando importación de modelos...")
        try:
            from ges_neu_api.modules.catalogos.models import Proveedor, TipoProveedorEnum
            from ges_neu_api.modules.catalogos.schemas import ProveedorRead
            print("   ✅ Modelos importados correctamente")
        except Exception as e:
            print(f"   ❌ Error en importación de modelos: {e}")
            return False
        
        # 2. Verificar conexión a BD usando el mismo método que la API
        print("\n2️⃣ Verificando conexión usando configuración de la API...")
        try:
            from ges_neu_api.core.database import get_session
            from ges_neu_api.core.config import settings
            print(f"   📊 DB URL: {settings.DATABASE_URL}")
            
            # Intentar obtener una sesión
            async for session in get_session():
                print("   ✅ Sesión de BD obtenida correctamente")
                
                # 3. Verificar consulta directa a la tabla
                print("\n3️⃣ Ejecutando consulta directa a proveedores...")
                from sqlalchemy import select, text
                
                # Consulta simple para verificar la tabla
                result = await session.execute(text("SELECT COUNT(*) FROM proveedores"))
                count = result.scalar()
                print(f"   📈 Registros en proveedores: {count}")
                
                # Consulta usando el modelo SQLAlchemy
                print("\n4️⃣ Probando consulta con modelo SQLAlchemy...")
                result = await session.execute(select(Proveedor).limit(1))
                proveedores = result.scalars().all()
                print(f"   📋 Proveedores obtenidos con modelo: {len(proveedores)}")
                
                if len(proveedores) > 0:
                    proveedor = proveedores[0]
                    print(f"   📄 Ejemplo: ID={proveedor.id}, Nombre={proveedor.nombre}")
                
                break
                
        except Exception as e:
            print(f"   ❌ Error en conexión/consulta BD: {e}")
            print(f"   🔧 Tipo de error: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return False
        
        # 4. Verificar el servicio de catálogos
        print("\n5️⃣ Verificando servicio de catálogos...")
        try:
            from ges_neu_api.modules.catalogos.service import CatalogService
            service = CatalogService()
            print("   ✅ Servicio de catálogos instanciado correctamente")
            
            # Probar el método get_proveedores
            async for session in get_session():
                proveedores = await service.get_proveedores(session)
                print(f"   📊 Servicio devolvió {len(proveedores)} proveedores")
                break
                
        except Exception as e:
            print(f"   ❌ Error en servicio de catálogos: {e}")
            print(f"   🔧 Tipo de error: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n✅ DIAGNÓSTICO COMPLETADO - Todo parece funcionar correctamente")
        print("🤔 El error 500 podría estar en el router o en la autenticación")
        return True
        
    except Exception as e:
        print(f"❌ ERROR GENERAL EN DIAGNÓSTICO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(diagnosticar_proveedores())
