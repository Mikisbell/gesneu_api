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
    presion_recomendada_psi: z.string().optional(),
    indice_carga: z.string().optional(),
    indice_velocidad: z.string().optional(),
})

type FormValues = z.infer<typeof formSchema>

interface QuickModeloFormProps {
    onSuccess: (nuevoModelo: any) => void
}

export function QuickModeloForm({ onSuccess }: QuickModeloFormProps) {
    const [open, setOpen] = useState(false)
    const { toast } = useToast()
    const queryClient = useQueryClient()

    const { data: fabricantes } = useQuery({
        queryKey: ["fabricantes"],
        queryFn: fabricantesApi.getAll,
    })

    const form = useForm<FormValues>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            fabricante_id: "",
            nombre_modelo: "",
            medida: "",
            profundidad_original_mm: "20",
            presion_recomendada_psi: "",
            indice_carga: "",
            indice_velocidad: "",
        },
    })

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
            profundidad_original_mm: parseFloat(values.profundidad_original_mm) as any,
            presion_recomendada_psi: values.presion_recomendada_psi ? parseFloat(values.presion_recomendada_psi) as any : undefined,
            // Valores por defecto seguros para campos requeridos
            reencauches_maximos: 3,
            permite_reencauche: true
        })
    }

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button variant="outline" size="icon" type="button" title="Crear nuevo modelo">
                    <Plus className="h-4 w-4" />
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>Crear Nuevo Modelo</DialogTitle>
                    <DialogDescription>
                        Registre un modelo rápidamente para usarlo ahora.
                    </DialogDescription>
                </DialogHeader>

                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
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
                                        <FormLabel>Prof. (mm)</FormLabel>
                                        <FormControl>
                                            <Input type="number" step="0.1" {...field} />
                                        </FormControl>
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
