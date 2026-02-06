"use client"

import { useEffect, useState } from "react"

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
import { QuickModeloForm } from "./quick-modelo-form"
import { NeumaticoFormSchema, type NeumaticoFormValues } from "@/lib/validators/neumatico.shared"

// ✅ Usar schema compartido (ya no duplicar validación)
type FormValues = NeumaticoFormValues

interface NeumaticoFormProps {
    initialData?: any
    onSuccess?: () => void
}

export function NeumaticoForm({ initialData, onSuccess }: NeumaticoFormProps) {
    const { toast } = useToast()
    const queryClient = useQueryClient()

    const { data: modelosApi } = useQuery({
        queryKey: ["modelos-neumatico"],
        queryFn: modelosNeumaticoApi.getAll,
    })

    const [listaModelos, setListaModelos] = useState<any[]>([])

    useEffect(() => {
        if (modelosApi) {
            setListaModelos(modelosApi)
        }
    }, [modelosApi])

    const { data: almacenes } = useQuery({
        queryKey: ["almacenes"],
        queryFn: almacenesApi.getAll,
    })

    // ✅ Usar schema compartido con resolver
    const form = useForm<FormValues>({
        // @ts-ignore - Resolver type mismatch with z.coerce
        resolver: zodResolver(NeumaticoFormSchema),
        // ✅ Sin defaultValues aquí - solo useEffect para evitar duplicación
    }) as any

    // Auto-fill form when editing (professional UX)
    useEffect(() => {
        if (initialData) {
            form.reset({
                numero_serie: initialData.numeroSerie || "",
                modelo_id: initialData.modelo?.id || "",
                dot: initialData.dot || "",
                profundidad_inicial_mm: initialData.mediciones?.profundidadInicial?.toString() || "",
                costo_compra: initialData.compra?.costo?.toString() || "",
                ubicacion_almacen_id: initialData.ubicacion?.almacen?.id || "",
                sensor_id: initialData.deviceId || "",
            });
        }
    }, [initialData, form]);

    // ✅ 2026: Optimistic updates para mejor UX
    const mutation = useMutation({
        mutationFn: (data: any) => {
            if (initialData) {
                return neumaticosApi.update(initialData.id, data)
            }
            return neumaticosApi.create(data)
        },

        // ✅ Optimistic update: Actualizar UI inmediatamente
        onMutate: async (newNeumatico) => {
            // Cancelar queries en progreso
            await queryClient.cancelQueries({ queryKey: ["neumaticos"] })

            // Guardar estado previo para rollback
            const previousNeumaticos = queryClient.getQueryData(["neumaticos"])

            // Actualizar cache optimistically
            if (!initialData) {
                // CREATE: Agregar optimistamente
                queryClient.setQueryData(["neumaticos"], (old: any) => {
                    if (!old) return [{ ...newNeumatico, id: 'temp-' + Date.now() }]
                    return [...old, { ...newNeumatico, id: 'temp-' + Date.now() }]
                })
            } else {
                // UPDATE: Actualizar optimistamente
                queryClient.setQueryData(["neumaticos"], (old: any) => {
                    if (!old) return []
                    return old.map((item: any) =>
                        item.id === initialData.id ? { ...item, ...newNeumatico } : item
                    )
                })
            }

            return { previousNeumaticos }
        },

        onSuccess: () => {
            // Refetch para datos reales del servidor
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

        // ✅ Rollback en caso de error
        onError: (error: Error, variables, context) => {
            // Restaurar estado previo
            if (context?.previousNeumaticos) {
                queryClient.setQueryData(["neumaticos"], context.previousNeumaticos)
            }

            toast({
                variant: "destructive",
                title: "Error",
                description: error.message || "No se pudo guardar el neumático.",
            })
        },
    })

    function onSubmit(values: FormValues) {
        // ✅ z.coerce ya convirtió strings → numbers
        // Solo necesitamos agregar campos server-required
        const payload = {
            ...values,
            profundidad_actual_mm: values.profundidad_inicial_mm, // Profundidad actual = inicial
            fecha_compra: new Date().toISOString(), // Requerido por schema
        }
        mutation.mutate(payload)
    }

    return (
        <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit as any)} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                    <FormField
                        control={form.control}
                        name="numero_serie"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Número de Serie *</FormLabel>
                                <FormControl>
                                    <Input data-testid="input-numero-serie" placeholder="SERIE123" {...field} />
                                </FormControl>
                                <FormMessage data-testid="input-numero-serie-error" />
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
                                    <Input data-testid="input-dot" placeholder="2423" maxLength={4} {...field} />
                                </FormControl>
                                <FormMessage data-testid="input-dot-error" />
                            </FormItem>
                        )}
                    />
                </div>

                <FormField
                    control={form.control}
                    name="sensor_id"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>ID Sensor TPMS (Opcional)</FormLabel>
                            <FormControl>
                                <Input data-testid="input-sensor-id" placeholder="Ej: 8A2B9C" {...field} />
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <FormField
                    control={form.control}
                    name="modelo_id"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Modelo *</FormLabel>
                            <div className="flex gap-2">
                                <Select
                                    onValueChange={field.onChange}
                                    defaultValue={field.value}
                                    value={field.value} // Asegurar que el valor se actualice
                                >
                                    <FormControl>
                                        <SelectTrigger data-testid="select-modelo-trigger" className="flex-1">
                                            <SelectValue placeholder="Seleccione modelo" />
                                        </SelectTrigger>
                                    </FormControl>
                                    <SelectContent>
                                        {listaModelos.map((modelo) => (
                                            <SelectItem key={modelo.id} value={modelo.id}>
                                                {modelo.nombre_modelo} ({modelo.medida})
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                                <QuickModeloForm
                                    onSuccess={(nuevoModelo) => {
                                        setListaModelos(prev => [...prev, nuevoModelo])
                                        field.onChange(nuevoModelo.id)
                                    }}
                                />
                            </div>
                            <FormMessage data-testid="select-modelo-error" />
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
                                    <Input data-testid="input-profundidad-inicial" type="number" step="0.1" placeholder="18.5" {...field} />
                                </FormControl>
                                <FormMessage data-testid="input-profundidad-inicial-error" />
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
                                    <Input data-testid="input-costo-compra" type="number" step="0.01" placeholder="0.00" {...field} />
                                </FormControl>
                                <FormMessage data-testid="input-costo-compra-error" />
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
                                    <SelectTrigger data-testid="select-almacen-trigger">
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
                    <Button type="submit" disabled={mutation.isPending} data-testid="btn-submit-neumatico">
                        {mutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        {initialData ? 'Actualizar' : 'Guardar'} Neumático
                    </Button>
                </div>
            </form>
        </Form>
    )
}
