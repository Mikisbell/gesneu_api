import { useSession } from "next-auth/react"
import { Permission } from "@/lib/auth/permissions"

export function usePermission() {
    const { data: session, status } = useSession()
    const permissions = session?.user?.permissions || []

    /**
     * Check if user has a specific permission
     */
    const hasPermission = (permission: Permission | Permission[]): boolean => {
        if (status !== 'authenticated') return false

        // Admin override (superuser)
        if (permissions.includes('*')) return true

        if (Array.isArray(permission)) {
            // If array, user needs ALL or ANY? Usually strict check implies ALL for "require", 
            // but for menu visibility "ANY" might be better if grouping?
            // For now, let's treat array as ANY (show if user has access to at least one)
            return permission.some(p => permissions.includes(p))
        }

        return permissions.includes(permission)
    }

    /**
     * Check if user has ALL permissions in the array
     */
    const hasAllPermissions = (requiredPermissions: Permission[]): boolean => {
        if (status !== 'authenticated') return false
        if (permissions.includes('*')) return true
        return requiredPermissions.every(p => permissions.includes(p))
    }

    return { hasPermission, hasAllPermissions, isLoading: status === 'loading' }
}
