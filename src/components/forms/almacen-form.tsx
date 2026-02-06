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
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { useToast } from "@/components/ui/use-toast"
import { almacenesApi } from "@/lib/api/almacenes"

const formSchema = z.object({
    codigo: z.string().min(2, "El código debe tener al menos 2 caracteres"),
    nombre: z.string().min(2, "El nombre debe tener al menos 2 caracteres"),
    tipo: z.string().min(1, "Seleccione un tipo"),
    direccion: z.string().optional(),
})

type FormValues = z.infer<typeof formSchema>

interface AlmacenFormProps {
    initialData?: any
    onSuccess?: () => void
}

export function AlmacenForm({ initialData, onSuccess }: AlmacenFormProps) {
    const { toast } = useToast()
    const queryClient = useQueryClient()

    const form = useForm<FormValues>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            codigo: initialData?.codigo || "",
            nombre: initialData?.nombre || "",
            tipo: initialData?.tipo || "PRINCIPAL",
            direccion: initialData?.direccion || initialData?.ubicacion || "",
        },
    })

    const mutation = useMutation({
        mutationFn: (data: any) => {
            if (initialData) {
                return almacenesApi.update(initialData.id, data)
            }
            return almacenesApi.create(data)
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["almacenes"] })
            toast({
                title: initialData ? "Almacén actualizado" : "Almacén creado",
                description: initialData
                    ? "Los datos se han actualizado correctamente."
                    : "El almacén se ha registrado exitosamente.",
            })
            if (!initialData) form.reset()
            onSuccess?.()
        },
        onError: (error: Error) => {
            toast({
                variant: "destructive",
                title: "Error",
                description: error.message || "No se pudo guardar el almacén.",
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

                <div className="grid grid-cols-2 gap-4">
                    <FormField
                        control={form.control}
                        name="tipo"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Tipo *</FormLabel>
                                <Select onValueChange={field.onChange} defaultValue={field.value}>
                                    <FormControl>
                                        <SelectTrigger>
                                            <SelectValue placeholder="Seleccione tipo" />
                                        </SelectTrigger>
                                    </FormControl>
                                    <SelectContent>
                                        <SelectItem value="PRINCIPAL">Principal</SelectItem>
                                        <SelectItem value="TRANSITORIO">Transitorio</SelectItem>
                                        <SelectItem value="SCRAP">Scrap (Desecho)</SelectItem>
                                        <SelectItem value="MOVIL">Móvil (Auxilio)</SelectItem>
                                    </SelectContent>
                                </Select>
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
                                    <Input placeholder="Nave 3, Sector B" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                </div>

                <div className="flex justify-end pt-4">
                    <Button type="submit" disabled={mutation.isPending}>
                        {mutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        {initialData ? 'Actualizar' : 'Guardar'} Almacén
                    </Button>
                </div>
            </form>
        </Form>
    )
}
