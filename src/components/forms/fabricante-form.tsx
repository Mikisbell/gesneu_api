"use client"

import { useEffect } from "react"
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
import { useToast } from "@/components/ui/use-toast"
import { fabricantesApi } from "@/lib/api/fabricantes"

const formSchema = z.object({
    nombre: z.string().min(2, "El nombre debe tener al menos 2 caracteres"),
    codigoAbreviado: z.string().max(10, "Máximo 10 caracteres").optional().or(z.literal("")),
    paisOrigen: z.string().max(50, "Máximo 50 caracteres").optional().or(z.literal("")),
    sitioWeb: z.string().url("URL inválida (ej: https://michelin.com)").optional().or(z.literal("")),
})

type FormValues = z.infer<typeof formSchema>

interface FabricanteFormProps {
    initialData?: any
    onSuccess?: () => void
}

export function FabricanteForm({ initialData, onSuccess }: FabricanteFormProps) {
    const { toast } = useToast()
    const queryClient = useQueryClient()

    const form = useForm<FormValues>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            nombre: "",
            codigoAbreviado: "",
            paisOrigen: "",
            sitioWeb: "",
        },
    })

    useEffect(() => {
        if (initialData) {
            form.reset({
                nombre: initialData.nombre || "",
                codigoAbreviado: initialData.codigoAbreviado || initialData.codigo_abreviado || "",
                paisOrigen: initialData.paisOrigen || initialData.pais_origen || "",
                sitioWeb: initialData.sitioWeb || initialData.sitio_web || "",
            })
        }
    }, [initialData, form])

    const mutation = useMutation({
        mutationFn: (data: any) => {
            if (initialData) {
                return fabricantesApi.update(initialData.id, data)
            }
            return fabricantesApi.create(data)
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["fabricantes"] })
            toast({
                title: initialData ? "Fabricante actualizado" : "Fabricante creado",
                description: initialData
                    ? "Los datos del fabricante se han actualizado."
                    : "El nuevo fabricante se ha registrado correctamente.",
            })
            form.reset()
            onSuccess?.()
        },
        onError: (error: Error) => {
            toast({
                variant: "destructive",
                title: "Error al guardar fabricante",
                description: error.message || "Ocurrió un problema al guardar el fabricante.",
            })
        },
    })

    function onSubmit(values: FormValues) {
        mutation.mutate({
            nombre: values.nombre,
            codigoAbreviado: values.codigoAbreviado || undefined,
            paisOrigen: values.paisOrigen || undefined,
            sitioWeb: values.sitioWeb || undefined,
        })
    }

    return (
        <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                <FormField
                    control={form.control}
                    name="nombre"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Nombre del Fabricante *</FormLabel>
                            <FormControl>
                                <Input placeholder="Ej: Michelin, Bridgestone, Goodyear" {...field} />
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <div className="grid grid-cols-2 gap-4">
                    <FormField
                        control={form.control}
                        name="codigoAbreviado"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Código / Sigla</FormLabel>
                                <FormControl>
                                    <Input placeholder="Ej: MCH, BS, GY" maxLength={10} {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="paisOrigen"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>País de Origen</FormLabel>
                                <FormControl>
                                    <Input placeholder="Ej: Francia, Japón, EE.UU." {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                </div>

                <FormField
                    control={form.control}
                    name="sitioWeb"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Sitio Web (Opcional)</FormLabel>
                            <FormControl>
                                <Input placeholder="https://www.michelin.com" {...field} />
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <div className="flex justify-end pt-4">
                    <Button type="submit" disabled={mutation.isPending}>
                        {mutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        {initialData ? "Guardar Cambios" : "Crear Fabricante"}
                    </Button>
                </div>
            </form>
        </Form>
    )
}
