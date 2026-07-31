"use client"

import { useEffect } from "react"
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
import { modelosNeumaticoApi } from "@/lib/api/modelos-neumatico"
import { fabricantesApi } from "@/lib/api/fabricantes"
import { getCountryIsoCode } from "@/app/(dashboard)/dashboard/fabricantes/columns"

const formSchema = z.object({
    fabricante_id: z.string().min(1, "Seleccione un fabricante"),
    nombre_modelo: z.string().min(2, "El nombre debe tener al menos 2 caracteres"),
    medida: z.string().min(3, "La medida es requerida (ej: 295/80R22.5)"),
    profundidad_original_mm: z.coerce
        .number({ error: "Ingrese un número válido" })
        .gt(0, "La profundidad debe ser mayor a 0mm"),
    profundidad_minima_retiro_mm: z.coerce
        .number()
        .min(0.5, "Profundidad mínima inválida")
        .default(3.0),
    presion_recomendada_psi: z.coerce
        .number()
        .gt(0, "La presión debe ser mayor a 0")
        .optional()
        .or(z.literal("")),
    patron_dibujo: z.string().optional(),
    tipo_servicio: z.string().optional(),
    indice_carga: z.string().optional(),
    indice_velocidad: z.string().optional(),
    reencauches_maximos: z.coerce.number().min(0).optional().default(3),
    permite_reencauche: z.boolean().optional().default(true),
})

type FormValues = z.infer<typeof formSchema>

interface ModeloNeumaticoFormProps {
    initialData?: any
    onSuccess?: () => void
}

export function ModeloNeumaticoForm({ initialData, onSuccess }: ModeloNeumaticoFormProps) {
    const { toast } = useToast()
    const queryClient = useQueryClient()

    const { data: fabricantes } = useQuery({
        queryKey: ["fabricantes"],
        queryFn: fabricantesApi.getAll,
    })

    const form = useForm<any>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            fabricante_id: "",
            nombre_modelo: "",
            medida: "",
            profundidad_original_mm: 20,
            profundidad_minima_retiro_mm: 3.0,
            presion_recomendada_psi: undefined as any,
            patron_dibujo: "TODA POSICION",
            tipo_servicio: "REGIONAL",
            indice_carga: "",
            indice_velocidad: "",
            reencauches_maximos: 3,
            permite_reencauche: true,
        },
    })

    useEffect(() => {
        if (initialData) {
            form.reset({
                fabricante_id: initialData.fabricante_id || initialData.fabricante?.id || "",
                nombre_modelo: initialData.nombre_modelo || initialData.nombre || "",
                medida: initialData.medida || "",
                profundidad_original_mm: Number(initialData.profundidad_original_mm || initialData.profundidadOriginal) || 16,
                profundidad_minima_retiro_mm: Number(initialData.profundidad_minima_retiro_mm || initialData.profundidadMinimaRetiro) || 3.0,
                presion_recomendada_psi: (initialData.presion_recomendada_psi || initialData.presionRecomendada) ? Number(initialData.presion_recomendada_psi || initialData.presionRecomendada) : "",
                patron_dibujo: initialData.patron_dibujo || initialData.patronDibujo || "TODA POSICION",
                tipo_servicio: initialData.tipo_servicio || initialData.tipoServicio || "REGIONAL",
                indice_carga: initialData.indice_carga || initialData.especificaciones?.indiceCarga || "",
                indice_velocidad: initialData.indice_velocidad || initialData.especificaciones?.indiceVelocidad || "",
                reencauches_maximos: initialData.reencauches_maximos ?? initialData.reencauche?.maximos ?? 3,
                permite_reencauche: initialData.permite_reencauche ?? initialData.reencauche?.permitido ?? true,
            })
        }
    }, [initialData, form])

    const mutation = useMutation({
        mutationFn: (data: any) => {
            const payload = {
                ...data,
                nombre: data.nombre_modelo,
                presion_recomendada_psi: data.presion_recomendada_psi || undefined,
                indice_carga: data.indice_carga || undefined,
                indice_velocidad: data.indice_velocidad || undefined,
            }
            if (initialData) {
                return modelosNeumaticoApi.update(initialData.id, payload)
            }
            return modelosNeumaticoApi.create(payload)
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["modelos-neumatico"] })
            toast({
                title: initialData ? "Modelo actualizado" : "Modelo creado",
                description: initialData
                    ? "Los cambios en el modelo de neumático fueron guardados."
                    : "El nuevo modelo de neumático ha sido registrado.",
            })
            form.reset()
            onSuccess?.()
        },
        onError: (error: Error) => {
            toast({
                variant: "destructive",
                title: "Error al guardar modelo",
                description: error.message || "Ocurrió un error al procesar el modelo.",
            })
        },
    })

    function onSubmit(values: any) {
        mutation.mutate(values)
    }

    return (
        <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit as any)} className="space-y-4">
                <FormField
                    control={form.control}
                    name="fabricante_id"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Fabricante *</FormLabel>
                            <Select
                                onValueChange={field.onChange}
                                defaultValue={field.value}
                                value={field.value}
                            >
                                <FormControl>
                                    <SelectTrigger>
                                        <SelectValue placeholder="Seleccione fabricante" />
                                    </SelectTrigger>
                                </FormControl>
                                <SelectContent>
                                    {fabricantes?.map((fab: any) => {
                                        const pais = fab.paisOrigen || fab.pais_origen
                                        const code = getCountryIsoCode(pais)

                                        return (
                                            <SelectItem key={fab.id} value={fab.id}>
                                                <div className="flex items-center gap-2">
                                                    {code ? (
                                                        <img
                                                            src={`https://flagcdn.com/w40/${code}.png`}
                                                            alt={pais || 'País'}
                                                            className="h-3 w-4.5 object-cover rounded-[2px] border border-slate-200"
                                                        />
                                                    ) : (
                                                        <span>🌐</span>
                                                    )}
                                                    <span>{fab.nombre}</span>
                                                    {fab.codigo_abreviado || fab.codigoAbreviado ? (
                                                        <span className="text-xs text-muted-foreground font-mono">
                                                            ({fab.codigo_abreviado || fab.codigoAbreviado})
                                                        </span>
                                                    ) : null}
                                                </div>
                                            </SelectItem>
                                        )
                                    })}
                                </SelectContent>
                            </Select>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <FormField
                    control={form.control}
                    name="nombre_modelo"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Nombre del Modelo *</FormLabel>
                            <FormControl>
                                <Input placeholder="Ej: X Multi Z" {...field} />
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <div className="grid grid-cols-3 gap-4">
                    <FormField
                        control={form.control}
                        name="medida"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Medida *</FormLabel>
                                <FormControl>
                                    <Input placeholder="Ej: 295/80R22.5" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="profundidad_original_mm"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Prof. Original (mm) *</FormLabel>
                                <FormControl>
                                    <Input type="number" step="0.1" placeholder="20.0" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="profundidad_minima_retiro_mm"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Prof. Mín. Retiro (mm)</FormLabel>
                                <FormControl>
                                    <Input type="number" step="0.1" placeholder="3.0" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <FormField
                        control={form.control}
                        name="patron_dibujo"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Patrón de Dibujo / Eje</FormLabel>
                                <Select onValueChange={field.onChange} value={field.value}>
                                    <FormControl>
                                        <SelectTrigger>
                                            <SelectValue placeholder="Seleccione patrón" />
                                        </SelectTrigger>
                                    </FormControl>
                                    <SelectContent>
                                        <SelectItem value="DIRECCIONAL">🧭 DIRECCIONAL (Steer)</SelectItem>
                                        <SelectItem value="TRACCION">🚜 TRACCIÓN (Drive)</SelectItem>
                                        <SelectItem value="REMOLQUE">🚛 REMOLQUE (Trailer)</SelectItem>
                                        <SelectItem value="TODA POSICION">🔄 TODA POSICIÓN (All-Position)</SelectItem>
                                    </SelectContent>
                                </Select>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="tipo_servicio"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Tipo de Servicio / Aplicación</FormLabel>
                                <Select onValueChange={field.onChange} value={field.value}>
                                    <FormControl>
                                        <SelectTrigger>
                                            <SelectValue placeholder="Seleccione servicio" />
                                        </SelectTrigger>
                                    </FormControl>
                                    <SelectContent>
                                        <SelectItem value="REGIONAL">🛣️ REGIONAL</SelectItem>
                                        <SelectItem value="LARGA DISTANCIA">🚚 LARGA DISTANCIA</SelectItem>
                                        <SelectItem value="MIXTO/OFF-ROAD">🪨 MIXTO / OFF-ROAD / MINERÍA</SelectItem>
                                        <SelectItem value="URBANO">🏙️ URBANO</SelectItem>
                                    </SelectContent>
                                </Select>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                </div>

                <div className="grid grid-cols-3 gap-4">
                    <FormField
                        control={form.control}
                        name="presion_recomendada_psi"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>PSI Recomendado</FormLabel>
                                <FormControl>
                                    <Input type="number" step="0.1" placeholder="110" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="indice_carga"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Índice Carga</FormLabel>
                                <FormControl>
                                    <Input placeholder="152/148" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="indice_velocidad"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Índice Vel.</FormLabel>
                                <FormControl>
                                    <Input placeholder="M" maxLength={2} {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <FormField
                        control={form.control}
                        name="reencauches_maximos"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Máx. Reencauches</FormLabel>
                                <FormControl>
                                    <Input type="number" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="permite_reencauche"
                        render={({ field }) => (
                            <FormItem className="flex flex-row items-center space-x-3 space-y-0 rounded-md border p-3 mt-6">
                                <FormControl>
                                    <input
                                        type="checkbox"
                                        checked={field.value}
                                        onChange={field.onChange}
                                        className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                                    />
                                </FormControl>
                                <FormLabel className="font-medium cursor-pointer text-sm">
                                    Permite Reencauche
                                </FormLabel>
                            </FormItem>
                        )}
                    />
                </div>

                <div className="flex justify-end pt-4">
                    <Button type="submit" disabled={mutation.isPending}>
                        {mutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        {initialData ? "Guardar Cambios" : "Crear Modelo"}
                    </Button>
                </div>
            </form>
        </Form>
    )
}
