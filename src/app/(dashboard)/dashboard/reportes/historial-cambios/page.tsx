'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { ColumnDef } from '@tanstack/react-table';
import { DataTable } from '@/components/ui/data-table';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Loader2, ArrowRight } from 'lucide-react';
import Link from 'next/link';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

interface ChangeLogEntry {
    id: string;
    fecha: string;
    ot: string;
    vehiculo: string;
    posicion: string;

    entrante: {
        serie: string;
        marca: string;
        modelo: string;
        km: number;
    };

    saliente?: {
        serie: string;
        marca: string;
        modelo: string;
        km: number;
        mm_remanente: number;
        motivo: string;
    };
}

const columns: ColumnDef<ChangeLogEntry>[] = [
    {
        accessorKey: "fecha",
        header: "Fecha / OT",
        cell: ({ row }) => (
            <div className="flex flex-col">
                <span className="font-semibold">{format(new Date(row.original.fecha), 'dd/MM/yyyy')}</span>
                <span className="text-xs text-muted-foreground">OT: {row.original.ot}</span>
            </div>
        )
    },
    {
        accessorKey: "vehiculo",
        header: "Ubicación",
        cell: ({ row }) => (
            <div className="flex flex-col">
                <span>{row.original.vehiculo}</span>
                <span className="text-xs text-muted-foreground">Pos {row.original.posicion}</span>
            </div>
        )
    },
    {
        id: "change_flow",
        header: "Intercambio (Saliente -> Entrante)",
        cell: ({ row }) => {
            const ent = row.original.entrante;
            const sal = row.original.saliente;

            return (
                <div className="flex items-center gap-4">
                    {/* Saliente (Left) */}
                    <div className="flex-1 text-right  min-w-[150px]">
                        {sal ? (
                            <div className="flex flex-col">
                                <span className="text-red-600 font-medium">{sal.serie}</span>
                                <span className="text-xs text-muted-foreground">{sal.marca}</span>
                                <span className="text-xs">{sal.mm_remanente}mm remanente</span>
                            </div>
                        ) : (
                            <span className="text-sm text-gray-400 italic">Posición Vacia</span>
                        )}
                    </div>

                    {/* Arrow */}
                    <div className="flex items-center justify-center">
                        <ArrowRight className="h-4 w-4 text-muted-foreground" />
                    </div>

                    {/* Entrante (Right) */}
                    <div className="flex-1 text-left min-w-[150px]">
                        <div className="flex flex-col">
                            <span className="text-green-600 font-medium">{ent.serie}</span>
                            <span className="text-xs text-muted-foreground">{ent.marca}</span>
                            <span className="text-xs">Instalado a {ent.km.toLocaleString()} km</span>
                        </div>
                    </div>
                </div>
            )
        }
    },
    {
        accessorKey: "motivo",
        header: "Motivo Cambio",
        cell: ({ row }) => row.original.saliente?.motivo || 'Instalación Inicial'
    },
];

export default function HistorialCambiosPage() {
    const { data: history, isLoading, error } = useQuery<ChangeLogEntry[]>({
        queryKey: ['historial-cambios'],
        queryFn: () => apiClient<ChangeLogEntry[]>('/reportes/historial-cambios'),
    });

    if (error) return <div className="p-8 text-center text-red-500">Error cargando historial</div>;
    if (isLoading) return <div className="p-8 flex justify-center"><Loader2 className="animate-spin h-8 w-8" /></div>;

    return (
        <div className="space-y-6 container mx-auto py-6">
            <div className="flex items-center gap-4">
                <Link href="/dashboard/reportes">
                    <Button variant="ghost" size="icon">
                        <ArrowLeft className="h-4 w-4" />
                    </Button>
                </Link>
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Bitácora de Cambios (Logbook)</h1>
                    <p className="text-muted-foreground">Registro cronológico de entradas y salidas de neumáticos.</p>
                </div>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Historial de Movimientos</CardTitle>
                    <CardDescription>
                        Visualización comparativa de neumático retirado vs instalado.
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <DataTable
                        columns={columns}
                        data={history || []}
                        searchKey="vehiculo" // Filtrar por placa 
                    />
                </CardContent>
            </Card>
        </div>
    );
}
