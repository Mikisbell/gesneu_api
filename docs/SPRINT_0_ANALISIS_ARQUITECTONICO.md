# Sprint 0: Análisis de Desviaciones Arquitectónicas - Reporte

## 📊 Resumen Ejecutivo

**Fecha**: 3 Septiembre 2025  
**Sprint**: 0 - Refactorización MCP  
**Estado**: En Progreso  
**Objetivo**: Identificar desviaciones del patrón Modelo-Controlador-Presentación en la API GesNeu

## 🎯 Metodología de Análisis

### Criterios de Evaluación MCP:
1. **Modelo (M)**: Solo lógica de datos y validaciones de negocio
2. **Controlador (C)**: Orquestación y lógica de negocio pura
3. **Presentación (P)**: Manejo HTTP, validación de entrada, formateo de respuesta

### ❌ Desviaciones Identificadas:

#### **CRÍTICA: HTTPException en Services**
```python
# INCORRECTO - Encontrado en múltiples services
from fastapi import HTTPException  # ❌ Lógica HTTP en capa de negocio
```

**Módulos Afectados:**
- `auth/service.py` - 1 importación HTTPException
- `neumaticos/service.py` - 1 importación HTTPException

#### **CRÍTICA: Lógica HTTP en Routers**
```python
# PATRÓN INCORRECTO encontrado en routers
@router.get("/endpoint")
async def endpoint(service: Service = Depends(get_service)):
    try:
        result = await service.method()
        if not result:
            raise HTTPException(status_code=404, detail="Not found")  # ❌
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  # ❌
```

**Módulos con Mayor Densidad de HTTPException:**
1. `auth/router.py` - 32 ocurrencias
2. `sistema/router.py` - 18 ocurrencias  
3. `catalogos/router.py` - 13 ocurrencias
4. `neumaticos/router.py` - 11 ocurrencias
5. `inventario/router.py` - 10 ocurrencias

## 🔍 Análisis Detallado por Módulo

### 1. Módulo Auth
**Estado**: ⚠️ Desviaciones Moderadas
- **Router**: 32 HTTPException (manejo directo de errores HTTP)
- **Service**: 1 HTTPException import + uso de excepciones core ✅
- **Dependencies**: 10 HTTPException (validación de tokens)

**Observación**: Módulo parcialmente refactorizado, usa excepciones personalizadas pero mantiene HTTPException.

### 2. Módulo Neumáticos  
**Estado**: ❌ Desviaciones Críticas
- **Router**: 11 HTTPException
- **Service**: 1 HTTPException import
- **Patrón**: Service devuelve None, Router maneja HTTPException

### 3. Módulo Sistema
**Estado**: ❌ Desviaciones Críticas  
- **Router**: 18 HTTPException
- **Alta densidad de manejo HTTP en presentación**

### 4. Módulos Restantes
**Estado**: ❌ Desviaciones Generalizadas
- Todos los módulos siguen el mismo patrón problemático
- Services importan HTTPException
- Routers manejan lógica de errores directamente

## 🚨 Problemas Arquitectónicos Identificados

### **Problema 1: Acoplamiento HTTP-Negocio**
```python
# ❌ INCORRECTO - Service acoplado a HTTP
class NeumaticoService:
    async def get_neumatico(self, id: UUID):
        neumatico = await self.db.get(id)
        if not neumatico:
            raise HTTPException(status_code=404)  # ❌ HTTP en negocio
```

### **Problema 2: Responsabilidades Mezcladas**
```python
# ❌ INCORRECTO - Router con lógica de negocio
@router.get("/neumaticos/{id}")
async def get_neumatico(id: UUID, service = Depends()):
    if not id:  # ❌ Validación de negocio en router
        raise HTTPException(400, "ID requerido")
    
    result = await service.get(id)
    if not result:  # ❌ Lógica de negocio en router
        raise HTTPException(404, "No encontrado")
```

### **Problema 3: Falta de Excepciones de Dominio**
- No existen excepciones específicas del dominio
- HTTPException usado para todo tipo de errores
- Pérdida de semántica de negocio

## ✅ Arquitectura Objetivo MCP

### **Modelo Correcto:**
```python
# ✅ CORRECTO - Excepciones de dominio
class RecursoNoEncontradoError(Exception):
    def __init__(self, recurso: str, id: str):
        self.recurso = recurso
        self.id = id
        super().__init__(f"{recurso} con ID {id} no encontrado")

# ✅ CORRECTO - Service puro
class NeumaticoService:
    async def get_neumatico(self, id: UUID) -> Neumatico:
        neumatico = await self.db.get(id)
        if not neumatico:
            raise RecursoNoEncontradoError("Neumático", str(id))
        return neumatico

# ✅ CORRECTO - Router como presentación
@router.get("/neumaticos/{id}")
async def get_neumatico(id: UUID, service = Depends()):
    try:
        return await service.get_neumatico(id)
    except RecursoNoEncontradoError:
        raise HTTPException(404, "Neumático no encontrado")
```

## 📋 Plan de Refactorización

### **Fase 1: Sistema de Excepciones** (Siguiente tarea)
1. Crear `core/exceptions.py`
2. Definir excepciones de dominio
3. Crear mapeo excepción → HTTP status

### **Fase 2: Refactorización Services**
1. Remover imports HTTPException
2. Usar excepciones de dominio
3. Lógica de negocio pura

### **Fase 3: Refactorización Routers**  
1. Manejo centralizado de excepciones
2. Solo lógica de presentación
3. Validación de entrada únicamente

### **Fase 4: Validación**
1. Tests de regresión
2. Verificar funcionalidad mantenida
3. Documentar cambios

## 🎯 Métricas de Éxito

- **HTTPException en Services**: 0 (actualmente: 2+)
- **Excepciones de dominio**: 100% cobertura
- **Separación de capas**: Completa
- **Tests pasando**: 27/27 endpoints

## 📝 Conclusiones

1. **Desviación Generalizada**: Todos los módulos tienen el mismo patrón problemático
2. **Acoplamiento Crítico**: Services acoplados a FastAPI/HTTP
3. **Refactorización Necesaria**: Sistema completo requiere reestructuración
4. **Impacto Controlado**: Cambios internos, API externa se mantiene igual

**Próximo Paso**: Crear sistema de excepciones personalizadas en `core/exceptions.py`
