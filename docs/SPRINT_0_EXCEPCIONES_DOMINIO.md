# Sprint 0: Sistema de Excepciones de Dominio - Documentación

## 📋 Resumen

**Fecha**: 3 Septiembre 2025  
**Tarea**: Crear sistema de excepciones personalizadas  
**Estado**: ✅ Completado  
**Archivo**: `ges_neu_api/core/exceptions.py`

## 🎯 Objetivo Cumplido

Extender el sistema de excepciones existente con **excepciones específicas del dominio** para eliminar el acoplamiento HTTP-Negocio identificado en el análisis arquitectónico.

## 🔧 Excepciones de Dominio Creadas

### **1. RecursoNoEncontradoError**
```python
class RecursoNoEncontradoError(NotFoundException):
    def __init__(self, recurso: str, identificador: str, **kwargs):
        message = f"{recurso} con ID '{identificador}' no encontrado"
```
**Uso**: Reemplaza `HTTPException(404)` en services
**Ejemplo**: `RecursoNoEncontradoError("Neumático", "123e4567-e89b-12d3")`

### **2. OperacionInvalidaError**
```python
class OperacionInvalidaError(BusinessRuleError):
    def __init__(self, operacion: str, razon: str, **kwargs):
        message = f"Operación '{operacion}' inválida: {razon}"
```
**Uso**: Validaciones de reglas de negocio
**Ejemplo**: `OperacionInvalidaError("montaje", "neumático ya montado")`

### **3. EstadoInvalidoError**
```python
class EstadoInvalidoError(BusinessRuleError):
    def __init__(self, recurso: str, estado_actual: str, estado_destino: str, **kwargs):
        message = f"{recurso} no puede cambiar de '{estado_actual}' a '{estado_destino}'"
```
**Uso**: Transiciones de estado inválidas
**Ejemplo**: `EstadoInvalidoError("Neumático", "MONTADO", "NUEVO")`

### **4. DuplicadoError**
```python
class DuplicadoError(ConflictException):
    def __init__(self, recurso: str, campo: str, valor: str, **kwargs):
        message = f"{recurso} con {campo} '{valor}' ya existe"
```
**Uso**: Recursos duplicados (409 Conflict)
**Ejemplo**: `DuplicadoError("Usuario", "email", "user@example.com")`

### **5. InventarioInsuficienteError**
```python
class InventarioInsuficienteError(BusinessRuleError):
    def __init__(self, producto: str, disponible: int, requerido: int, **kwargs):
        message = f"Stock insuficiente de {producto}: disponible {disponible}, requerido {requerido}"
```
**Uso**: Control de stock
**Ejemplo**: `InventarioInsuficienteError("Neumático 205/55R16", 2, 5)`

### **6. NeumaticoNoDisponibleError**
```python
class NeumaticoNoDisponibleError(BusinessRuleError):
    def __init__(self, neumatico_id: str, estado_actual: str, operacion: str, **kwargs):
        message = f"Neumático {neumatico_id} en estado '{estado_actual}' no disponible para {operacion}"
```
**Uso**: Validaciones específicas de neumáticos
**Ejemplo**: `NeumaticoNoDisponibleError("NEU001", "DAÑADO", "montaje")`

### **7. VehiculoOcupadoError**
```python
class VehiculoOcupadoError(BusinessRuleError):
    def __init__(self, vehiculo_id: str, **kwargs):
        message = f"Vehículo {vehiculo_id} está ocupado y no puede ser modificado"
```
**Uso**: Validaciones de vehículos en uso
**Ejemplo**: `VehiculoOcupadoError("VEH001")`

## 🗺️ Mapeo HTTP Status

```python
EXCEPTION_STATUS_MAP = {
    RecursoNoEncontradoError: 404,           # Not Found
    OperacionInvalidaError: 422,             # Unprocessable Entity
    EstadoInvalidoError: 422,                # Unprocessable Entity
    DuplicadoError: 409,                     # Conflict
    DependenciaError: 422,                   # Unprocessable Entity
    InventarioInsuficienteError: 422,        # Unprocessable Entity
    NeumaticoNoDisponibleError: 422,         # Unprocessable Entity
    VehiculoOcupadoError: 422,               # Unprocessable Entity
}
```

## 🔄 Patrón de Uso Correcto

### **ANTES (Problemático)**
```python
# ❌ Service acoplado a HTTP
class NeumaticoService:
    async def get_neumatico(self, id: UUID):
        neumatico = await self.db.get(id)
        if not neumatico:
            raise HTTPException(404, "Neumático no encontrado")  # ❌
        return neumatico

# ❌ Router con lógica de negocio
@router.get("/neumaticos/{id}")
async def get_neumatico(id: UUID, service = Depends()):
    if not id:  # ❌ Validación en router
        raise HTTPException(400, "ID requerido")
    return await service.get_neumatico(id)
```

### **DESPUÉS (Correcto MCP)**
```python
# ✅ Service puro - Solo lógica de negocio
class NeumaticoService:
    async def get_neumatico(self, id: UUID) -> Neumatico:
        neumatico = await self.db.get(id)
        if not neumatico:
            raise RecursoNoEncontradoError("Neumático", str(id))  # ✅
        return neumatico

# ✅ Router como presentación - Solo HTTP
@router.get("/neumaticos/{id}")
async def get_neumatico(id: UUID, service = Depends()):
    # El manejador global convierte automáticamente la excepción
    return await service.get_neumatico(id)  # ✅
```

## 🚀 Beneficios Obtenidos

### **1. Desacoplamiento Completo**
- Services sin dependencias HTTP
- Lógica de negocio pura y testeable
- Reutilización entre capas

### **2. Semántica Clara**
- Excepciones expresan intención de negocio
- Mensajes de error consistentes
- Códigos de error específicos

### **3. Manejo Centralizado**
- `global_exception_handler` convierte automáticamente
- Respuestas JSON estandarizadas
- Logging centralizado de errores

### **4. Facilidad de Testing**
```python
# ✅ Test limpio sin HTTP
def test_neumatico_no_encontrado():
    with pytest.raises(RecursoNoEncontradoError) as exc_info:
        await service.get_neumatico("inexistente")
    
    assert exc_info.value.recurso == "Neumático"
    assert exc_info.value.identificador == "inexistente"
```

## 📝 Próximos Pasos

1. **Refactorizar Services**: Remover HTTPException imports
2. **Actualizar Routers**: Simplificar manejo de errores
3. **Actualizar Tests**: Usar nuevas excepciones
4. **Validar Funcionalidad**: Ejecutar suite completa

## ✅ Estado del Sistema

- **Excepciones Base**: ✅ Existían previamente
- **Excepciones Dominio**: ✅ Creadas (8 nuevas)
- **Mapeo HTTP**: ✅ Definido
- **Manejador Global**: ✅ Funcional
- **Documentación**: ✅ Completada

**Listo para Fase 2**: Refactorización de Services y Routers
