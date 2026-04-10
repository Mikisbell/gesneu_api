// src/lib/auth/permissions.ts
export const PERMISSIONS = {
  // CATÁLOGOS
  CATALOGOS_PROVEEDORES_READ: 'catalogos:proveedores:read',
  CATALOGOS_PROVEEDORES_CREATE: 'catalogos:proveedores:create',
  CATALOGOS_PROVEEDORES_UPDATE: 'catalogos:proveedores:update',
  CATALOGOS_PROVEEDORES_DELETE: 'catalogos:proveedores:delete',

  CATALOGOS_ALMACENES_READ: 'catalogos:almacenes:read',
  CATALOGOS_ALMACENES_CREATE: 'catalogos:almacenes:create',
  CATALOGOS_ALMACENES_UPDATE: 'catalogos:almacenes:update',
  CATALOGOS_ALMACENES_DELETE: 'catalogos:almacenes:delete',

  CATALOGOS_FABRICANTES_READ: 'catalogos:fabricantes:read',
  CATALOGOS_FABRICANTES_CREATE: 'catalogos:fabricantes:create',
  CATALOGOS_FABRICANTES_UPDATE: 'catalogos:fabricantes:update',
  CATALOGOS_FABRICANTES_DELETE: 'catalogos:fabricantes:delete',

  // VEHÍCULOS
  VEHICULOS_READ: 'vehiculos:read',
  VEHICULOS_CREATE: 'vehiculos:create',
  VEHICULOS_UPDATE: 'vehiculos:update',
  VEHICULOS_DELETE: 'vehiculos:delete',
  VEHICULOS_CONFIGURAR: 'vehiculos:configurar',

  // NEUMÁTICOS
  NEUMATICOS_READ: 'neumaticos:read',
  NEUMATICOS_CREATE: 'neumaticos:create',
  NEUMATICOS_UPDATE: 'neumaticos:update',
  NEUMATICOS_DELETE: 'neumaticos:delete',

  // EVENTOS DE NEUMÁTICOS (Granular por tipo)
  NEUMATICOS_EVENTO_INSTALACION: 'neumaticos:evento:instalacion',
  NEUMATICOS_EVENTO_DESMONTAJE: 'neumaticos:evento:desmontaje',
  NEUMATICOS_EVENTO_ROTACION: 'neumaticos:evento:rotacion',
  NEUMATICOS_EVENTO_INSPECCION: 'neumaticos:evento:inspeccion',
  NEUMATICOS_EVENTO_REPARACION_ENTRADA: 'neumaticos:evento:reparacion_entrada',
  NEUMATICOS_EVENTO_REPARACION_SALIDA: 'neumaticos:evento:reparacion_salida',
  NEUMATICOS_EVENTO_REENCAUCHE: 'neumaticos:evento:reencauche',
  NEUMATICOS_EVENTO_DESECHO: 'neumaticos:evento:desecho',
  NEUMATICOS_EVENTO_AJUSTE: 'neumaticos:evento:ajuste',

  // INVENTARIO
  INVENTARIO_READ: 'inventario:read',
  INVENTARIO_MOVIMIENTOS: 'inventario:movimientos',
  INVENTARIO_AJUSTES: 'inventario:ajustes',

  // REPORTES
  REPORTES_DASHBOARD: 'reportes:dashboard',
  REPORTES_RENDIMIENTO: 'reportes:rendimiento',
  REPORTES_AUDITORIA: 'reportes:auditoria',

  // USUARIOS (shorthand for convenience)
  USUARIOS_READ: 'sistema:usuarios:read',
  USUARIOS_CREATE: 'sistema:usuarios:create',
  USUARIOS_UPDATE: 'sistema:usuarios:update',
  USUARIOS_DELETE: 'sistema:usuarios:delete',

  // SISTEMA
  SISTEMA_USUARIOS_READ: 'sistema:usuarios:read',
  SISTEMA_USUARIOS_CREATE: 'sistema:usuarios:create',
  SISTEMA_USUARIOS_UPDATE: 'sistema:usuarios:update',
  SISTEMA_USUARIOS_DELETE: 'sistema:usuarios:delete',
  SISTEMA_ROLES_MANAGE: 'sistema:roles:manage',
  SISTEMA_PERMISOS_MANAGE: 'sistema:permisos:manage',
  SISTEMA_AUDITORIA_READ: 'sistema:auditoria:read',
  SISTEMA_AUDITORIA: 'sistema:auditoria',
  SISTEMA_AJUSTES_READ: 'sistema:ajustes:read',
  SISTEMA_AJUSTES: 'sistema:ajustes'
} as const

export type Permission = typeof PERMISSIONS[keyof typeof PERMISSIONS]

// Roles predefinidos del sistema
export const SYSTEM_ROLES = {
  ADMIN: {
    nombre: 'ADMINISTRADOR',
    descripcion: 'Acceso completo al sistema',
    permisos: Object.values(PERMISSIONS) // Todos los permisos
  },

  SUPERADMIN: {
    nombre: 'SUPERADMIN',
    descripcion: 'Control Total Multi-tenant',
    permisos: Object.values(PERMISSIONS)
  },

  GESTOR: {
    nombre: 'GESTOR',
    descripcion: 'Gestión operativa completa',
    permisos: [
      // Catálogos - CRUD completo
      PERMISSIONS.CATALOGOS_PROVEEDORES_READ,
      PERMISSIONS.CATALOGOS_PROVEEDORES_CREATE,
      PERMISSIONS.CATALOGOS_PROVEEDORES_UPDATE,
      PERMISSIONS.CATALOGOS_ALMACENES_READ,
      PERMISSIONS.CATALOGOS_ALMACENES_CREATE,
      PERMISSIONS.CATALOGOS_ALMACENES_UPDATE,
      PERMISSIONS.CATALOGOS_FABRICANTES_READ,
      PERMISSIONS.CATALOGOS_FABRICANTES_CREATE,
      PERMISSIONS.CATALOGOS_FABRICANTES_UPDATE,

      // Vehículos - CRUD completo
      PERMISSIONS.VEHICULOS_READ,
      PERMISSIONS.VEHICULOS_CREATE,
      PERMISSIONS.VEHICULOS_UPDATE,
      PERMISSIONS.VEHICULOS_CONFIGURAR,

      // Neumáticos - CRUD completo
      PERMISSIONS.NEUMATICOS_READ,
      PERMISSIONS.NEUMATICOS_CREATE,
      PERMISSIONS.NEUMATICOS_UPDATE,

      // Eventos - Todos excepto ajustes
      PERMISSIONS.NEUMATICOS_EVENTO_INSTALACION,
      PERMISSIONS.NEUMATICOS_EVENTO_DESMONTAJE,
      PERMISSIONS.NEUMATICOS_EVENTO_ROTACION,
      PERMISSIONS.NEUMATICOS_EVENTO_INSPECCION,
      PERMISSIONS.NEUMATICOS_EVENTO_REPARACION_ENTRADA,
      PERMISSIONS.NEUMATICOS_EVENTO_REPARACION_SALIDA,
      PERMISSIONS.NEUMATICOS_EVENTO_REENCAUCHE,
      PERMISSIONS.NEUMATICOS_EVENTO_DESECHO,

      // Inventario - Lectura y movimientos
      PERMISSIONS.INVENTARIO_READ,
      PERMISSIONS.INVENTARIO_MOVIMIENTOS,

      // Reportes - Dashboard y rendimiento
      PERMISSIONS.REPORTES_DASHBOARD,
      PERMISSIONS.REPORTES_RENDIMIENTO
    ]
  },

  OPERADOR: {
    nombre: 'OPERADOR',
    descripcion: 'Operaciones diarias de campo',
    permisos: [
      // Catálogos - Solo lectura
      PERMISSIONS.CATALOGOS_PROVEEDORES_READ,
      PERMISSIONS.CATALOGOS_ALMACENES_READ,
      PERMISSIONS.CATALOGOS_FABRICANTES_READ,

      // Vehículos - Solo lectura
      PERMISSIONS.VEHICULOS_READ,

      // Neumáticos - Lectura y eventos operativos
      PERMISSIONS.NEUMATICOS_READ,
      PERMISSIONS.NEUMATICOS_EVENTO_INSTALACION,
      PERMISSIONS.NEUMATICOS_EVENTO_DESMONTAJE,
      PERMISSIONS.NEUMATICOS_EVENTO_ROTACION,
      PERMISSIONS.NEUMATICOS_EVENTO_INSPECCION,

      // Inventario - Solo lectura
      PERMISSIONS.INVENTARIO_READ,

      // Reportes - Solo dashboard
      PERMISSIONS.REPORTES_DASHBOARD
    ]
  },

  CONSULTOR: {
    nombre: 'CONSULTOR',
    descripcion: 'Solo lectura y reportes',
    permisos: [
      // Solo permisos de lectura
      PERMISSIONS.CATALOGOS_PROVEEDORES_READ,
      PERMISSIONS.CATALOGOS_ALMACENES_READ,
      PERMISSIONS.CATALOGOS_FABRICANTES_READ,
      PERMISSIONS.VEHICULOS_READ,
      PERMISSIONS.NEUMATICOS_READ,
      PERMISSIONS.INVENTARIO_READ,
      PERMISSIONS.REPORTES_DASHBOARD,
      PERMISSIONS.REPORTES_RENDIMIENTO
    ]
  }
} as const
