#!/usr/bin/env python3
"""
Test schema validation to identify exact field mismatches
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from ges_neu_api.core.config import settings
from ges_neu_api.modules.neumaticos.models import ModeloNeumatico
from ges_neu_api.modules.neumaticos.schemas import ModeloResponse

async def test_modelo_validation():
    """Test ModeloNeumatico to ModeloResponse validation"""
    print("Testing ModeloNeumatico validation...")
    
    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI)
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
            
            # Get all model attributes
            model_dict = {}
            for attr in dir(modelo):
                if not attr.startswith('_') and not callable(getattr(modelo, attr)):
                    try:
                        value = getattr(modelo, attr)
                        model_dict[attr] = value
                        print(f"   {attr}: {value} ({type(value).__name__})")
                    except:
                        pass
            
            # Try to validate with ModeloResponse schema
            try:
                modelo_response = ModeloResponse.model_validate(modelo)
                print("✅ Model validation successful")
                return True
            except Exception as e:
                print(f"❌ Model validation failed: {str(e)}")
                
                # Check which fields are expected by schema
                schema_fields = set(ModeloResponse.model_fields.keys())
                model_fields = set(model_dict.keys())
                
                missing_in_model = schema_fields - model_fields
                extra_in_model = model_fields - schema_fields
                
                if missing_in_model:
                    print(f"   Fields missing in model: {missing_in_model}")
                if extra_in_model:
                    print(f"   Extra fields in model: {extra_in_model}")
                
                return False
                
    except Exception as e:
        print(f"❌ Database error: {str(e)}")
        return False
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_modelo_validation())
