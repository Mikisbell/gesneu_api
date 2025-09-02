import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='ges_neu_bd',
    user='postgres',
    password='B3ll1c0s'
)

cursor = conn.cursor()

# Verificar si existe la función
cursor.execute("SELECT COUNT(*) FROM pg_proc WHERE proname = 'f_immutable_lower_unaccent'")
count = cursor.fetchone()[0]

if count == 0:
    print("Creando función f_immutable_lower_unaccent...")
    cursor.execute("""
        CREATE OR REPLACE FUNCTION f_immutable_lower_unaccent(text)
        RETURNS text AS $$
        BEGIN
            RETURN lower(unaccent($1));
        END;
        $$ LANGUAGE plpgsql IMMUTABLE;
    """)
    conn.commit()
    print("Función creada")
else:
    print("Función ya existe")

# Verificar extensión unaccent
cursor.execute("SELECT COUNT(*) FROM pg_extension WHERE extname = 'unaccent'")
unaccent_count = cursor.fetchone()[0]

if unaccent_count == 0:
    print("Instalando extensión unaccent...")
    cursor.execute("CREATE EXTENSION IF NOT EXISTS unaccent")
    conn.commit()
    print("Extensión instalada")
else:
    print("Extensión unaccent ya existe")

cursor.close()
conn.close()
print("Verificación completada")
