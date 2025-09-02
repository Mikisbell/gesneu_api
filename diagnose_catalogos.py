#!/usr/bin/env python3
"""
Diagnóstico específico para error 500 en POST proveedores
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ges_neu_api.core.database import get_session
from ges_neu_api.modules.catalogos.service import CatalogService
from ges_neu_api.modules.catalogos.schemas import ProveedorCreate

async def test_create_proveedor():
    """Probar creación de proveedor directamente"""
    print("🔍 DIAGNÓSTICO - Crear proveedor directamente")
    
    try:
        # Obtener sesión de base de datos
        async for db in get_session():
            service = CatalogService(db)
            
            # Datos de prueba mínimos
            proveedor_data = ProveedorCreate(
                nombre="Test Proveedor Directo",
                telefono="987654321",
                email="directo@test.com"
            )
            
            print(f"📋 Datos a crear: {proveedor_data.model_dump()}")
            
            # Intentar crear
            resultado = await service.create_proveedor(proveedor_data)
            print(f"✅ Proveedor creado exitosamente: {resultado.nombre}")
            
            break
            
    except Exception as e:
        print(f"❌ Error al crear proveedor: {str(e)}")
        print(f"   Tipo de error: {type(e).__name__}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_create_proveedor())
