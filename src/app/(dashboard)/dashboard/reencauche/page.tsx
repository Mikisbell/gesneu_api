'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { DataTable } from '@/components/ui/data-table';
import { ColumnDef } from '@tanstack/react-table';
import { toast } from 'sonner';
import { RefreshCw, Truck, Factory, TrendingUp } from 'lucide-react';
import { apiClient } from '@/lib/api/client';

// Types
interface Neumatico {
    id: string;
    numero_serie: string;
    modelo: { nombre_modelo: string; fabricante: { nombre: string } };
    profundidad_remanente_actual_mm: number;
    vida_actual: number;
    reencauches_realizados: number;
    estado_actual: string;
}

interface IndiceReencauchabilidad {
    total_neumaticos: number;
    total_vidas_acumuladas: number;
    ir_global: number;
    interpretacion: string;
}

// API Functions
const fetchNeumaticosParaEnviar = async (): Promise<Neumatico[]> => {
    const data = await apiClient<Neumatico[]>('/neumaticos?estado=EN_STOCK');
    // Filter those with low tread depth (candidates for retread)
    return (data || []).filter(n => Number(n.profundidad_remanente_actual_mm) < 5);
};

const fetchNeumaticosEnPlanta = async (): Promise<Neumatico[]> => {
    return await apiClient<Neumatico[]>('/neumaticos?estado=EN_REENCAUCHE') || [];
};

const fetchIndiceIR = async (): Promise<IndiceReencauchabilidad> => {
    return await apiClient<IndiceReencauchabilidad>('/reencauche/indice');
};

// Column Definitions
// We must move columns inside the component or use cell renderers properly dealing with hooks if needed.
// Since Dialogs use hooks (useMutation), they are safe inside cell renderers.

import { EnviarNeumaticoDialog } from '@/components/reencauche/EnviarNeumaticoDialog';
import { RecepcionarNeumaticoDialog } from '@/components/reencauche/RecepcionarNeumaticoDialog';

const columnsParaEnviar: ColumnDef<Neumatico>[] = [
    { accessorKey: 'numero_serie', header: 'Nº Serie' },
    { accessorKey: 'modelo.nombre_modelo', header: 'Modelo' },
    {
        accessorKey: 'profundidad_remanente_actual_mm',
        header: 'Prof. (mm)',
        cell: ({ row }) => <span className="font-mono">{Number(row.original.profundidad_remanente_actual_mm).toFixed(1)}</span>
    },
    { accessorKey: 'vida_actual', header: 'Vida' },
    {
        id: 'actions',
        cell: ({ row }) => (
            <EnviarNeumaticoDialog
                neumaticoId={row.original.id}
                numeroSerie={row.original.numero_serie}
            />
        )
    }
];

const columnsEnPlanta: ColumnDef<Neumatico>[] = [
    { accessorKey: 'numero_serie', header: 'Nº Serie' },
    { accessorKey: 'modelo.nombre_modelo', header: 'Modelo' },
    { accessorKey: 'vida_actual', header: 'Vida Anterior' },
    {
        id: 'actions',
        cell: ({ row }) => (
            <RecepcionarNeumaticoDialog
                neumaticoId={row.original.id}
                numeroSerie={row.original.numero_serie}
            />
        )
    }
];

export default function ReencauchePage() {
    const queryClient = useQueryClient();

    // Queries
    const { data: paraEnviar = [], isLoading: loadingEnviar } = useQuery({
        queryKey: ['neumaticos-para-enviar'],
        queryFn: fetchNeumaticosParaEnviar
    });

    const { data: enPlanta = [], isLoading: loadingPlanta } = useQuery({
        queryKey: ['neumaticos-en-planta'],
        queryFn: fetchNeumaticosEnPlanta
    });

    const { data: indice, isLoading: loadingIndice } = useQuery({
        queryKey: ['indice-reencauchabilidad'],
        queryFn: fetchIndiceIR
    });

    return (
        <div className="flex flex-col gap-6 p-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Gestión de Reencauche</h1>
                    <p className="text-muted-foreground">Envío, recepción y seguimiento del ciclo de vida.</p>
                </div>
                <Button
                    variant="outline"
                    onClick={() => queryClient.invalidateQueries()}
                    className="gap-2"
                >
                    <RefreshCw className="h-4 w-4" /> Actualizar
                </Button>
            </div>

            {/* KPI Card */}
            <Card className="bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-emerald-950/30 dark:to-teal-950/30 border-emerald-200">
                <CardHeader className="pb-2">
                    <CardTitle className="text-lg flex items-center gap-2">
                        <TrendingUp className="h-5 w-5 text-emerald-600" />
                        Índice de Reencauchabilidad (IR)
                    </CardTitle>
                    <CardDescription>Promedio de vidas útiles de tu flota</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="flex items-baseline gap-4">
                        <span className="text-5xl font-extrabold text-emerald-700 dark:text-emerald-400">
                            {loadingIndice ? '...' : indice?.ir_global?.toFixed(2) || '0.00'}
                        </span>
                        <Badge variant="secondary" className="text-sm">
                            {indice?.interpretacion || 'Sin datos'}
                        </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground mt-2">
                        {indice?.total_neumaticos || 0} neumáticos | {indice?.total_vidas_acumuladas || 0} vidas acumuladas
                    </p>
                </CardContent>
            </Card>

            {/* Tabs */}
            <Tabs defaultValue="enviar" className="w-full">
                <TabsList className="grid w-full max-w-md grid-cols-2">
                    <TabsTrigger value="enviar" className="gap-2">
                        <Truck className="h-4 w-4" /> Por Enviar ({paraEnviar.length})
                    </TabsTrigger>
                    <TabsTrigger value="planta" className="gap-2">
                        <Factory className="h-4 w-4" /> En Planta ({enPlanta.length})
                    </TabsTrigger>
                </TabsList>

                <TabsContent value="enviar" className="mt-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>Neumáticos Listos para Reencauche</CardTitle>
                            <CardDescription>Cascos con profundidad menor a 5mm, en almacén.</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <DataTable
                                columns={columnsParaEnviar}
                                data={paraEnviar}
                            />
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="planta" className="mt-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>Neumáticos en Planta de Reencauche</CardTitle>
                            <CardDescription>Esperando retorno con nueva banda.</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <DataTable
                                columns={columnsEnPlanta}
                                data={enPlanta}
                            />
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    );
}
