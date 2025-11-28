"use client"

import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Loader2 } from "lucide-react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

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
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { useToast } from "@/components/ui/use-toast"
import { neumaticosApi } from "@/lib/api/neumaticos"
import { modelosNeumaticoApi } from "@/lib/api/modelos-neumatico"
import { almacenesApi } from "@/lib/api/almacenes"

const formSchema = z.object({
    numero_serie: z.string().min(4, "El número de serie debe tener al menos 4 caracteres"),
    modelo_id: z.string().min(1, "Seleccione un modelo"),
    dot: z.string().length(4, "El DOT debe tener 4 caracteres"),
    profundidad_inicial_mm: z.string().min(1, "Ingrese profundidad"),
    costo_compra: z.string().optional(),
    ubicacion_almacen_id: z.string().optional(),
})

type FormValues = z.infer<typeof formSchema>

interface NeumaticoFormProps {
    initialData?: any
    onSuccess?: () => void
}

export function NeumaticoForm({ initialData, onSuccess }: NeumaticoFormProps) {
    const { toast } = useToast()
    const queryClient = useQueryClient()

    const { data: modelos } = useQuery({
        queryKey: ["modelos-neumatico"],
        queryFn: modelosNeumaticoApi.getAll,
    })

    const { data: almacenes } = useQuery({
        queryKey: ["almacenes"],
        queryFn: almacenesApi.getAll,
    })

    const form = useForm<FormValues>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            numero_serie: initialData?.numero_serie || "",
            modelo_id: initialData?.modelo_id || "",
            dot: initialData?.dot || "",
            profundidad_inicial_mm: initialData?.profundidad_inicial_mm?.toString() || "",
            costo_compra: initialData?.costo_compra?.toString() || "",
            ubicacion_almacen_id: initialData?.ubicacion_almacen_id || "",
        },
    })

    const mutation = useMutation({
        mutationFn: (data: any) => {
            if (initialData) {
                return neumaticosApi.update(initialData.id, data)
            }
            return neumaticosApi.create(data)
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["neumaticos"] })
            toast({
                title: initialData ? "Neumático actualizado" : "Neumático creado",
                description: initialData
                    ? "Los datos se han actualizado correctamente."
                    : "El neumático se ha registrado exitosamente.",
            })
            if (!initialData) form.reset()
            onSuccess?.()
        },
        onError: (error: Error) => {
            toast({
                variant: "destructive",
                title: "Error",
                description: error.message || "No se pudo guardar el neumático.",
            })
        },
    })

    function onSubmit(values: FormValues) {
        const payload = {
            ...values,
            profundidad_inicial_mm: parseFloat(values.profundidad_inicial_mm),
            costo_compra: values.costo_compra ? parseFloat(values.costo_compra) : undefined,
            ubicacion_almacen_id: values.ubicacion_almacen_id || undefined,
        }
        mutation.mutate(payload)
    }

    return (
        <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                    <FormField
                        control={form.control}
                        name="numero_serie"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Número de Serie *</FormLabel>
                                <FormControl>
                                    <Input placeholder="SERIE123" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="dot"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>DOT *</FormLabel>
                                <FormControl>
                                    <Input placeholder="2423" maxLength={4} {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                </div>

                <FormField
                    control={form.control}
                    name="modelo_id"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Modelo *</FormLabel>
                            <Select onValueChange={field.onChange} defaultValue={field.value}>
                                <FormControl>
                                    <SelectTrigger>
                                        <SelectValue placeholder="Seleccione modelo" />
                                    </SelectTrigger>
                                </FormControl>
                                <SelectContent>
                                    {modelos?.map((modelo) => (
                                        <SelectItem key={modelo.id} value={modelo.id}>
                                            {modelo.nombre} ({modelo.medida})
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <div className="grid grid-cols-2 gap-4">
                    <FormField
                        control={form.control}
                        name="profundidad_inicial_mm"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Profundidad (mm) *</FormLabel>
                                <FormControl>
                                    <Input type="number" step="0.1" placeholder="18.5" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="costo_compra"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Costo Compra</FormLabel>
                                <FormControl>
                                    <Input type="number" step="0.01" placeholder="0.00" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                </div>

                <FormField
                    control={form.control}
                    name="ubicacion_almacen_id"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Almacén Inicial</FormLabel>
                            <Select onValueChange={field.onChange} defaultValue={field.value}>
                                <FormControl>
                                    <SelectTrigger>
                                        <SelectValue placeholder="Seleccione almacén (Opcional)" />
                                    </SelectTrigger>
                                </FormControl>
                                <SelectContent>
                                    {almacenes?.map((almacen) => (
                                        <SelectItem key={almacen.id} value={almacen.id}>
                                            {almacen.nombre}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <div className="flex justify-end pt-4">
                    <Button type="submit" disabled={mutation.isPending}>
                        {mutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        {initialData ? 'Actualizar' : 'Guardar'} Neumático
                    </Button>
                </div>
            </form>
        </Form>
    )
}
