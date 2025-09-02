#!/usr/bin/env python3
"""
Verificar estructura real de BD para corregir modelos
"""
import psycopg2
from psycopg2.extras import RealDictCursor

def verificar_fabricantes_neumatico():
    """Verifica estructura real de fabricantes_neumatico"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            database='ges_neu_bd', 
            user='postgres',
            password='B3ll1c0s'
        )
        
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Estructura completa
            cur.execute("""
                SELECT column_name, data_type, character_maximum_length, 
                       is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'fabricantes_neumatico' 
                ORDER BY ordinal_position
            """)
            
            print("=== ESTRUCTURA REAL fabricantes_neumatico ===")
            for row in cur.fetchall():
                col = row['column_name']
                tipo = row['data_type']
                longitud = row['character_maximum_length']
                nullable = row['is_nullable']
                default = row['column_default']
                
                tipo_completo = f"{tipo}({longitud})" if longitud else tipo
                print(f"{col}: {tipo_completo} | null={nullable} | default={default}")
            
            # Constraints
            cur.execute("""
                SELECT constraint_name, constraint_type
                FROM information_schema.table_constraints 
                WHERE table_name = 'fabricantes_neumatico'
            """)
            
            print("\n=== CONSTRAINTS ===")
            for row in cur.fetchall():
                print(f"{row['constraint_name']}: {row['constraint_type']}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

def verificar_tipos_vehiculo():
    """Verifica estructura real de tipos_vehiculo"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            database='ges_neu_bd', 
            user='postgres',
            password='B3ll1c0s'
        )
        
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT column_name, data_type, character_maximum_length, 
                       is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'tipos_vehiculo' 
                ORDER BY ordinal_position
            """)
            
            print("\n=== ESTRUCTURA REAL tipos_vehiculo ===")
            for row in cur.fetchall():
                col = row['column_name']
                tipo = row['data_type']
                longitud = row['character_maximum_length']
                nullable = row['is_nullable']
                default = row['column_default']
                
                tipo_completo = f"{tipo}({longitud})" if longitud else tipo
                print(f"{col}: {tipo_completo} | null={nullable} | default={default}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verificar_fabricantes_neumatico()
    verificar_tipos_vehiculo()
