"use client"

import { useEffect, useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { Loader2, Pencil, Disc, Plus } from "lucide-react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
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
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog"
import { useToast } from "@/components/ui/use-toast"
import { neumaticosApi } from "@/lib/api/neumaticos"
import { modelosNeumaticoApi } from "@/lib/api/modelos-neumatico"
import { fabricantesApi } from "@/lib/api/fabricantes"
import { almacenesApi } from "@/lib/api/almacenes"
import { proveedoresApi } from "@/lib/api/proveedores"
import { getCountryIsoCode } from "@/app/(dashboard)/dashboard/fabricantes/columns"
import { QuickModeloForm } from "./quick-modelo-form"
import { ModeloNeumaticoForm } from "./modelo-neumatico-form"
import { NeumaticoFormSchema, type NeumaticoFormValues } from "@/lib/validators/neumatico.shared"

type FormValues = NeumaticoFormValues

interface NeumaticoFormProps {
    initialData?: any
    onSuccess?: () => void
}

export function NeumaticoForm({ initialData, onSuccess }: NeumaticoFormProps) {
    const { toast } = useToast()
    const queryClient = useQueryClient()
    const [editingModeloOpen, setEditingModeloOpen] = useState(false)

    const { data: fabricantes } = useQuery({
        queryKey: ["fabricantes"],
        queryFn: fabricantesApi.getAll,
    })
    const [selectedFabricanteId, setSelectedFabricanteId] = useState<string>("")

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

    const { data: proveedores } = useQuery({
        queryKey: ["proveedores"],
        queryFn: proveedoresApi.getAll,
    })

    const form = useForm<FormValues>({
        // @ts-ignore - Resolver type mismatch with z.coerce
        resolver: zodResolver(NeumaticoFormSchema),
        defaultValues: {
            numero_serie: "",
            dot: "",
            sensor_id: "",
            modelo_id: "",
            profundidad_inicial_mm: 18.5,
            costo_compra: "" as any,
            fecha_compra: new Date().toISOString().split("T")[0],
            moneda_compra: "PEN",
            proveedor_compra_id: "",
            es_reencauchado: false,
            ubicacion_almacen_id: "",
        }
    }) as any

    useEffect(() => {
        if (initialData) {
            form.reset({
                numero_serie: initialData.numeroSerie || initialData.numero_serie || "",
                modelo_id: initialData.modelo?.id || initialData.modelo_id || "",
                dot: initialData.dot || "",
                profundidad_inicial_mm: initialData.mediciones?.profundidadInicial ?? initialData.profundidad_inicial_mm ?? 18.5,
                costo_compra: (initialData.compra?.costo ?? initialData.costo_compra ?? "") as any,
                fecha_compra: initialData.compra?.fecha
                    ? new Date(initialData.compra.fecha).toISOString().split("T")[0]
                    : initialData.fecha_compra
                    ? new Date(initialData.fecha_compra).toISOString().split("T")[0]
                    : new Date().toISOString().split("T")[0],
                moneda_compra: initialData.compra?.moneda || initialData.moneda_compra || "PEN",
                proveedor_compra_id: initialData.compra?.proveedorId || initialData.proveedor_compra_id || "",
                es_reencauchado: initialData.condicion?.esReencauchado ?? initialData.es_reencauchado ?? false,
                ubicacion_almacen_id: initialData.ubicacion?.almacen?.id || initialData.ubicacion_almacen_id || "",
                sensor_id: initialData.deviceId || initialData.sensor_id || "",
            });
        }
    }, [initialData, form]);

    const mutation = useMutation({
        mutationFn: (data: any) => {
            if (initialData) {
                return neumaticosApi.update(initialData.id, data)
            }
            return neumaticosApi.create(data)
        },

        onMutate: async (newNeumatico) => {
            await queryClient.cancelQueries({ queryKey: ["neumaticos"] })
            const previousNeumaticos = queryClient.getQueryData(["neumaticos"])

            if (!initialData) {
                queryClient.setQueryData(["neumaticos"], (old: any) => {
                    if (!old) return [{ ...newNeumatico, id: 'temp-' + Date.now() }]
                    return [...old, { ...newNeumatico, id: 'temp-' + Date.now() }]
                })
            } else {
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
            queryClient.invalidateQueries({ queryKey: ["neumaticos"] })
            toast({
                title: initialData ? "Neumático actualizado" : "Neumático creado",
                description: initialData
                    ? "Los datos se han actualizado correctamente."
                    : "El neumático se ha registrado exitosamente en el inventario.",
            })
            if (!initialData) form.reset()
            onSuccess?.()
        },

        onError: (error: Error, variables, context) => {
            if (context?.previousNeumaticos) {
                queryClient.setQueryData(["neumaticos"], context.previousNeumaticos)
            }

            toast({
                variant: "destructive",
                title: "Error al guardar neumático",
                description: error.message || "No se pudo guardar la información en el servidor.",
            })
        },
    })

    function onSubmit(values: FormValues) {
        const payload = {
            ...values,
            profundidad_actual_mm: values.profundidad_inicial_mm,
            fecha_compra: new Date(values.fecha_compra).toISOString(),
            proveedor_compra_id: values.proveedor_compra_id || undefined,
            ubicacion_almacen_id: values.ubicacion_almacen_id || undefined,
            sensor_id: values.sensor_id || undefined,
            dot: values.dot || undefined,
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

                <div className="space-y-4 rounded-lg border p-4 bg-slate-50/50 dark:bg-slate-900/50">
                    <div className="space-y-2">
                        <Label>Fabricante (Filtrar catálogo)</Label>
                        <Select
                            value={selectedFabricanteId}
                            onValueChange={(val) => {
                                setSelectedFabricanteId(val)
                                // Reset selected model when manufacturer changes
                                form.setValue("modelo_id", "")
                            }}
                        >
                            <SelectTrigger>
                                <SelectValue placeholder="Todos los fabricantes (o seleccione uno)" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="TODOS">🌐 Todos los fabricantes</SelectItem>
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
                    </div>

                    <FormField
                        control={form.control}
                        name="modelo_id"
                        render={({ field }) => {
                            const modelosFiltrados = (selectedFabricanteId && selectedFabricanteId !== "TODOS")
                                ? listaModelos.filter(m => (m.fabricante?.id || m.fabricante_id) === selectedFabricanteId)
                                : listaModelos

                            const selectedModelo = listaModelos.find(m => m.id === field.value)
                            const selectedFabObject = fabricantes?.find((f: any) => f.id === selectedFabricanteId)

                            return (
                                <FormItem>
                                    <FormLabel>Modelo *</FormLabel>
                                    <div className="flex gap-2">
                                        <Select
                                            onValueChange={(val) => {
                                                field.onChange(val)
                                                const mod = listaModelos.find(m => m.id === val)
                                                if (mod) {
                                                    // Auto fill depth from model spec
                                                    const origDepth = mod.profundidadOriginal ?? mod.profundidad_original_mm
                                                    if (origDepth) {
                                                        form.setValue("profundidad_inicial_mm", Number(origDepth))
                                                    }
                                                }
                                            }}
                                            defaultValue={field.value}
                                            value={field.value}
                                        >
                                            <FormControl>
                                                <SelectTrigger data-testid="select-modelo-trigger" className="flex-1">
                                                    <SelectValue placeholder={modelosFiltrados.length > 0 ? "Seleccione modelo de neumático" : "No hay modelos para esta marca"} />
                                                </SelectTrigger>
                                            </FormControl>
                                            <SelectContent>
                                                {modelosFiltrados.map((modelo) => {
                                                    const fabNombre = modelo.fabricante?.nombre || modelo.fabricante_nombre || ""
                                                    const modNombre = modelo.nombre || modelo.nombre_modelo || ""
                                                    return (
                                                        <SelectItem key={modelo.id} value={modelo.id}>
                                                            {fabNombre ? `${fabNombre} - ` : ""}{modNombre} ({modelo.medida})
                                                        </SelectItem>
                                                    )
                                                })}
                                            </SelectContent>
                                        </Select>
                                        <QuickModeloForm
                                            defaultFabricanteId={selectedFabricanteId}
                                            onSuccess={(nuevoModelo) => {
                                                setListaModelos(prev => [...prev, nuevoModelo])
                                                field.onChange(nuevoModelo.id)
                                            }}
                                        />
                                        {selectedModelo && (
                                            <Dialog open={editingModeloOpen} onOpenChange={setEditingModeloOpen}>
                                                <Button
                                                    variant="outline"
                                                    size="icon"
                                                    type="button"
                                                    title="Editar modelo seleccionado"
                                                    onClick={() => setEditingModeloOpen(true)}
                                                >
                                                    <Pencil className="h-4 w-4" />
                                                </Button>
                                                <DialogContent className="sm:max-w-[550px]">
                                                    <DialogHeader>
                                                        <DialogTitle>Editar Modelo de Neumático</DialogTitle>
                                                    </DialogHeader>
                                                    <ModeloNeumaticoForm
                                                        initialData={selectedModelo}
                                                        onSuccess={() => {
                                                            setEditingModeloOpen(false)
                                                            queryClient.invalidateQueries({ queryKey: ["modelos-neumatico"] })
                                                        }}
                                                    />
                                                </DialogContent>
                                            </Dialog>
                                        )}
                                    </div>

                                    {/* Empty state banner when selected manufacturer has no models */}
                                    {modelosFiltrados.length === 0 && selectedFabricanteId && selectedFabricanteId !== "TODOS" && (
                                        <div className="rounded-md border border-dashed border-slate-300 dark:border-slate-700 p-3 bg-white dark:bg-slate-900 text-center space-y-2 mt-2">
                                            <p className="text-xs text-muted-foreground">
                                                No hay modelos cargados para {selectedFabObject?.nombre || 'este fabricante'}.
                                            </p>
                                            <QuickModeloForm
                                                defaultFabricanteId={selectedFabricanteId}
                                                onSuccess={(nuevoModelo) => {
                                                    setListaModelos(prev => [...prev, nuevoModelo])
                                                    field.onChange(nuevoModelo.id)
                                                }}
                                                trigger={
                                                    <Button variant="secondary" size="sm" type="button" className="text-xs gap-1.5">
                                                        <Plus className="h-3.5 w-3.5" />
                                                        Registrar primer modelo para {selectedFabObject?.nombre || 'esta marca'}
                                                    </Button>
                                                }
                                            />
                                        </div>
                                    )}

                                    {/* Rich Spec Preview Card when a model is selected */}
                                    {selectedModelo && (
                                        <div className="rounded-lg border bg-emerald-50/50 dark:bg-emerald-950/20 border-emerald-200 dark:border-emerald-800/50 p-3 mt-2 space-y-2">
                                            <div className="flex items-center justify-between text-xs font-semibold text-emerald-800 dark:text-emerald-300">
                                                <span className="flex items-center gap-1.5">
                                                    <Disc className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
                                                    Ficha Técnica: {selectedModelo.nombre || selectedModelo.nombre_modelo}
                                                </span>
                                                <Badge variant="outline" className="font-mono bg-white dark:bg-slate-900 text-xs">
                                                    {selectedModelo.medida}
                                                </Badge>
                                            </div>
                                            <div className="grid grid-cols-4 gap-2 text-[11px] text-slate-600 dark:text-slate-400 font-mono pt-1 border-t border-emerald-100 dark:border-emerald-900/50">
                                                <div>
                                                    <span className="block text-[10px] text-muted-foreground">Prof. Fábrica</span>
                                                    <span className="font-bold text-slate-800 dark:text-slate-200">
                                                        {selectedModelo.profundidadOriginal ?? selectedModelo.profundidad_original_mm ?? '-'} mm
                                                    </span>
                                                </div>
                                                <div>
                                                    <span className="block text-[10px] text-muted-foreground">PSI Rec.</span>
                                                    <span className="font-bold text-slate-800 dark:text-slate-200">
                                                        {selectedModelo.presionRecomendada ?? selectedModelo.presion_recomendada_psi ?? '110'} PSI
                                                    </span>
                                                </div>
                                                <div>
                                                    <span className="block text-[10px] text-muted-foreground">Patrón</span>
                                                    <span className="font-bold text-slate-800 dark:text-slate-200">
                                                        {selectedModelo.patronDibujo ?? selectedModelo.patron_dibujo ?? 'TODA POS'}
                                                    </span>
                                                </div>
                                                <div>
                                                    <span className="block text-[10px] text-muted-foreground">Reencauches</span>
                                                    <span className="font-bold text-slate-800 dark:text-slate-200">
                                                        Máx {selectedModelo.reencauchesMaximos ?? selectedModelo.reencauches_maximos ?? 3}x
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    <FormMessage data-testid="select-modelo-error" />
                                </FormItem>
                            )
                        }}
                    />
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <FormField
                        control={form.control}
                        name="profundidad_inicial_mm"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Profundidad Inicial (mm) *</FormLabel>
                                <FormControl>
                                    <Input data-testid="input-profundidad-inicial" type="number" step="0.1" placeholder="18.5" {...field} />
                                </FormControl>
                                <FormMessage data-testid="input-profundidad-inicial-error" />
                            </FormItem>
                        )}
                    />
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
                </div>

                <div className="grid grid-cols-3 gap-4">
                    <FormField
                        control={form.control}
                        name="costo_compra"
                        render={({ field }) => (
                            <FormItem className="col-span-1">
                                <FormLabel>Costo Compra *</FormLabel>
                                <FormControl>
                                    <Input data-testid="input-costo-compra" type="number" step="0.01" placeholder="350.00" {...field} value={field.value ?? ""} />
                                </FormControl>
                                <FormMessage data-testid="input-costo-compra-error" />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="moneda_compra"
                        render={({ field }) => (
                            <FormItem className="col-span-1">
                                <FormLabel>Moneda</FormLabel>
                                <Select onValueChange={field.onChange} defaultValue={field.value} value={field.value}>
                                    <FormControl>
                                        <SelectTrigger>
                                            <SelectValue placeholder="PEN" />
                                        </SelectTrigger>
                                    </FormControl>
                                    <SelectContent>
                                        <SelectItem value="PEN">PEN (S/)</SelectItem>
                                        <SelectItem value="USD">USD ($)</SelectItem>
                                    </SelectContent>
                                </Select>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="fecha_compra"
                        render={({ field }) => (
                            <FormItem className="col-span-1">
                                <FormLabel>Fecha Compra *</FormLabel>
                                <FormControl>
                                    <Input type="date" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <FormField
                        control={form.control}
                        name="proveedor_compra_id"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Proveedor de Compra</FormLabel>
                                <Select onValueChange={field.onChange} defaultValue={field.value} value={field.value}>
                                    <FormControl>
                                        <SelectTrigger>
                                            <SelectValue placeholder="Seleccione proveedor (Opcional)" />
                                        </SelectTrigger>
                                    </FormControl>
                                    <SelectContent>
                                        {proveedores?.map((prov) => (
                                            <SelectItem key={prov.id} value={prov.id}>
                                                {prov.nombre} {prov.ruc ? `(${prov.ruc})` : ''}
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
                        name="ubicacion_almacen_id"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Almacén Inicial</FormLabel>
                                <Select onValueChange={field.onChange} defaultValue={field.value} value={field.value}>
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
                </div>

                <FormField
                    control={form.control}
                    name="es_reencauchado"
                    render={({ field }) => (
                        <FormItem className="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-3">
                            <FormControl>
                                <input
                                    type="checkbox"
                                    checked={field.value}
                                    onChange={field.onChange}
                                    className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                                />
                            </FormControl>
                            <div className="space-y-1 leading-none">
                                <FormLabel className="font-semibold cursor-pointer">
                                    ¿Es un neumático reencauchado?
                                </FormLabel>
                                <p className="text-xs text-muted-foreground">
                                    Marcar si la banda de rodamiento ha sido renovada.
                                </p>
                            </div>
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
