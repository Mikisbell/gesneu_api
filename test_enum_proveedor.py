#!/usr/bin/env python3
"""
Script para probar específicamente el ENUM tipoproveedorenum
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from ges_neu_api.core.config import get_settings
from ges_neu_api.modules.catalogos.models import Proveedor, TipoProveedorEnum
from ges_neu_api.modules.catalogos.schemas import ProveedorCreate

async def test_enum_proveedor():
    """Probar creación de proveedor con ENUM específico"""
    settings = get_settings()
    
    # Crear engine
    engine = create_async_engine(
        settings.database_url,
        echo=True
    )
    
    # Crear sesión
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            print("🔍 PRUEBA ENUM - Verificar ENUM en BD")
            
            # Verificar que el ENUM existe en la BD
            result = await session.execute(text("""
                SELECT enumlabel 
                FROM pg_enum 
                WHERE enumtypid = (
                    SELECT oid 
                    FROM pg_type 
                    WHERE typname = 'tipoproveedorenum'
                )
                ORDER BY enumsortorder;
            """))
            enum_values = [row[0] for row in result.fetchall()]
            print(f"📋 Valores ENUM en BD: {enum_values}")
            
            # Probar inserción directa con SQL
            print("\n🔍 PRUEBA 1 - Inserción directa con SQL")
            await session.execute(text("""
                INSERT INTO proveedores (nombre, tipo, telefono, email, activo)
                VALUES ('Test SQL Directo', 'DISTRIBUIDOR', '123456789', 'sql@test.com', true)
            """))
            await session.commit()
            print("✅ Inserción SQL directa exitosa")
            
            # Probar con modelo SQLModel
            print("\n🔍 PRUEBA 2 - Con modelo SQLModel")
            proveedor = Proveedor(
                nombre="Test SQLModel",
                tipo=TipoProveedorEnum.FABRICANTE,
                telefono="987654321",
                email="sqlmodel@test.com"
            )
            
            session.add(proveedor)
            await session.commit()
            print("✅ Inserción con SQLModel exitosa")
            
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
    asyncio.run(test_enum_proveedor())
