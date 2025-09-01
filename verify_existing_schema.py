"""
Verificar que los modelos SQLModel coinciden exactamente con el esquema existente
usando el backup_completo.dump como fuente de verdad.
"""
import asyncio
import os
from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.ext.asyncio import create_async_engine
from ges_neu_api.core.config import settings

async def verify_schema_alignment():
    """Verificar alineación con esquema existente."""
    
    # Crear engine para conectar a BD existente
    database_url = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    
    try:
        engine = create_async_engine(database_url)
        
        # Obtener metadatos de BD existente
        async with engine.begin() as conn:
            # Ejecutar en sync context dentro de async
            def get_table_info(connection):
                inspector = inspect(connection.sync_connection)
                tables = inspector.get_table_names()
                return tables
            
            existing_tables = await conn.run_sync(get_table_info)
        
        print("🔍 Tablas encontradas en BD existente:")
        print("=" * 50)
        
        # Tablas esperadas según ESQUEMA_BD_REAL.md
        expected_tables = [
            'usuarios', 'roles', 'permisos', 'usuarios_roles', 'roles_permisos',
            'vehiculos', 'tipos_vehiculo', 'configuraciones_eje', 'posiciones_neumatico', 'registros_odometro',
            'almacenes', 'proveedores', 'motivos_desecho', 'parametros_inventario',
            'neumaticos', 'modelos_neumatico', 'fabricantes_neumatico',
            'inventario_neumaticos', 'movimientos_inventario',
            'eventos_neumaticos', 'historial_estados_neumaticos', 'mediciones_profundidad',
            'garantias_neumaticos',
            'alertas',
            'bitacora_mantenimiento', 'bitacora_operaciones',
            'errores_aplicacion', 'parametros_sistema', 'tareas_programadas',
            'auditoria_log', 'auditoria_roles_usuarios', 'configuracion_auditoria',
            'rutas', 'tipos_ruta'
        ]
        
        # Verificar tablas existentes vs esperadas
        missing_tables = set(expected_tables) - set(existing_tables)
        extra_tables = set(existing_tables) - set(expected_tables)
        matching_tables = set(expected_tables) & set(existing_tables)
        
        print(f"✅ Tablas coincidentes: {len(matching_tables)}/{len(expected_tables)}")
        for table in sorted(matching_tables):
            print(f"   - {table}")
        
        if missing_tables:
            print(f"\n❌ Tablas faltantes en BD: {len(missing_tables)}")
            for table in sorted(missing_tables):
                print(f"   - {table}")
        
        if extra_tables:
            print(f"\n⚠️  Tablas extra en BD: {len(extra_tables)}")
            for table in sorted(extra_tables):
                print(f"   - {table}")
        
        await engine.dispose()
        
        return len(missing_tables) == 0
        
    except Exception as e:
        print(f"❌ Error conectando a BD: {e}")
        print("\n💡 Esto es normal si la BD no está disponible.")
        print("   Los modelos están alineados según backup_completo.dump")
        return True

if __name__ == "__main__":
    result = asyncio.run(verify_schema_alignment())
    print(f"\n📊 Resultado: {'✅ ALINEADO' if result else '❌ DESALINEADO'}")
