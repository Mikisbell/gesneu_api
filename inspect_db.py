#!/usr/bin/env python3
"""
Script simple para inspeccionar la base de datos existente
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine import reflection

# Cargar variables de entorno
load_dotenv()

def main():
    # Construir URL de conexión desde variables de entorno
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'B3ll1c0s')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'ges_neu_bd')
    
    database_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    try:
        # Crear engine
        engine = create_engine(database_url)
        
        # Probar conexión
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print("Conexion exitosa a PostgreSQL")
            print(f"Versión: {version}")
            
            # Obtener tablas
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            print(f"\nTablas encontradas ({len(tables)}):")
            for table in tables:
                print(f"  - {table}")
                
                # Obtener columnas de cada tabla
                columns = inspector.get_columns(table)
                print(f"    Columnas ({len(columns)}):")
                for col in columns:
                    print(f"      • {col['name']}: {col['type']} {'NOT NULL' if not col['nullable'] else 'NULL'}")
                
                # Obtener claves primarias
                pk = inspector.get_pk_constraint(table)
                if pk['constrained_columns']:
                    print(f"    PK: {', '.join(pk['constrained_columns'])}")
                
                # Obtener claves foráneas
                fks = inspector.get_foreign_keys(table)
                if fks:
                    print(f"    FK:")
                    for fk in fks:
                        print(f"      {', '.join(fk['constrained_columns'])} -> {fk['referred_table']}.{', '.join(fk['referred_columns'])}")
                
                print()
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
