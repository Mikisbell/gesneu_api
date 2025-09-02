#!/usr/bin/env python3
import psycopg2

try:
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='ges_neu_bd',
        user='postgres',
        password='B3ll1c0s'
    )
    
    cursor = conn.cursor()
    
    # Verificar si existe la función f_immutable_lower_unaccent
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM pg_proc 
            WHERE proname = 'f_immutable_lower_unaccent'
        );
    """)
    
    funcion_existe = cursor.fetchone()[0]
    print(f"Función f_immutable_lower_unaccent existe: {funcion_existe}")
    
    if not funcion_existe:
        print("❌ PROBLEMA ENCONTRADO: La función f_immutable_lower_unaccent no existe")
        print("🔧 Esto explica el error 500 en el endpoint de proveedores")
        
        # Crear la función faltante
        print("📝 Creando función f_immutable_lower_unaccent...")
        cursor.execute("""
            CREATE OR REPLACE FUNCTION f_immutable_lower_unaccent(text)
            RETURNS text AS $$
            BEGIN
                RETURN lower(unaccent($1));
            END;
            $$ LANGUAGE plpgsql IMMUTABLE;
        """)
        
        conn.commit()
        print("✅ Función creada exitosamente")
    else:
        print("✅ La función existe correctamente")
    
    # Verificar la tabla proveedores
    cursor.execute("SELECT COUNT(*) FROM proveedores;")
    count = cursor.fetchone()[0]
    print(f"📊 Registros en proveedores: {count}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
