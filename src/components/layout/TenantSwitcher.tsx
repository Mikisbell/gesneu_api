
"use client"

import * as React from "react"
import { Building2, PlusCircle } from "lucide-react"

import { cn } from "@/lib/utils"
import {
    Select,
    SelectContent,
    SelectGroup,
    SelectItem,
    SelectLabel,
    SelectSeparator,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { useQuery } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import { useToast } from "@/components/ui/use-toast"
import { useSession } from "next-auth/react"

type Tenant = {
    id: string
    nombre: string
}

export function TenantSwitcher({ className }: { className?: string }) {
    const router = useRouter()
    const { toast } = useToast()
    const { data: session, update } = useSession()
    const [selectedTenantId, setSelectedTenantId] = React.useState<string>("")
    const [isPending, startTransition] = React.useTransition()

    const { data: tenants = [] } = useQuery<Tenant[]>({
        queryKey: ["tenants"],
        queryFn: async () => {
            const res = await fetch("/api/v1/admin/tenants");
            if (!res.ok) return [];
            const json = await res.json();
            return json.data || [];
        },
        // Only fetch if we are superadmin? For now fetch all allowed.
        retry: false
    })

    // Set initial selection based on session
    React.useEffect(() => {
        const empresaId = (session?.user as { empresa_id?: string } | undefined)?.empresa_id;
        if (empresaId) {
            setSelectedTenantId(empresaId)
        } else if (Array.isArray(tenants) && tenants.length > 0 && !selectedTenantId) {
            // Fallback if no session ID (rare)
            setSelectedTenantId(tenants[0].id)
        }
    }, [session, tenants, selectedTenantId])

    const onTenantSelect = async (id: string) => {
        if (id === "manage") {
            router.push("/dashboard/admin/tenants")
            return
        }

        const tenant = Array.isArray(tenants) ? tenants.find(t => t.id === id) : null
        if (!tenant) return

        setSelectedTenantId(id)

        startTransition(async () => {
            try {
                // 1. Trigger Session Update
                await update({ empresa_id: id })

                toast({
                    title: "Empresa Cambiada",
                    description: `Ahora administrando: ${tenant.nombre}`,
                })

                // 2. Refresh Data
                router.refresh()

            } catch (error) {
                console.error("Failed to switch tenant:", error)
                toast({
                    title: "Error",
                    description: "No se pudo cambiar de empresa",
                    variant: "destructive"
                })
                // Revert selection
                const revertEmpresaId = (session?.user as { empresa_id?: string } | undefined)?.empresa_id;
                if (revertEmpresaId) {
                    setSelectedTenantId(revertEmpresaId)
                }
            }
        })
    }

    // Hydration fix
    const [mounted, setMounted] = React.useState(false)
    React.useEffect(() => {
        setMounted(true)
    }, [])

    if (!mounted) {
        return (
            <div className={cn("w-[200px] h-9 bg-muted rounded-md animate-pulse", className)} />
        )
    }

    return (
        <Select value={selectedTenantId} onValueChange={onTenantSelect} disabled={isPending}>
            <SelectTrigger className={cn("w-[200px] transition-all", isPending && "opacity-50", className)}>
                <Building2 className="mr-2 h-4 w-4 text-muted-foreground" />
                <SelectValue placeholder={isPending ? "Cambiando..." : "Seleccionar empresa"} />
            </SelectTrigger>
            <SelectContent>
                <SelectGroup>
                    <SelectLabel>Empresas Disponibles</SelectLabel>
                    {Array.isArray(tenants) && tenants.map((tenant) => (
                        <SelectItem key={tenant.id} value={tenant.id}>
                            {tenant.nombre}
                        </SelectItem>
                    ))}
                </SelectGroup>
                <SelectSeparator />
                <SelectGroup>
                    <SelectItem value="manage" className="text-muted-foreground">
                        <div className="flex items-center text-xs">
                            <PlusCircle className="mr-2 h-3 w-3" />
                            Gestionar Empresas
                        </div>
                    </SelectItem>
                </SelectGroup>
            </SelectContent>
        </Select>
    )
}
