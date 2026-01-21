'use client';

import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { AlertOctagon, AlertTriangle, Info, Check, Eye } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';

interface AlertaProps {
    alerta: {
        id: string;
        tipo: string;
        severidad: 'CRITICAL' | 'WARNING' | 'INFO';
        mensaje: string;
        leida: boolean;
        resuelta: boolean;
        creada_en: string;
        neumatico?: { numero_serie: string };
        vehiculo?: { placa: string };
    };
    onRead: (id: string) => void;
    onResolve: (id: string) => void;
}

export function AlertCard({ alerta, onRead, onResolve }: AlertaProps) {
    const getIcon = (severidad: string) => {
        switch (severidad) {
            case 'CRITICAL': return <AlertOctagon className="h-5 w-5 text-destructive" />;
            case 'WARNING': return <AlertTriangle className="h-5 w-5 text-amber-500" />;
            default: return <Info className="h-5 w-5 text-blue-500" />;
        }
    };

    const getBadgeVariant = (severidad: string) => {
        switch (severidad) {
            case 'CRITICAL': return 'destructive';
            case 'WARNING': return 'default'; // Or custom yellow
            default: return 'secondary';
        }
    };

    return (
        <Card className={`transition-all ${!alerta.leida ? 'border-l-4 border-l-primary bg-muted/10' : ''}`}>
            <CardHeader className="pb-2">
                <div className="flex justify-between items-start">
                    <div className="flex items-center gap-2">
                        {getIcon(alerta.severidad)}
                        <CardTitle className="text-base font-semibold">
                            {alerta.tipo.replace(/_/g, ' ')}
                        </CardTitle>
                        <Badge variant={getBadgeVariant(alerta.severidad)} className="ml-2 text-[10px]">
                            {alerta.severidad}
                        </Badge>
                    </div>
                    <span className="text-xs text-muted-foreground">
                        {formatDistanceToNow(new Date(alerta.creada_en), { addSuffix: true, locale: es })}
                    </span>
                </div>
            </CardHeader>
            <CardContent>
                <p className="text-sm text-muted-foreground mb-4">
                    {alerta.mensaje}
                </p>
                <div className="flex gap-4 text-xs font-medium text-foreground">
                    {alerta.vehiculo && (
                        <span className="flex items-center gap-1 bg-secondary px-2 py-1 rounded">
                            🚚 {alerta.vehiculo.placa}
                        </span>
                    )}
                    {alerta.neumatico && (
                        <span className="flex items-center gap-1 bg-secondary px-2 py-1 rounded">
                            🔘 {alerta.neumatico.numero_serie}
                        </span>
                    )}
                </div>
            </CardContent>
            <CardFooter className="flex justify-end gap-2 pt-2 border-t bg-muted/5">
                {!alerta.leida && (
                    <Button variant="ghost" size="sm" onClick={() => onRead(alerta.id)}>
                        <Eye className="h-4 w-4 mr-2" />
                        Marcar Leída
                    </Button>
                )}
                {!alerta.resuelta && (
                    <Button variant="outline" size="sm" onClick={() => onResolve(alerta.id)} className="text-green-600 border-green-200 hover:bg-green-50">
                        <Check className="h-4 w-4 mr-2" />
                        Resolver
                    </Button>
                )}
                {alerta.resuelta && (
                    <span className="text-xs text-green-600 flex items-center font-medium px-3">
                        <Check className="h-3 w-3 mr-1" /> Resuelta
                    </span>
                )}
            </CardFooter>
        </Card>
    );
}
