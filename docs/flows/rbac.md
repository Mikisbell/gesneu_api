# Sistema RBAC (Role-Based Access Control)

Este diagrama muestra la estructura de roles, permisos y autorización en GesNeu API.

## Arquitectura RBAC

```mermaid
flowchart TD
    Usuario[Usuario] --> TieneRol{Tiene rol}
    TieneRol --> Admin[ADMINISTRADOR]
    TieneRol --> Gestor[GESTOR]
    TieneRol --> Operador[OPERADOR]
    TieneRol --> Consultor[CONSULTOR]
    
    Admin --> PermisosAdmin[40+ permisos<br/>Acceso total]
    Gestor --> PermisosGestor[30+ permisos<br/>Gestión + Operaciones]
    Operador --> PermisosOperador[15+ permisos<br/>Solo operaciones]
    Consultor --> PermisosConsultor[5+ permisos<br/>Solo lectura]
    
    PermisosAdmin --> Modulos[Acceso a módulos]
    PermisosGestor --> Modulos
    PermisosOperador --> Modulos
    PermisosConsultor --> Modulos
    
    Modulos --> Neumaticos[Neumáticos]
    Modulos --> Vehiculos[Vehículos]
    Modulos --> Operaciones[Operaciones]
    Modulos --> Reportes[Reportes]
    Modulos --> Usuarios[Usuarios]
    Modulos --> AdminPanel[Admin Panel]
    
    style Admin fill:#ff6b6b
    style Gestor fill:#ffd93d
    style Operador fill:#6bcf7f
    style Consultor fill:#4d96ff
```

## Roles y Permisos

### Matriz de Permisos por Módulo

```mermaid
%%{init: {'theme':'base'}}%%
graph TB
    subgraph Neumáticos
        NA[neumaticos:crear<br/>ADMIN, GESTOR]
        NB[neumaticos:leer<br/>TODOS]
        NC[neumaticos:actualizar<br/>ADMIN, GESTOR]
        ND[neumaticos:eliminar<br/>ADMIN]
    end
    
    subgraph Vehículos
        VA[vehiculos:crear<br/>ADMIN, GESTOR]
        VB[vehiculos:leer<br/>TODOS]
        VC[vehiculos:actualizar<br/>ADMIN, GESTOR]
        VD[vehiculos:eliminar<br/>ADMIN]
    end
    
    subgraph Operaciones
        OA[operaciones:montar<br/>ADMIN, GESTOR, OPERADOR]
        OB[operaciones:desmontar<br/>ADMIN, GESTOR, OPERADOR]
        OC[operaciones:inspeccionar<br/>ADMIN, GESTOR, OPERADOR]
        OD[operaciones:leer<br/>TODOS]
    end
    
    subgraph Usuarios
        UA[usuarios:crear<br/>ADMIN]
        UB[usuarios:leer<br/>ADMIN, GESTOR]
        UC[usuarios:actualizar<br/>ADMIN]
        UD[usuarios:eliminar<br/>ADMIN]
    end
    
    subgraph Reportes
        RA[reportes:generar<br/>ADMIN, GESTOR]
        RB[reportes:exportar<br/>ADMIN, GESTOR]
        RC[reportes:leer<br/>TODOS]
    end
    
    style NA fill:#ffebee
    style ND fill:#ffcdd2
    style UA fill:#ffebee
    style UD fill:#ffcdd2
```

## Flujo de Autorización

```mermaid
flowchart TD
    Request[Request HTTP] --> Middleware1[NextAuth Middleware]
    Middleware1 --> HasSession{Sesión<br/>válida?}
    
    HasSession -->|No| Redirect401[HTTP 401<br/>Redirigir a /login]
    Redirect401 --> End1([Login Page])
    
    HasSession -->|Sí| DecodeJWT[Decodificar JWT]
    DecodeJWT --> GetPerms[Obtener permisos<br/>del token]
    
    GetPerms --> AuthorizationMiddleware[Authorization Middleware]
    AuthorizationMiddleware --> CheckPerm{Tiene permiso<br/>requerido?}
    
    CheckPerm -->|No| Return403[HTTP 403<br/>Forbidden]
    Return403 --> End2([Error: No autorizado])
    
    CheckPerm -->|Sí| RouteHandler[Ejecutar route handler]
    RouteHandler --> CheckTenant{Multi-tenant<br/>check}
    
    CheckTenant -->|Empresa diferente| Return403
    CheckTenant -->|OK| ProcessRequest[Procesar request]
    
    ProcessRequest --> Response[HTTP 200<br/>Response]
    Response --> End3([Success])
    
    style End1 fill:#fff3cd
    style End2 fill:#ffe1e1
    style End3 fill:#e1f5e1
```

## Estructura de Permisos

### Formato de Permisos

```mermaid
flowchart LR
    Permiso[Permiso] --> Modulo[módulo]
    Modulo --> Separador1[:]
    Separador1 --> Accion[acción]
    
    Example1[neumaticos:crear]
    Example2[usuarios:eliminar]
    Example3[reportes:exportar]
    
    style Example1 fill:#e3f2fd
    style Example2 fill:#e3f2fd
    style Example3 fill:#e3f2fd
```

### Permisos por Rol

```mermaid
flowchart TD
    subgraph ADMINISTRADOR
        A1[✅ TODOS los permisos]
        A2[✅ usuarios:*]
        A3[✅ sistema:configurar]
        A4[✅ auditorias:ver]
    end
    
    subgraph GESTOR
        G1[✅ neumaticos:*]
        G2[✅ vehiculos:*]
        G3[✅ operaciones:*]
        G4[✅ reportes:*]
        G5[❌ usuarios:*]
        G6[❌ sistema:*]
    end
    
    subgraph OPERADOR
        O1[✅ operaciones:*]
        O2[✅ neumaticos:leer]
        O3[✅ vehiculos:leer]
        O4[❌ neumaticos:crear/actualizar]
        O5[❌ reportes:*]
        O6[❌ usuarios:*]
    end
    
    subgraph CONSULTOR
        C1[✅ *:leer]
        C2[❌ *:crear/actualizar/eliminar]
        C3[❌ operaciones:*]
        C4[❌ reportes:exportar]
    end
    
    style ADMINISTRADOR fill:#ffebee
    style GESTOR fill:#fff9c4
    style OPERADOR fill:#e8f5e9
    style CONSULTOR fill:#e3f2fd
```

## Multi-Tenancy

```mermaid
flowchart TD
    Usuario[Usuario] --> HasEmpresa[empresa_id]
    HasEmpresa --> Request[HTTP Request]
    
    Request --> Middleware[Auth Middleware]
    Middleware --> ExtractEmpresa[Extraer empresa_id<br/>del token]
    
    ExtractEmpresa --> DBQuery[(Query a DB)]
    DBQuery --> FilterByEmpresa[WHERE empresa_id = ?]
    
    FilterByEmpresa --> CheckOwnership{Recurso pertenece<br/>a empresa?}
    
    CheckOwnership -->|No| Return403[HTTP 403<br/>Forbidden]
    CheckOwnership -->|Sí| AllowAccess[Permitir acceso]
    
    AllowAccess --> Response[Return data]
    
    style Return403 fill:#ffe1e1
    style AllowAccess fill:#e1f5e1
```

## Implementación en Código

### Archivo: `src/lib/auth/permissions.ts`

```typescript
// Definición de roles
export const ROLES = {
  ADMINISTRADOR: 'ADMINISTRADOR',
  GESTOR: 'GESTOR',
  OPERADOR: 'OPERADOR',
  CONSULTOR: 'CONSULTOR'
} as const;

// Permisos por módulo
export const PERMISSIONS = {
  neumaticos: ['crear', 'leer', 'actualizar', 'eliminar'],
  vehiculos: ['crear', 'leer', 'actualizar', 'eliminar'],
  operaciones: ['montar', 'desmontar', 'inspeccionar', 'leer'],
  usuarios: ['crear', 'leer', 'actualizar', 'eliminar'],
  reportes: ['generar', 'exportar', 'leer']
};

// Mapeo de permisos por rol
export const ROLE_PERMISSIONS = {
  ADMINISTRADOR: ['*:*'], // Todos los permisos
  GESTOR: [
    'neumaticos:*',
    'vehiculos:*',
    'operaciones:*',
    'reportes:*'
  ],
  OPERADOR: [
    'neumaticos:leer',
    'vehiculos:leer',
    'operaciones:*'
  ],
  CONSULTOR: ['*:leer']
};
```

### Archivo: `src/lib/auth/authorization.ts`

```typescript
// Middleware de autorización
export function requirePermission(permission: string) {
  return async (req: Request) => {
    const session = await getSession(req);
    
    if (!session) {
      return new Response('Unauthorized', { status: 401 });
    }
    
    if (!hasPermission(session.user.permissions, permission)) {
      return new Response('Forbidden', { status: 403 });
    }
    
    return null; // Permitir acceso
  };
}

// Verificar permiso
function hasPermission(userPermissions: string[], required: string): boolean {
  // Check for wildcard permission
  if (userPermissions.includes('*:*')) return true;
  
  const [module, action] = required.split(':');
  
  // Check for module wildcard
  if (userPermissions.includes(`${module}:*`)) return true;
  
  // Check for exact permission
  return userPermissions.includes(required);
}
```

## UI Condicional por Rol

```mermaid
flowchart TD
    Component[React Component] --> GetSession[useSession]
    GetSession --> CheckPermission[Verificar permiso]
    
    CheckPermission --> HasPerm{Tiene<br/>permiso?}
    
    HasPerm -->|No| HideElement[Ocultar elemento]
    HasPerm -->|Sí| ShowElement[Mostrar elemento]
    
    ShowElement --> EnableButton[Habilitar botón/acción]
    HideElement --> DisableButton[Deshabilitar/ocultar]
    
    style ShowElement fill:#e1f5e1
    style HideElement fill:#ffe1e1
```

### Ejemplo en React

```typescript
// Componente con autorización
function CreateButton() {
  const { data: session } = useSession();
  const canCreate = hasPermission(session?.user.permissions, 'neumaticos:crear');
  
  if (!canCreate) return null;
  
  return <Button onClick={handleCreate}>Crear Neumático</Button>;
}
```

## Archivos Relacionados

### Backend
- **`src/lib/auth/permissions.ts`**: Definición de roles y permisos
- **`src/lib/auth/authorization.ts`**: Middleware de autorización
- **`src/lib/auth/config.ts`**: Configuración NextAuth con callbacks

### Frontend
- **`src/hooks/usePermission.ts`**: Hook para verificar permisos
- **`src/components/auth/ProtectedRoute.tsx`**: Componente de rutas protegidas

### Database
```prisma
model Usuario {
  id          String   @id @default(uuid())
  rol         Rol
  empresa_id  String
  // ... más campos
}

model Rol {
  id          String   @id
  nombre      String   @unique
  permisos    String[] // Array de permisos
}
```

## Logs de Auditoría

```mermaid
flowchart LR
    Action[Acción del usuario] --> Log[Registrar en audit_logs]
    Log --> Capture[Capturar datos]
    
    Capture --> User[usuario_id]
    Capture --> Action2[acción]
    Capture --> Resource[recurso]
    Capture --> Timestamp[timestamp]
    Capture --> IP[IP address]
    
    style Log fill:#e3f2fd
```

### Acciones Auditadas
- ✅ Login/Logout
- ✅ Creación de usuarios
- ✅ Cambio de permisos
- ✅ Eliminación de datos críticos
- ✅ Exportación de reportes
- ✅ Acceso a admin panel
