/**
 * Feature flags del sistema.
 *
 * Control de funcionalidades que están implementadas pero NO deben
 * estar activas en la fase actual del sistema. Se habilitan mediante
 * variables de entorno (default: false).
 *
 * Ver docs/01_ARQUITECTURA.md §10 para deuda técnica relacionada.
 */

/**
 * RBAC dinámico basado en tablas Rol/Permiso/UsuarioRol.
 *
 * BUG DE SEGURIDAD documentado: actualmente las tablas dinámicas NO
 * afectan la autenticación real (el login usa SYSTEM_ROLES hardcoded).
 * Los endpoints /admin/roles/* y /admin/users/[id]/roles están bloqueados
 * hasta que se conecte auth.ts al rbac.service.ts en la fase multi-tenant.
 *
 * Habilitar: DYNAMIC_RBAC_ENABLED=true
 */
export const DYNAMIC_RBAC_ENABLED = process.env.DYNAMIC_RBAC_ENABLED === 'true';

/**
 * Gestión multi-tenant (Empresa cross-tenant administration).
 *
 * Solo tiene sentido cuando se active multi-tenant. En la fase actual
 * (single-tenant operativo) los endpoints /admin/tenants/* están bloqueados
 * para evitar exposición accidental.
 *
 * Habilitar: MULTI_TENANT_ENABLED=true
 */
export const MULTI_TENANT_ENABLED = process.env.MULTI_TENANT_ENABLED === 'true';

/**
 * Helper para retornar un 501 Not Implemented cuando un feature flag
 * está desactivado. Mensaje genérico para no filtrar información
 * de implementación interna.
 */
export function featureDisabledResponse(featureName: string, reason: string) {
  return new Response(
    JSON.stringify({
      success: false,
      error: `Feature '${featureName}' no disponible en esta fase del sistema`,
      reason,
      code: 'FEATURE_DISABLED',
    }),
    {
      status: 501,
      headers: { 'Content-Type': 'application/json' },
    }
  );
}
