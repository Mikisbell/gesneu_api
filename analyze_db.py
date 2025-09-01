#!/usr/bin/env python3
"""
Script para analizar el esquema de la base de datos existente
y generar los modelos SQLModel correspondientes.
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import sys
from typing import Dict, List, Any

def connect_to_db():
    """Conecta a la base de datos PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="ges_neu_bd",
            user="postgres",
            password="B3ll1c0s"
        )
        return conn
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def get_tables(conn):
    """Obtiene todas las tablas de la base de datos"""
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """)
    return [row['table_name'] for row in cursor.fetchall()]

def get_table_columns(conn, table_name):
    """Obtiene las columnas de una tabla específica"""
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("""
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default,
            character_maximum_length,
            numeric_precision,
            numeric_scale
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = %s
        ORDER BY ordinal_position;
    """, (table_name,))
    return cursor.fetchall()

def get_primary_keys(conn, table_name):
    """Obtiene las claves primarias de una tabla"""
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("""
        SELECT column_name
        FROM information_schema.key_column_usage
        WHERE table_schema = 'public'
        AND table_name = %s
        AND constraint_name IN (
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_schema = 'public'
            AND table_name = %s
            AND constraint_type = 'PRIMARY KEY'
        );
    """, (table_name, table_name))
    return [row['column_name'] for row in cursor.fetchall()]

def get_foreign_keys(conn, table_name):
    """Obtiene las claves foráneas de una tabla"""
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("""
        SELECT
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.key_column_usage AS kcu
        JOIN information_schema.constraint_column_usage AS ccu
            ON kcu.constraint_name = ccu.constraint_name
        WHERE kcu.table_schema = 'public'
        AND kcu.table_name = %s
        AND kcu.constraint_name IN (
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_schema = 'public'
            AND table_name = %s
            AND constraint_type = 'FOREIGN KEY'
        );
    """, (table_name, table_name))
    return cursor.fetchall()

def analyze_database():
    """Analiza toda la estructura de la base de datos"""
    conn = connect_to_db()
    if not conn:
        return
    
    try:
        tables = get_tables(conn)
        print("=== ANÁLISIS DE BASE DE DATOS GES_NEU_BD ===\n")
        print(f"Tablas encontradas: {len(tables)}")
        print("-" * 50)
        
        db_structure = {}
        
        for table in tables:
            print(f"\n📋 TABLA: {table}")
            print("=" * 40)
            
            # Obtener columnas
            columns = get_table_columns(conn, table)
            primary_keys = get_primary_keys(conn, table)
            foreign_keys = get_foreign_keys(conn, table)
            
            db_structure[table] = {
                'columns': columns,
                'primary_keys': primary_keys,
                'foreign_keys': foreign_keys
            }
            
            print("Columnas:")
            for col in columns:
                pk_indicator = " 🔑 PK" if col['column_name'] in primary_keys else ""
                fk_indicator = ""
                for fk in foreign_keys:
                    if fk['column_name'] == col['column_name']:
                        fk_indicator = f" 🔗 FK -> {fk['foreign_table_name']}.{fk['foreign_column_name']}"
                        break
                
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
                
                print(f"  - {col['column_name']}: {col['data_type']}{pk_indicator}{fk_indicator} ({nullable}){default}")
            
            if foreign_keys:
                print("\nRelaciones:")
                for fk in foreign_keys:
                    print(f"  - {fk['column_name']} -> {fk['foreign_table_name']}.{fk['foreign_column_name']}")
        
        return db_structure
        
    finally:
        conn.close()

if __name__ == "__main__":
    analyze_database()
