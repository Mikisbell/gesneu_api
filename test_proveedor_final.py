#!/usr/bin/env python3
"""
Script final para probar la creación de proveedores con ENUM corregido
"""
import asyncio
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from ges_neu_api.core.config import get_settings
from ges_neu_api.modules.catalogos.service import CatalogService
from ges_neu_api.modules.catalogos.schemas import ProveedorCreate

async def test_create_proveedor_final():
    """Probar creación de proveedor con nombre único"""
    settings = get_settings()
    
    # Crear engine
    engine = create_async_engine(
        settings.SQLALCHEMY_DATABASE_URI,
        echo=True
    )
    
    # Crear sesión
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            service = CatalogService(session)
            
            # Generar nombre único con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            
            print(f"🔍 PRUEBA FINAL - Crear proveedor con ENUM corregido")
            
            # Datos con nombre único
            proveedor_data = ProveedorCreate(
                nombre=f"Proveedor Test {timestamp}_{unique_id}",
                tipo="DISTRIBUIDOR",  # Usar valor válido del ENUM
                telefono="987654321",
                email=f"test_{unique_id}@proveedor.com",
                ruc=None  # Sin RUC para evitar duplicados
            )
            
            print(f"📋 Datos a crear: {proveedor_data.model_dump()}")
            
            # Crear proveedor
            resultado = await service.create_proveedor(proveedor_data)
            print(f"✅ Proveedor creado exitosamente!")
            print(f"   ID: {resultado.id}")
            print(f"   Nombre: {resultado.nombre}")
            print(f"   Tipo: {resultado.tipo}")
            print(f"   Creado en: {resultado.creado_en}")
            
            # Probar también con tipo None
            print(f"\n🔍 PRUEBA 2 - Crear proveedor con tipo=None")
            proveedor_data_2 = ProveedorCreate(
                nombre=f"Proveedor Sin Tipo {timestamp}_{unique_id}",
                tipo=None,  # Probar con None
                telefono="123456789",
                email=f"sinTipo_{unique_id}@proveedor.com"
            )
            
            resultado_2 = await service.create_proveedor(proveedor_data_2)
            print(f"✅ Proveedor sin tipo creado exitosamente!")
            print(f"   ID: {resultado_2.id}")
            print(f"   Nombre: {resultado_2.nombre}")
            print(f"   Tipo: {resultado_2.tipo}")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error: {e}")
            print(f"   Tipo de error: {type(e).__name__}")
            import traceback
            traceback.print_exc()
        finally:
            await session.close()
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_create_proveedor_final())
