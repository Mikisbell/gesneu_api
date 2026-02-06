'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { DataTable } from '@/components/ui/data-table';
import { ColumnDef } from '@tanstack/react-table';
import { toast } from 'sonner';
import { Gauge, Ruler, AlertTriangle, RefreshCw, Loader2 } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from '@/components/ui/dialog';

// Types
interface Neumatico {
    id: string;
    numero_serie: string;
    modelo: { nombre_modelo: string };
    presion_actual_psi: number | null;
    profundidad_remanente_actual_mm: number | null;
    estado_actual: string;
}

interface Alerta {
    id: string;
    tipo: string;
    severidad: string;
    mensaje: string;
    creada_en: string;
    neumatico?: { numero_serie: string };
}

// API Functions
const fetchNeumaticosActivos = async (): Promise<Neumatico[]> => {
    return await apiClient<Neumatico[]>('/neumaticos?estado=EN_VEHICULO') || [];
};

const fetchAlertasRecientes = async (): Promise<Alerta[]> => {
    return await apiClient<Alerta[]>('/alertas?limit=10') || [];
};

// Columns for Tires Table
const columnsTires: ColumnDef<Neumatico>[] = [
    { accessorKey: 'numero_serie', header: 'Nº Serie' },
    { accessorKey: 'modelo.nombre_modelo', header: 'Modelo' },
    {
        accessorKey: 'presion_actual_psi',
        header: 'Presión (PSI)',
        cell: ({ row }) => {
            const val = row.original.presion_actual_psi;
            return val ? <span className="font-mono">{Number(val).toFixed(0)}</span> : '-';
        }
    },
    {
        accessorKey: 'profundidad_remanente_actual_mm',
        header: 'Prof. (mm)',
        cell: ({ row }) => {
            const val = row.original.profundidad_remanente_actual_mm;
            return val ? <span className="font-mono">{Number(val).toFixed(1)}</span> : '-';
        }
    },
    {
        id: 'actions',
        cell: ({ row }) => (
            <div className="flex gap-2">
                <RegistrarPresionDialog neumaticoId={row.original.id} numeroSerie={row.original.numero_serie} />
                <RegistrarProfundidadDialog neumaticoId={row.original.id} numeroSerie={row.original.numero_serie} />
            </div>
        )
    }
];

// Columns for Alerts Table
const columnsAlertas: ColumnDef<Alerta>[] = [
    {
        accessorKey: 'severidad',
        header: 'Sev.',
        cell: ({ row }) => (
            <Badge variant={row.original.severidad === 'CRITICAL' ? 'destructive' : 'secondary'}>
                {row.original.severidad}
            </Badge>
        )
    },
    { accessorKey: 'tipo', header: 'Tipo' },
    { accessorKey: 'neumatico.numero_serie', header: 'Neumático' },
    { accessorKey: 'mensaje', header: 'Mensaje' },
    {
        accessorKey: 'creada_en',
        header: 'Fecha',
        cell: ({ row }) => new Date(row.original.creada_en).toLocaleString()
    }
];

// Dialog: Registrar Presión
function RegistrarPresionDialog({ neumaticoId, numeroSerie }: { neumaticoId: string; numeroSerie: string }) {
    const [open, setOpen] = useState(false);
    const [presion, setPresion] = useState('');
    const queryClient = useQueryClient();

    const { mutate, isPending } = useMutation({
        mutationFn: () => apiClient('/inspecciones/presion', {
            method: 'POST',
            body: JSON.stringify({ neumatico_id: neumaticoId, presion_psi: Number(presion) })
        }),
        onSuccess: () => {
            toast.success(`Presión registrada para ${numeroSerie}`);
            queryClient.invalidateQueries({ queryKey: ['neumaticos-activos'] });
            queryClient.invalidateQueries({ queryKey: ['alertas-recientes'] });
            setOpen(false);
            setPresion('');
        },
        onError: (e: any) => toast.error(e.message)
    });

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button size="sm" variant="outline" className="gap-1">
                    <Gauge className="h-4 w-4" /> PSI
                </Button>
            </DialogTrigger>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>Registrar Presión</DialogTitle>
                    <DialogDescription>Neumático: <strong>{numeroSerie}</strong></DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="presion" className="text-right">PSI</Label>
                        <Input
                            id="presion"
                            type="number"
                            className="col-span-3"
                            value={presion}
                            onChange={(e) => setPresion(e.target.value)}
                            placeholder="Ej: 100"
                        />
                    </div>
                </div>
                <DialogFooter>
                    <Button variant="outline" onClick={() => setOpen(false)}>Cancelar</Button>
                    <Button onClick={() => mutate()} disabled={isPending || !presion}>
                        {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        Guardar
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}

// Dialog: Registrar Profundidad
function RegistrarProfundidadDialog({ neumaticoId, numeroSerie }: { neumaticoId: string; numeroSerie: string }) {
    const [open, setOpen] = useState(false);
    const [pInt, setPInt] = useState('');
    const [pCen, setPCen] = useState('');
    const [pExt, setPExt] = useState('');
    const queryClient = useQueryClient();

    const { mutate, isPending } = useMutation({
        mutationFn: () => apiClient('/inspecciones/profundidad', {
            method: 'POST',
            body: JSON.stringify({
                neumatico_id: neumaticoId,
                profundidad_int: Number(pInt),
                profundidad_cen: Number(pCen),
                profundidad_ext: Number(pExt)
            })
        }),
        onSuccess: () => {
            toast.success(`Profundidad registrada para ${numeroSerie}`);
            queryClient.invalidateQueries({ queryKey: ['neumaticos-activos'] });
            queryClient.invalidateQueries({ queryKey: ['alertas-recientes'] });
            setOpen(false);
        },
        onError: (e: any) => toast.error(e.message)
    });

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button size="sm" variant="outline" className="gap-1">
                    <Ruler className="h-4 w-4" /> mm
                </Button>
            </DialogTrigger>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>Registrar Profundidad</DialogTitle>
                    <DialogDescription>Neumático: <strong>{numeroSerie}</strong></DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label className="text-right">Interior</Label>
                        <Input type="number" className="col-span-3" value={pInt} onChange={(e) => setPInt(e.target.value)} placeholder="mm" />
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label className="text-right">Centro</Label>
                        <Input type="number" className="col-span-3" value={pCen} onChange={(e) => setPCen(e.target.value)} placeholder="mm" />
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label className="text-right">Exterior</Label>
                        <Input type="number" className="col-span-3" value={pExt} onChange={(e) => setPExt(e.target.value)} placeholder="mm" />
                    </div>
                </div>
                <DialogFooter>
                    <Button variant="outline" onClick={() => setOpen(false)}>Cancelar</Button>
                    <Button onClick={() => mutate()} disabled={isPending || !pInt || !pCen || !pExt}>
                        {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        Guardar
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}

// Main Page
export default function InspeccionesPage() {
    const queryClient = useQueryClient();

    const { data: neumaticos = [], isLoading: loadingTires } = useQuery({
        queryKey: ['neumaticos-activos'],
        queryFn: fetchNeumaticosActivos
    });

    const { data: alertas = [], isLoading: loadingAlertas } = useQuery({
        queryKey: ['alertas-recientes'],
        queryFn: fetchAlertasRecientes
    });

    return (
        <div className="flex flex-col gap-6 p-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Inspecciones</h1>
                    <p className="text-muted-foreground">Registro de lecturas de presión y profundidad.</p>
                </div>
                <Button variant="outline" onClick={() => queryClient.invalidateQueries()} className="gap-2">
                    <RefreshCw className="h-4 w-4" /> Actualizar
                </Button>
            </div>

            {/* Tabs */}
            <Tabs defaultValue="neumaticos" className="w-full">
                <TabsList className="grid w-full max-w-md grid-cols-2">
                    <TabsTrigger value="neumaticos" className="gap-2">
                        <Gauge className="h-4 w-4" /> Neumáticos ({neumaticos.length})
                    </TabsTrigger>
                    <TabsTrigger value="alertas" className="gap-2">
                        <AlertTriangle className="h-4 w-4" /> Alertas ({alertas.length})
                    </TabsTrigger>
                </TabsList>

                <TabsContent value="neumaticos" className="mt-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>Neumáticos en Vehículos</CardTitle>
                            <CardDescription>Registre lecturas directamente desde aquí.</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <DataTable columns={columnsTires} data={neumaticos} />
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="alertas" className="mt-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>Alertas Recientes</CardTitle>
                            <CardDescription>Últimas alertas generadas automáticamente.</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <DataTable columns={columnsAlertas} data={alertas} />
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    );
}
