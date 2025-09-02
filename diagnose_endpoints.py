#!/usr/bin/env python3
"""
Diagnostic script to identify the root cause of endpoint errors
"""
import asyncio
import traceback
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text

from ges_neu_api.core.config import settings
from ges_neu_api.modules.neumaticos.models import ModeloNeumatico
from ges_neu_api.modules.neumaticos.schemas import ModeloResponse
from ges_neu_api.modules.inventario.models import ParametrosInventario

async def test_database_connection():
    """Test basic database connectivity"""
    print("🔌 Testing database connection...")
    
    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI)
    
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Database connected: {version}")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False
    finally:
        await engine.dispose()

async def test_modelos_neumatico_query():
    """Test the exact query used by the tire models endpoint"""
    print("\n🔍 Testing modelos_neumatico query...")
    
    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        async with async_session() as session:
            # Test the exact query from the service
            result = await session.execute(
                select(ModeloNeumatico).offset(0).limit(100)
            )
            modelos = list(result.scalars().all())
            print(f"✅ Found {len(modelos)} tire models")
            
            if modelos:
                modelo = modelos[0]
                print(f"   Sample model: {modelo.nombre_modelo}")
                
                # Test schema validation
                try:
                    modelo_response = ModeloResponse.model_validate(modelo)
                    print("✅ Schema validation successful")
                    return True
                except Exception as e:
                    print(f"❌ Schema validation failed: {str(e)}")
                    print(f"   Model dict: {modelo.__dict__}")
                    return False
            else:
                print("⚠️  No models found in database")
                return True
                
    except Exception as e:
        print(f"❌ Query failed: {str(e)}")
        print(f"   Traceback: {traceback.format_exc()}")
        return False
    finally:
        await engine.dispose()

async def test_parametros_inventario_query():
    """Test the parametros_inventario query"""
    print("\n🔍 Testing parametros_inventario query...")
    
    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        async with async_session() as session:
            # Test table existence
            result = await session.execute(
                text("SELECT COUNT(*) FROM parametros_inventario")
            )
            count = result.scalar()
            print(f"✅ parametros_inventario table exists with {count} records")
            
            # Test SQLModel query
            result = await session.execute(
                select(ParametrosInventario).offset(0).limit(10)
            )
            parametros = list(result.scalars().all())
            print(f"✅ SQLModel query returned {len(parametros)} parameters")
            
            return True
            
    except Exception as e:
        print(f"❌ parametros_inventario query failed: {str(e)}")
        print(f"   Traceback: {traceback.format_exc()}")
        return False
    finally:
        await engine.dispose()

async def test_table_schemas():
    """Test if all expected tables exist"""
    print("\n📋 Testing table existence...")
    
    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI)
    
    tables_to_check = [
        'modelos_neumatico',
        'parametros_inventario', 
        'fabricantes_neumatico',
        'neumaticos',
        'proveedores',
        'almacenes'
    ]
    
    try:
        async with engine.begin() as conn:
            for table in tables_to_check:
                try:
                    result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"✅ {table}: {count} records")
                except Exception as e:
                    print(f"❌ {table}: {str(e)}")
            return True
    except Exception as e:
        print(f"❌ Table check failed: {str(e)}")
        return False
    finally:
        await engine.dispose()

async def main():
    print("🩺 Endpoint Diagnostic Tool")
    print("=" * 40)
    
    # Test database connection
    db_ok = await test_database_connection()
    if not db_ok:
        print("❌ Cannot proceed without database connection")
        return
    
    # Test table schemas
    tables_ok = await test_table_schemas()
    
    # Test specific queries
    modelos_ok = await test_modelos_neumatico_query()
    parametros_ok = await test_parametros_inventario_query()
    
    print("\n📊 Diagnostic Results:")
    print(f"   Database connection: {'✅ OK' if db_ok else '❌ FAIL'}")
    print(f"   Table schemas: {'✅ OK' if tables_ok else '❌ FAIL'}")
    print(f"   Tire models query: {'✅ OK' if modelos_ok else '❌ FAIL'}")
    print(f"   Inventory params query: {'✅ OK' if parametros_ok else '❌ FAIL'}")
    
    if modelos_ok and parametros_ok:
        print("\n🎯 Root cause: Likely service or router configuration issue")
        print("   Recommendation: Check service dependencies and router registration")
    else:
        print("\n🎯 Root cause: Database model/schema mismatch")
        print("   Recommendation: Fix model field alignment with database schema")

if __name__ == "__main__":
    asyncio.run(main())
