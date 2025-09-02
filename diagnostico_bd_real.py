#!/usr/bin/env python3
"""
Diagnóstico directo de la base de datos para identificar errores 422 y 500
"""
import asyncio
import sys
import os
sys.path.append('.')

from ges_neu_api.core.database import get_engine
from sqlalchemy import text

async def verificar_tablas_existentes():
    """Verifica qué tablas existen realmente en la BD"""
    engine = get_engine()
    
    try:
        async with engine.begin() as conn:
            # Listar todas las tablas
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            
            tablas = [row[0] for row in result]
            print("=== TABLAS EXISTENTES EN BD ===")
            for tabla in tablas:
                print(f"  - {tabla}")
            
            # Verificar específicamente fabricantes_neumatico
            if 'fabricantes_neumatico' in tablas:
                print("\n=== ESTRUCTURA fabricantes_neumatico ===")
                result2 = await conn.execute(text("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = 'fabricantes_neumatico' 
                    ORDER BY ordinal_position
                """))
                
                for row in result2:
                    print(f"  {row.column_name}: {row.data_type} | nullable={row.is_nullable} | default={row.column_default}")
            else:
                print("❌ Tabla fabricantes_neumatico NO EXISTE")
            
            # Verificar tipos_vehiculo y vehiculos
            for tabla_vehiculo in ['tipos_vehiculo', 'vehiculos']:
                if tabla_vehiculo in tablas:
                    print(f"\n=== ESTRUCTURA {tabla_vehiculo} ===")
                    result3 = await conn.execute(text(f"""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns 
                        WHERE table_name = '{tabla_vehiculo}' 
                        ORDER BY ordinal_position
                    """))
                    
                    for row in result3:
                        print(f"  {row.column_name}: {row.data_type} | nullable={row.is_nullable}")
                else:
                    print(f"❌ Tabla {tabla_vehiculo} NO EXISTE")
                    
    except Exception as e:
        print(f"❌ Error conectando a BD: {e}")
        print("Verificar que PostgreSQL esté corriendo y configuración sea correcta")

if __name__ == "__main__":
    asyncio.run(verificar_tablas_existentes())
