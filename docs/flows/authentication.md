# Authentication Flow

Este diagrama muestra el flujo completo de autenticación en GesNeu API.

## Flujo de Login

```mermaid
flowchart TD
    Start([Usuario accede a /login]) --> Form[Formulario de Login]
    Form --> Input[Usuario ingresa email/username y contraseña]
    Input --> Submit[Envía formulario]
    
    Submit --> Validate{Validación<br/>Zod Schema}
    Validate -->|Inválido| ShowError[Mostrar errores de validación]
    ShowError --> Form
    
    Validate -->|Válido| AuthCheck[NextAuth: Autorizar credenciales]
    AuthCheck --> DBQuery[(Consulta DB<br/>Usuario)]
    
    DBQuery --> UserExists{Usuario<br/>existe?}
    UserExists -->|No| Error401[Error: Usuario no encontrado]
    Error401 --> Form
    
    UserExists -->|Sí| CheckActive{Usuario<br/>activo?}
    CheckActive -->|No| ErrorInactive[Error: Usuario inactivo]
    ErrorInactive --> Form
    
    CheckActive -->|Sí| ComparePassword[Bcrypt: Comparar password]
    ComparePassword --> PasswordMatch{Password<br/>correcto?}
    
    PasswordMatch -->|No| Error403[Error: Contraseña incorrecta]
    Error403 --> Form
    
    PasswordMatch -->|Sí| GetPermissions[Obtener permisos según rol]
    GetPermissions --> CreateSession[Crear sesión JWT]
    CreateSession --> SetCookie[Guardar cookie]
    SetCookie --> Redirect[Redirigir a /dashboard]
    Redirect --> End([Dashboard])
    
    style Start fill:#e1f5e1
    style End fill:#e1f5e1
    style Error401 fill:#ffe1e1
    style Error403 fill:#ffe1e1
    style ErrorInactive fill:#ffe1e1
```

## Flujo de Logout

```mermaid
flowchart TD
    Start([Usuario en Dashboard]) --> ClickLogout[Click en botón Salir/Cerrar sesión]
    ClickLogout --> CallSignOut[NextAuth: signOut]
    CallSignOut --> ClearSession[Limpiar sesión JWT]
    ClearSession --> DeleteCookie[Eliminar cookie]
    DeleteCookie --> Redirect[Redirigir a /login]
    Redirect--> End([Login Page])
    
    style Start fill:#e1f5e1
    style End fill:#e1f5e1
```

## Flujo de Protección de Rutas

```mermaid
flowchart TD
    Start([Usuario accede a ruta protegida]) --> HasSession{Tiene<br/>sesión?}
    
    HasSession -->|No| RedirectLogin[Redirigir a /login]
    RedirectLogin --> LoginPage([Página de Login])
    
    HasSession -->|Sí| CheckPermission{Tiene<br/>permiso?}
    
    CheckPermission -->|No| Show403[Mostrar Error 403]
    Show403 --> Unauthorized([Página No Autorizada])
    
    CheckPermission -->|Sí| RenderPage[Renderizar página]
    RenderPage --> Success([Contenido])
    
    style Start fill:#e1f5e1
    style LoginPage fill:#fff3cd
    style Unauthorized fill:#ffe1e1
    style Success fill:#e1f5e1
```

## Persistencia de Sesión

```mermaid
flowchart TD
    Start([Usuario recarga página]) --> CheckCookie{Cookie<br/>existe?}
    
    CheckCookie -->|No| RedirectLogin[Redirigir a /login]
    RedirectLogin --> End1([Login Page])
    
    CheckCookie -->|Sí| ValidateJWT{JWT<br/>válido?}
    
    ValidateJWT -->|No| ClearCookie[Limpiar cookie]
    ClearCookie --> RedirectLogin
    
    ValidateJWT -->|Sí| DecodeToken[Decodificar token]
    DecodeToken --> LoadUser[Cargar datos de usuario]
    LoadUser --> RestoreSession[Restaurar sesión]
    RestoreSession --> End2([Usuario autenticado])
    
    style Start fill:#e1f5e1
    style End1 fill:#fff3cd
    style End2 fill:#e1f5e1
```

## Componentes Clave

### Backend
- **`src/lib/auth/auth.ts`**: Configuración NextAuth
- **`src/lib/auth/config.ts`**: Callbacks JWT y sesión
- **`src/lib/auth/authorization.ts`**: Middleware de autorización

### Frontend
- **`src/app/(auth)/login/page.tsx`**: Página de login
- **`src/components/auth/`**: Componentes de autenticación

### Database
- **`schema.prisma`**: Usuario table con password_hash

## Variables de Entorno Requeridas

```env
NEXTAUTH_SECRET=<secret-key>
AUTH_SECRET=<secret-key>
AUTH_TRUST_HOST=true
DATABASE_URL=<postgres-url>
```

## Seguridad

✅ **Bcrypt** para hashing de contraseñas  
✅ **JWT** para sesiones stateless  
✅ **CSRF Protection** activado  
✅ **HTTP-only cookies** para prevenir XSS  
✅ **Role-Based Access Control** (RBAC)
