
"use client"

import { Button } from "@/components/ui/button"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"
import {
    Form,
    FormControl,
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { useState } from "react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useToast } from "@/components/ui/use-toast"
import { Loader2, Plus } from "lucide-react"

const tenantSchema = z.object({
    nombre: z.string().min(2, "El nombre debe tener al menos 2 caracteres"),
    ruc: z.string().length(11, "El RUC debe tener 11 dígitos").regex(/^\d+$/, "Solo números"),
    direccion: z.string().optional(),
    adminName: z.string().min(2, "El nombre del admin es requerido"),
    adminEmail: z.string().email("Email inválido"),
    adminPassword: z.string().min(6, "La contraseña debe tener al menos 6 caracteres"),
})

type TenantFormValues = z.infer<typeof tenantSchema>

export function TenantDialog() {
    const [open, setOpen] = useState(false)
    const queryClient = useQueryClient()
    const { toast } = useToast()

    const form = useForm<TenantFormValues>({
        resolver: zodResolver(tenantSchema),
        defaultValues: {
            nombre: "",
            ruc: "",
            direccion: "",
            adminName: "",
            adminEmail: "",
            adminPassword: "",
        },
    })

    const mutation = useMutation({
        mutationFn: async (values: TenantFormValues) => {
            const response = await fetch("/api/v1/admin/tenants", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(values),
            })

            if (!response.ok) {
                const error = await response.json()
                throw new Error(error.error || "Error al crear empresa")
            }
            return response.json()
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["tenants"] })
            toast({
                title: "Empresa creada",
                description: "La empresa y su administrador han sido configurados correctamente.",
            })
            setOpen(false)
            form.reset()
        },
        onError: (error) => {
            toast({
                variant: "destructive",
                title: "Error",
                description: error.message,
            })
        },
    })

    function onSubmit(values: TenantFormValues) {
        mutation.mutate(values)
    }

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button>
                    <Plus className="mr-2 h-4 w-4" />
                    Nueva Empresa
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>Registrar Nueva Empresa</DialogTitle>
                    <DialogDescription>
                        Crea un nuevo tenant y su usuario administrador inicial.
                    </DialogDescription>
                </DialogHeader>
                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                        <FormField
                            control={form.control}
                            name="nombre"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Nombre Comercial</FormLabel>
                                    <FormControl>
                                        <Input placeholder="Ej: Transportes SAC" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <FormField
                            control={form.control}
                            name="ruc"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>RUC</FormLabel>
                                    <FormControl>
                                        <Input placeholder="1045..." {...field} maxLength={11} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <FormField
                            control={form.control}
                            name="direccion"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Dirección</FormLabel>
                                    <FormControl>
                                        <Input placeholder="Av. Principal 123" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <div className="pt-4 pb-2">
                            <h4 className="text-sm font-medium text-muted-foreground">Administrador Inicial</h4>
                        </div>

                        <FormField
                            control={form.control}
                            name="adminName"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Nombre Completo</FormLabel>
                                    <FormControl>
                                        <Input placeholder="Juan Pérez" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <FormField
                            control={form.control}
                            name="adminEmail"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Email Corporativo</FormLabel>
                                    <FormControl>
                                        <Input type="email" placeholder="admin@empresa.com" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <FormField
                            control={form.control}
                            name="adminPassword"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Contraseña Administrador</FormLabel>
                                    <FormControl>
                                        <Input type="password" placeholder="******" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <DialogFooter className="pt-4">
                            <Button type="submit" disabled={mutation.isPending}>
                                {mutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                Crear Empresa
                            </Button>
                        </DialogFooter>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    )
}
