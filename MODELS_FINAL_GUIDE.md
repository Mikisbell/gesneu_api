# GesNeu API - Guía Final de Modelos

## Estado Actual de los Modelos

### ✅ Modelos Funcionando Correctamente

**AUTH MODELS** (`ges_neu_api/modules/auth/models.py`):
- `Usuario`, `Rol`, `Permiso` - Modelos principales
- `UsuariosRoles`, `RolesPermisos` - Tablas de unión
- **Status**: 100% funcional, importables sin errores

**VEHICULOS MODELS** (`ges_neu_api/modules/vehiculos/models.py`):
- `Vehiculos`, `TiposVehiculo`, `ConfiguracionesEje`
- `PosicionesNeumatico`, `RegistrosOdometro`
- **Status**: 100% funcional, importables sin errores

### ⚠️ Modelos con Conflictos de Metadatos SQLAlchemy

**NEUMATICOS, BITACORAS, CATALOGOS**:
- **Problema**: Definiciones duplicadas de tablas entre archivos
- **Causa**: SQLAlchemy mantiene registro global de metadatos
- **Solución**: Usar solo un archivo por módulo o nombres únicos de tablas

## Solución Recomendada

### Opción 1: Consolidación por Módulo (Recomendada)
1. Mantener un solo archivo `models.py` por módulo
2. Eliminar archivos `models_final.py`, `models_clean.py`, etc.
3. Consolidar todas las definiciones en el archivo principal

### Opción 2: Nombres Únicos de Tablas
1. Usar sufijos únicos en `__tablename__` (ej: `fabricantes_neumatico_v2`)
2. Actualizar referencias FK correspondientes
3. Generar migración para renombrar tablas en BD

## Archivos de Trabajo Creados

### Scripts de Verificación
- `verify_models_schema.py` - Verificación BD vs modelos
- `test_all_imports.py` - Testing de importabilidad
- `final_models_summary.py` - Resumen del estado

### Archivos de Modelos Experimentales
- `models_final.py` (varios módulos) - Intentos de consolidación
- `models_clean.py` - Modelos con nombres únicos
- `models_consolidated.py` - Modelos consolidados

## Configuración de Migraciones

### Estado Actual
- `migrations/env.py` actualizado con modelos funcionales
- Alembic configurado y detecta diferencias con BD existente
- Listo para generar migraciones incrementales

### Imports Funcionales en env.py
```python
from ges_neu_api.modules.auth.models import Usuario, Rol, Permiso, UsuariosRoles, RolesPermisos
from ges_neu_api.modules.vehiculos.models import Vehiculos, TiposVehiculo, ConfiguracionesEje, PosicionesNeumatico, RegistrosOdometro
```

## Próximos Pasos Recomendados

### Inmediatos
1. **Usar modelos funcionales** (auth, vehiculos) para desarrollo de API
2. **Implementar endpoints** basados en modelos estables
3. **Generar migraciones** solo para modelos funcionales

### Mediano Plazo
1. **Consolidar neumáticos** en archivo único
2. **Refactorizar bitácoras** eliminando conflictos con BaseModel
3. **Reorganizar catálogos** sin duplicados

### Largo Plazo
1. **Ejecutar migraciones completas** una vez resueltos conflictos
2. **Implementar endpoints** para todos los módulos
3. **Documentar API** completa

## Comandos Útiles

### Testing de Imports
```bash
python test_all_imports.py
```

### Verificación de Estado
```bash
python final_models_summary.py
```

### Verificación Alembic
```bash
alembic check
```

### Generar Migración (solo modelos funcionales)
```bash
alembic revision --autogenerate -m "Add auth and vehiculos models"
```

## Notas Importantes

1. **No importar múltiples archivos de modelos** del mismo módulo simultáneamente
2. **SQLAlchemy mantiene metadatos globales** - evitar definiciones duplicadas
3. **BaseModel incluye campos de auditoría** - no redefinir en modelos hijos
4. **Usar sa_column explícitamente** para control total de tipos y restricciones

## Estructura Recomendada Final

```
ges_neu_api/modules/
├── auth/
│   └── models.py ✅ (funcional)
├── vehiculos/
│   └── models.py ✅ (funcional)
├── neumaticos/
│   └── models.py ⚠️ (consolidar)
├── bitacoras/
│   └── models.py ⚠️ (refactorizar)
└── catalogos/
    └── models.py ⚠️ (reorganizar)
```
