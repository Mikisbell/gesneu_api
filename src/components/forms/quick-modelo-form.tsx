"use client"

import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Loader2, Plus } from "lucide-react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"

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
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"
import { useToast } from "@/components/ui/use-toast"
import { modelosNeumaticoApi } from "@/lib/api/modelos-neumatico"
import { fabricantesApi } from "@/lib/api/fabricantes"

const formSchema = z.object({
    fabricante_id: z.string().min(1, "Seleccione un fabricante"),
    nombre_modelo: z.string().min(2, "El nombre debe tener al menos 2 caracteres"),
    medida: z.string().min(3, "La medida es requerida (ej: 295/80R22.5)"),
    profundidad_original_mm: z.string().min(1, "Ingrese la profundidad original"),
    profundidad_minima_retiro_mm: z.string().optional().default("3.0"),
    patron_dibujo: z.string().optional().default("TODA POSICION"),
    tipo_servicio: z.string().optional().default("REGIONAL"),
    presion_recomendada_psi: z.string().optional(),
    indice_carga: z.string().optional(),
    indice_velocidad: z.string().optional(),
})

type FormValues = z.infer<typeof formSchema>

interface QuickModeloFormProps {
    defaultFabricanteId?: string
    onSuccess: (nuevoModelo: any) => void
    trigger?: React.ReactNode
}

export function QuickModeloForm({ defaultFabricanteId, onSuccess, trigger }: QuickModeloFormProps) {
    const [open, setOpen] = useState(false)
    const { toast } = useToast()
    const queryClient = useQueryClient()

    const { data: fabricantes } = useQuery({
        queryKey: ["fabricantes"],
        queryFn: fabricantesApi.getAll,
    })

    const initialFabId = defaultFabricanteId && defaultFabricanteId !== "TODOS" ? defaultFabricanteId : ""

    const form = useForm<any>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            fabricante_id: initialFabId,
            nombre_modelo: "",
            medida: "",
            profundidad_original_mm: "18.5",
            profundidad_minima_retiro_mm: "3.0",
            patron_dibujo: "TODA POSICION",
            tipo_servicio: "REGIONAL",
            presion_recomendada_psi: "110",
            indice_carga: "152/148",
            indice_velocidad: "M",
        },
    })

    const handleOpenChange = (isOpen: boolean) => {
        setOpen(isOpen)
        if (isOpen && initialFabId) {
            form.setValue("fabricante_id", initialFabId)
        }
    }

    const mutation = useMutation({
        mutationFn: modelosNeumaticoApi.create,
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ["modelos-neumatico"] })
            toast({
                title: "Modelo creado",
                description: "El modelo se ha creado exitosamente.",
            })
            form.reset()
            setOpen(false)
            onSuccess(data)
        },
        onError: (error: Error) => {
            toast({
                variant: "destructive",
                title: "Error",
                description: error.message || "No se pudo crear el modelo.",
            })
        },
    })

    function onSubmit(values: FormValues) {
        mutation.mutate({
            ...values,
            nombre_modelo: values.nombre_modelo,
            profundidad_original_mm: parseFloat(values.profundidad_original_mm) as any,
            profundidad_minima_retiro_mm: parseFloat(values.profundidad_minima_retiro_mm || "3.0") as any,
            presion_recomendada_psi: values.presion_recomendada_psi ? parseFloat(values.presion_recomendada_psi) as any : undefined,
            reencauches_maximos: 3,
            permite_reencauche: true
        } as any)
    }

    return (
        <Dialog open={open} onOpenChange={handleOpenChange}>
            <DialogTrigger asChild>
                {trigger ? (
                    trigger
                ) : (
                    <Button variant="outline" size="icon" type="button" title="Crear nuevo modelo">
                        <Plus className="h-4 w-4" />
                    </Button>
                )}
            </DialogTrigger>
            <DialogContent className="sm:max-w-[500px]">
                <DialogHeader>
                    <DialogTitle>Crear Nuevo Modelo</DialogTitle>
                    <DialogDescription>
                        Registre las especificaciones técnicas del modelo rápido.
                    </DialogDescription>
                </DialogHeader>

                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit as any)} className="space-y-4">
                        <FormField
                            control={form.control}
                            name="fabricante_id"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Fabricante</FormLabel>
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
                                            {fabricantes?.map((fab) => (
                                                <SelectItem key={fab.id} value={fab.id}>
                                                    {fab.nombre}
                                                </SelectItem>
                                            ))}
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
                                    <FormLabel>Nombre Modelo</FormLabel>
                                    <FormControl>
                                        <Input placeholder="Ej: X Multi Z" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <div className="grid grid-cols-2 gap-4">
                            <FormField
                                control={form.control}
                                name="medida"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Medida</FormLabel>
                                        <FormControl>
                                            <Input placeholder="295/80R22.5" {...field} />
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
                                        <FormLabel>Prof. Orig. (mm)</FormLabel>
                                        <FormControl>
                                            <Input type="number" step="0.1" {...field} />
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
                                        <FormLabel>Patrón / Eje</FormLabel>
                                        <Select onValueChange={field.onChange} value={field.value}>
                                            <FormControl>
                                                <SelectTrigger>
                                                    <SelectValue placeholder="Seleccione patrón" />
                                                </SelectTrigger>
                                            </FormControl>
                                            <SelectContent>
                                                <SelectItem value="DIRECCIONAL">🧭 DIRECCIONAL</SelectItem>
                                                <SelectItem value="TRACCION">🚜 TRACCIÓN</SelectItem>
                                                <SelectItem value="REMOLQUE">🚛 REMOLQUE</SelectItem>
                                                <SelectItem value="TODA POSICION">🔄 TODA POSICIÓN</SelectItem>
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
                                        <FormLabel>Tipo Servicio</FormLabel>
                                        <Select onValueChange={field.onChange} value={field.value}>
                                            <FormControl>
                                                <SelectTrigger>
                                                    <SelectValue placeholder="Seleccione servicio" />
                                                </SelectTrigger>
                                            </FormControl>
                                            <SelectContent>
                                                <SelectItem value="REGIONAL">REGIONAL</SelectItem>
                                                <SelectItem value="LARGA DISTANCIA">LARGA DISTANCIA</SelectItem>
                                                <SelectItem value="MIXTO/OFF-ROAD">MIXTO/OFF-ROAD</SelectItem>
                                                <SelectItem value="URBANO">URBANO</SelectItem>
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
                                        <FormLabel>PSI Rec.</FormLabel>
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
                                        <FormLabel>Ind. Carga</FormLabel>
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
                                        <FormLabel>Ind. Vel.</FormLabel>
                                        <FormControl>
                                            <Input placeholder="M" maxLength={2} {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </div>

                        <div className="flex justify-end pt-4">
                            <Button type="submit" disabled={mutation.isPending}>
                                {mutation.isPending && (
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                )}
                                Crear Modelo
                            </Button>
                        </div>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    )
}
