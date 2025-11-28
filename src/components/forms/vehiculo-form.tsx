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
import { useToast } from "@/hooks/use-toast"
import { vehiculosApi } from "@/lib/api/vehiculos"
import { tiposVehiculoApi } from "@/lib/api/tipos-vehiculo"

const formSchema = z.object({
    placa: z.string().min(6, "La placa debe tener al menos 6 caracteres"),
    tipo_vehiculo_id: z.string().min(1, "Seleccione un tipo de vehículo"),
    marca: z.string().optional(),
    modelo: z.string().optional(),
    anio: z.string().optional(),
    kilometraje_actual: z.string().optional(),
})

type FormValues = z.infer<typeof formSchema>

interface VehiculoFormProps {
    onSuccess?: () => void
}

export function VehiculoForm({ onSuccess }: VehiculoFormProps) {
    const { toast } = useToast()
    const queryClient = useQueryClient()

    const { data: tiposVehiculo } = useQuery({
        queryKey: ["tipos-vehiculo"],
        queryFn: tiposVehiculoApi.getAll,
    })

    const form = useForm<FormValues>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            placa: "",
            tipo_vehiculo_id: "",
            marca: "",
            modelo: "",
            anio: "",
            kilometraje_actual: "",
        },
    })

    const mutation = useMutation({
        mutationFn: vehiculosApi.create,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["vehiculos"] })
            toast({
                title: "Vehículo creado",
                description: "El vehículo se ha registrado exitosamente.",
            })
            form.reset()
            onSuccess?.()
        },
        onError: (error: Error) => {
            toast({
                variant: "destructive",
                title: "Error",
                description: error.message || "No se pudo crear el vehículo.",
            })
        },
    })

    function onSubmit(values: FormValues) {
        const payload = {
            ...values,
            anio: values.anio ? parseInt(values.anio) : undefined,
            kilometraje_actual: values.kilometraje_actual ? parseFloat(values.kilometraje_actual) : undefined,
        }
        mutation.mutate(payload)
    }

    return (
        <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                    <FormField
                        control={form.control}
                        name="placa"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Placa *</FormLabel>
                                <FormControl>
                                    <Input placeholder="ABC-123" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="tipo_vehiculo_id"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Tipo de Vehículo *</FormLabel>
                                <Select onValueChange={field.onChange} defaultValue={field.value}>
                                    <FormControl>
                                        <SelectTrigger>
                                            <SelectValue placeholder="Seleccione tipo" />
                                        </SelectTrigger>
                                    </FormControl>
                                    <SelectContent>
                                        {tiposVehiculo?.map((tipo) => (
                                            <SelectItem key={tipo.id} value={tipo.id}>
                                                {tipo.nombre}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <FormField
                        control={form.control}
                        name="marca"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Marca</FormLabel>
                                <FormControl>
                                    <Input placeholder="Toyota" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="modelo"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Modelo</FormLabel>
                                <FormControl>
                                    <Input placeholder="Hilux" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <FormField
                        control={form.control}
                        name="anio"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Año</FormLabel>
                                <FormControl>
                                    <Input type="number" placeholder="2024" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="kilometraje_actual"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Kilometraje Actual</FormLabel>
                                <FormControl>
                                    <Input type="number" step="0.1" placeholder="0.0" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                </div>

                <div className="flex justify-end pt-4">
                    <Button type="submit" disabled={mutation.isPending}>
                        {mutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        Guardar Vehículo
                    </Button>
                </div>
            </form>
        </Form>
    )
}
