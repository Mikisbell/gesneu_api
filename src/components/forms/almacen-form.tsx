"use client"

import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Loader2 } from "lucide-react"
import { useMutation, useQueryClient } from "@tanstack/react-query"

import { Button } from "@/components/ui/button"
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { useToast } from "@/hooks/use-toast"
import { almacenesApi } from "@/lib/api/almacenes"

const formSchema = z.object({
    codigo: z.string().min(2, "El código debe tener al menos 2 caracteres"),
    nombre: z.string().min(2, "El nombre debe tener al menos 2 caracteres"),
    ubicacion: z.string().optional(),
    descripcion: z.string().optional(),
})

type FormValues = z.infer<typeof formSchema>

interface AlmacenFormProps {
    onSuccess?: () => void
}

export function AlmacenForm({ onSuccess }: AlmacenFormProps) {
    const { toast } = useToast()
    const queryClient = useQueryClient()

    const form = useForm<FormValues>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            codigo: "",
            nombre: "",
            ubicacion: "",
            descripcion: "",
        },
    })

    const mutation = useMutation({
        mutationFn: almacenesApi.create,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["almacenes"] })
            toast({
                title: "Almacén creado",
                description: "El almacén se ha registrado exitosamente.",
            })
            form.reset()
            onSuccess?.()
        },
        onError: (error: Error) => {
            toast({
                variant: "destructive",
                title: "Error",
                description: error.message || "No se pudo crear el almacén.",
            })
        },
    })

    function onSubmit(values: FormValues) {
        mutation.mutate(values)
    }

    return (
        <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                    <FormField
                        control={form.control}
                        name="codigo"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Código *</FormLabel>
                                <FormControl>
                                    <Input placeholder="ALM-01" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="nombre"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Nombre *</FormLabel>
                                <FormControl>
                                    <Input placeholder="Almacén Central" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                </div>

                <FormField
                    control={form.control}
                    name="ubicacion"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Ubicación</FormLabel>
                            <FormControl>
                                <Input placeholder="Nave 3, Sector B" {...field} />
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <FormField
                    control={form.control}
                    name="descripcion"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Descripción</FormLabel>
                            <FormControl>
                                <Input placeholder="Almacén principal de neumáticos nuevos" {...field} />
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <div className="flex justify-end pt-4">
                    <Button type="submit" disabled={mutation.isPending}>
                        {mutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        Guardar Almacén
                    </Button>
                </div>
            </form>
        </Form>
    )
}
