# 🔐 ANÁLISIS DEL SISTEMA RBAC - API GesNeu

## 📋 Estructura del Sistema RBAC

### 🏗️ Modelos de Base de Datos

#### 1. **Usuarios** (`usuarios`)
- **ID**: UUID único
- **Username**: Nombre de usuario único
- **Email**: Email único
- **Password**: Hash de contraseña
- **es_superusuario**: Flag para superusuarios
- **activo**: Estado del usuario
- **Auditoría**: creado_en, creado_por, actualizado_en, actualizado_por

#### 2. **Roles** (`roles`)
- **ID**: UUID único
- **nombre**: Nombre del rol (único)
- **descripcion**: Descripción del rol
- **es_rol_sistema**: Flag para roles del sistema
- **Auditoría**: creado_en, creado_por, actualizado_en, actualizado_por

#### 3. **Permisos** (`permisos`)
- **ID**: UUID único
- **nombre_recurso**: Recurso protegido (ej: "vehiculos", "usuarios")
- **accion**: Acción permitida (ej: "read", "write", "delete")
- **descripcion**: Descripción del permiso
- **Auditoría**: creado_en

#### 4. **Tablas de Relación**
- **usuarios_roles**: Relación muchos a muchos entre usuarios y roles
- **roles_permisos**: Relación muchos a muchos entre roles y permisos

---

## 🔄 Flujo de Autenticación y Autorización

### 1. **Autenticación (Login)**
```
POST /api/v1/auth/login
├── Validar credenciales (username/password)
├── Generar token JWT con claims:
│   ├── sub: username
│   ├── exp: fecha expiración
│   └── iat: fecha emisión
└── Retornar access_token
```

### 2. **Validación de Token**
```
Middleware JWT
├── Extraer token del header Authorization
├── Decodificar y validar token
├── Obtener usuario desde BD por username
├── Verificar que usuario esté activo
└── Inyectar usuario en contexto de request
```

### 3. **Verificación de Permisos**
```
PermissionChecker(resource, action)
├── Verificar si es superusuario → ✅ PERMITIR TODO
├── Si no es superusuario:
│   ├── Consultar permisos del usuario
│   ├── Verificar permiso específico (recurso + acción)
│   └── ✅ PERMITIR o ❌ DENEGAR (403)
```

---

## 🛠️ Implementación Actual

### ✅ **Componentes Implementados**

1. **Modelos SQLModel** - Completamente definidos
2. **Autenticación JWT** - Funcionando correctamente
3. **Dependencias FastAPI** - Sistema de inyección listo
4. **PermissionChecker** - Clase para verificar permisos
5. **Servicios Base** - AuthService, UserService, PermissionService

### ⚠️ **Estado Actual del Sistema**

**IMPLEMENTACIÓN PERMISIVA TEMPORAL:**
```python
async def check_permission(self, user_id: UUID, resource: str, action: str) -> bool:
    # TODO: Reemplazar con verificación real contra roles/permisos en BD
    return True  # ← SIEMPRE PERMITE TODO
```

---

## 🎯 Cómo Usar el Sistema RBAC

### 1. **Proteger Endpoints con Permisos**
```python
from ges_neu_api.modules.auth.dependencies import PermissionChecker

# Crear verificador de permiso específico
require_vehiculos_read = PermissionChecker(resource="vehiculos", action="read")
require_vehiculos_write = PermissionChecker(resource="vehiculos", action="write")

@router.get("/vehiculos")
async def get_vehiculos(
    current_user: UserRead = Depends(require_vehiculos_read)  # ← Protegido
):
    return await vehiculos_service.get_all()
```

### 2. **Verificadores Predefinidos**
```python
# Para roles
has_role_read = PermissionChecker(resource="roles", action="read")
has_role_write = PermissionChecker(resource="roles", action="write")
has_role_delete = PermissionChecker(resource="roles", action="delete")

# Para usuarios
has_user_read = PermissionChecker(resource="users", action="read")
has_user_write = PermissionChecker(resource="users", action="write")
has_user_delete = PermissionChecker(resource="users", action="delete")
```

### 3. **Niveles de Acceso**
```python
# Solo autenticación (sin permisos específicos)
current_user: UserRead = Depends(get_current_user)

# Usuario activo
current_user: UserRead = Depends(get_current_active_user)

# Superusuario
current_user: UserRead = Depends(get_current_active_superuser)

# Permiso específico
current_user: UserRead = Depends(PermissionChecker("recurso", "accion"))
```

---

## 🚀 Para Activar RBAC Completo

### 1. **Completar PermissionService**
```python
async def check_permission(self, user_id: UUID, resource: str, action: str) -> bool:
    # 1. Obtener roles del usuario
    user_roles = await self.get_user_roles(user_id)
    
    # 2. Obtener permisos de los roles
    for role in user_roles:
        role_permissions = await self.get_role_permissions(role.id)
        
        # 3. Verificar si tiene el permiso específico
        for permission in role_permissions:
            if (permission.nombre_recurso == resource and 
                permission.accion == action):
                return True
    
    return False
```

### 2. **Crear Datos Iniciales**
```python
# Roles básicos
roles = [
    {"nombre": "admin", "descripcion": "Administrador del sistema"},
    {"nombre": "operador", "descripcion": "Operador de vehículos"},
    {"nombre": "consultor", "descripcion": "Solo lectura"}
]

# Permisos por módulo
permisos = [
    {"recurso": "vehiculos", "accion": "read"},
    {"recurso": "vehiculos", "accion": "write"},
    {"recurso": "neumaticos", "accion": "read"},
    {"recurso": "neumaticos", "accion": "write"},
    # ... más permisos
]
```

### 3. **Aplicar en Endpoints**
```python
@router.post("/vehiculos", dependencies=[Depends(PermissionChecker("vehiculos", "write"))])
@router.get("/vehiculos", dependencies=[Depends(PermissionChecker("vehiculos", "read"))])
@router.delete("/vehiculos/{id}", dependencies=[Depends(PermissionChecker("vehiculos", "delete"))])
```

---

## 📊 Estado Actual: **RBAC PREPARADO PERO PERMISIVO**

- ✅ **Estructura completa** - Modelos, servicios, dependencias
- ✅ **Autenticación funcionando** - JWT válido
- ✅ **Framework listo** - PermissionChecker implementado
- ⚠️ **Verificación deshabilitada** - Actualmente permite todo
- 🎯 **Listo para activar** - Solo falta completar check_permission()

El sistema está **arquitectónicamente completo** y listo para usar. Solo necesitas decidir qué permisos aplicar a cada endpoint y completar la lógica de verificación en `PermissionService.check_permission()`.
