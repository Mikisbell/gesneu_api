#!/usr/bin/env python3
"""
Test script to validate model-schema alignment and identify 500 error causes
"""
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

# Import models and schemas
from ges_neu_api.modules.neumaticos.models import ModeloNeumatico
from ges_neu_api.modules.neumaticos.schemas import ModeloResponse
from ges_neu_api.modules.inventario.models import ParametrosInventario
from ges_neu_api.core.config import settings

async def test_modelo_validation():
    """Test ModeloNeumatico to ModeloResponse validation"""
    print("🔍 Testing ModeloNeumatico validation...")
    
    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        async with async_session() as session:
            # Get first modelo from database
            result = await session.execute(select(ModeloNeumatico).limit(1))
            modelo = result.scalar_one_or_none()
            
            if not modelo:
                print("❌ No models found in database")
                return False
                
            print(f"✅ Found model: {modelo.nombre_modelo}")
            print(f"   ID: {modelo.id}")
            print(f"   Fabricante ID: {modelo.fabricante_id}")
            
            # Try to validate with ModeloResponse schema
            try:
                modelo_response = ModeloResponse.model_validate(modelo)
                print("✅ Model validation successful")
                return True
            except Exception as e:
                print(f"❌ Model validation failed: {str(e)}")
                print(f"   Model attributes: {list(modelo.__dict__.keys())}")
                
                # Check which fields are missing or mismatched
                schema_fields = set(ModeloResponse.model_fields.keys())
                model_fields = set(attr for attr in dir(modelo) if not attr.startswith('_'))
                
                missing_in_model = schema_fields - model_fields
                missing_in_schema = model_fields - schema_fields
                
                if missing_in_model:
                    print(f"   Fields missing in model: {missing_in_model}")
                if missing_in_schema:
                    print(f"   Fields missing in schema: {missing_in_schema}")
                
                return False
                
    except Exception as e:
        print(f"❌ Database connection error: {str(e)}")
        return False
    finally:
        await engine.dispose()

async def test_parametros_inventario():
    """Test ParametrosInventario table access"""
    print("\n🔍 Testing ParametrosInventario access...")
    
    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        async with async_session() as session:
            # Try to query parametros_inventario table
            result = await session.execute(select(ParametrosInventario).limit(5))
            parametros = list(result.scalars().all())
            
            print(f"✅ Found {len(parametros)} inventory parameters")
            
            if parametros:
                param = parametros[0]
                print(f"   Sample parameter: {param.parametro_tipo}")
                print(f"   Model ID: {param.modelo_id}")
                print(f"   Active: {param.activo}")
            
            return True
            
    except Exception as e:
        print(f"❌ ParametrosInventario query failed: {str(e)}")
        return False
    finally:
        await engine.dispose()

async def main():
    print("🧪 Model Validation Test Suite")
    print("=" * 40)
    
    # Test modelo validation
    modelo_ok = await test_modelo_validation()
    
    # Test parametros inventario
    parametros_ok = await test_parametros_inventario()
    
    print("\n📊 Test Results:")
    print(f"   ModeloNeumatico validation: {'✅ PASS' if modelo_ok else '❌ FAIL'}")
    print(f"   ParametrosInventario access: {'✅ PASS' if parametros_ok else '❌ FAIL'}")
    
    if modelo_ok and parametros_ok:
        print("\n🎉 All tests passed - API should work correctly")
    else:
        print("\n⚠️  Some tests failed - API endpoints may have errors")

if __name__ == "__main__":
    asyncio.run(main())
