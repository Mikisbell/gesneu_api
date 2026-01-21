'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/components/ui/use-toast';
import { FileText, Download, BarChart3, TrendingUp, Truck, CircleDollarSign, Loader2, FileSpreadsheet, PieChart as PieIcon } from 'lucide-react';
import { InventoryPieChart } from '@/components/dashboard/charts/InventoryPieChart';
import { CPKBarChart } from '@/components/dashboard/charts/CPKBarChart';

interface ReportCard {
    id: string;
    title: string;
    description: string;
    icon: React.ReactNode;
    category: string;
    endpoint: string;
}

const REPORTS: ReportCard[] = [
    {
        id: 'flota',
        title: 'Estado de Flota',
        description: 'Resumen de todos los vehículos y neumáticos instalados.',
        icon: <Truck className="h-8 w-8" />,
        category: 'Operacional',
        endpoint: '/api/v1/reportes/flota',
    },
    {
        id: 'cpk',
        title: 'Costo por Kilómetro (CPK)',
        description: 'Análisis de costo operativo por neumático y marca.',
        icon: <CircleDollarSign className="h-8 w-8" />,
        category: 'Financiero',
        endpoint: '/api/v1/reportes/cpk',
    },
    {
        id: 'desgaste',
        title: 'Tasa de Desgaste',
        description: 'Comparativa de desgaste por modelo y posición.',
        icon: <TrendingUp className="h-8 w-8" />,
        category: 'Técnico',
        endpoint: '/api/v1/reportes/desgaste',
    },
    {
        id: 'inventario',
        title: 'Inventario de Stock',
        description: 'Neumáticos disponibles en almacén por estado.',
        icon: <BarChart3 className="h-8 w-8" />,
        category: 'Operacional',
        endpoint: '/api/v1/reportes/inventario',
    },
];

export default function ReportesPage() {
    const { toast } = useToast();
    const [generatingReport, setGeneratingReport] = useState<string | null>(null);
    const [selectedFormat, setSelectedFormat] = useState<'pdf' | 'excel'>('pdf');

    // Fetch dashboard stats for quick preview
    const { data: stats, isLoading } = useQuery({
        queryKey: ['dashboard-stats'],
        queryFn: () => apiClient<any>('/api/v1/dashboard'),
    });

    // Fetch Chart Data
    const { data: inventoryData } = useQuery({
        queryKey: ['reporte-inventario'],
        queryFn: () => apiClient<any>('/api/v1/reportes/inventario'),
    });

    const { data: cpkData } = useQuery({
        queryKey: ['reporte-cpk-brands'],
        queryFn: () => apiClient<any>('/api/v1/reportes/comparativo-marcas'),
    });

    const handleGenerateReport = async (report: ReportCard) => {
        setGeneratingReport(report.id);
        toast({
            title: '📄 Generando reporte...',
            description: `Preparando ${report.title} en formato ${selectedFormat.toUpperCase()}`,
        });

        try {
            // Simulated - in production this would call the API and download
            const response = await fetch(`${report.endpoint}?format=${selectedFormat}`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
            });

            if (!response.ok) {
                throw new Error('Error generando reporte');
            }

            // For PDF/Excel, we'd normally handle blob download
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${report.id}_${new Date().toISOString().split('T')[0]}.${selectedFormat}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            toast({
                title: '✅ Reporte generado',
                description: `${report.title} descargado correctamente.`,
            });
        } catch (error) {
            toast({
                title: '⚠️ Reporte en desarrollo',
                description: 'Esta funcionalidad estará disponible pronto.',
                variant: 'default',
            });
        } finally {
            setGeneratingReport(null);
        }
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
                        <FileText className="h-8 w-8" /> Centro de Reportes
                    </h1>
                    <p className="text-muted-foreground">Métricas en tiempo real y descarga de informes</p>
                </div>
                <div className="flex items-center gap-2">
                    <span className="text-sm text-muted-foreground">Formato Descarga:</span>
                    <Select value={selectedFormat} onValueChange={(v) => setSelectedFormat(v as 'pdf' | 'excel')}>
                        <SelectTrigger className="w-32">
                            <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="pdf">PDF</SelectItem>
                            <SelectItem value="excel">Excel</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
            </div>

            <Tabs defaultValue="dashboard" className="w-full">
                <TabsList>
                    <TabsTrigger value="dashboard" className="flex gap-2"><PieIcon className="w-4 h-4" /> Dashboard Analítico</TabsTrigger>
                    <TabsTrigger value="downloads" className="flex gap-2"><Download className="w-4 h-4" /> Zona de Descargas</TabsTrigger>
                </TabsList>

                <TabsContent value="dashboard" className="mt-6 space-y-6">
                    {/* Quick Stats Row */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <Card>
                            <CardContent className="pt-6">
                                <div className="text-center">
                                    <p className="text-sm text-muted-foreground">Vehículos</p>
                                    <p className="text-3xl font-bold">{isLoading ? '-' : stats?.vehiculos?.total || 0}</p>
                                </div>
                            </CardContent>
                        </Card>
                        <Card>
                            <CardContent className="pt-6">
                                <div className="text-center">
                                    <p className="text-sm text-muted-foreground">Neumáticos</p>
                                    <p className="text-3xl font-bold">{isLoading ? '-' : stats?.neumaticos?.total || 0}</p>
                                </div>
                            </CardContent>
                        </Card>
                        <Card>
                            <CardContent className="pt-6">
                                <div className="text-center">
                                    <p className="text-sm text-muted-foreground">En Stock</p>
                                    <p className="text-3xl font-bold text-green-600">{isLoading ? '-' : stats?.neumaticos?.en_stock || 0}</p>
                                </div>
                            </CardContent>
                        </Card>
                        <Card>
                            <CardContent className="pt-6">
                                <div className="text-center">
                                    <p className="text-sm text-muted-foreground">Alertas Activas</p>
                                    <p className="text-3xl font-bold text-amber-600">{isLoading ? '-' : stats?.alertas?.pendientes || 0}</p>
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Charts Row */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <CPKBarChart data={cpkData?.marcas || []} />
                        <InventoryPieChart data={inventoryData?.stock_por_marca || []} />
                    </div>
                </TabsContent>

                <TabsContent value="downloads" className="mt-6">
                    {/* Reports Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {REPORTS.map((report) => (
                            <Card key={report.id} className="hover:shadow-lg transition-shadow">
                                <CardHeader>
                                    <div className="flex items-start justify-between">
                                        <div className="p-3 rounded-lg bg-primary/10 text-primary">
                                            {report.icon}
                                        </div>
                                        <span className="text-xs bg-muted px-2 py-1 rounded">{report.category}</span>
                                    </div>
                                    <CardTitle className="mt-4">{report.title}</CardTitle>
                                    <CardDescription>{report.description}</CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <Button
                                        className="w-full"
                                        onClick={() => handleGenerateReport(report)}
                                        disabled={generatingReport === report.id}
                                    >
                                        {generatingReport === report.id ? (
                                            <>
                                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                                Generando...
                                            </>
                                        ) : (
                                            <>
                                                <Download className="mr-2 h-4 w-4" />
                                                Descargar {selectedFormat.toUpperCase()}
                                            </>
                                        )}
                                    </Button>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                </TabsContent>
            </Tabs>
        </div>
    );
}
