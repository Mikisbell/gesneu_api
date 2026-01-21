'use client';

import { useState, useEffect } from 'react';
import { Bell, Check, AlertTriangle, Info, AlertOctagon } from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';
import Link from 'next/link';

interface Alerta {
    id: string;
    tipo: string;
    severidad: 'CRITICAL' | 'WARNING' | 'INFO';
    mensaje: string;
    leida: boolean;
    creada_en: string;
}

export function AlertsDropdown() {
    const queryClient = useQueryClient();
    const [isOpen, setIsOpen] = useState(false);

    // Fetch unread alerts
    const { data: alerts = [], isLoading } = useQuery<Alerta[]>({
        queryKey: ['alertas-unread'],
        queryFn: () => apiClient('/alertas?leida=false&limit=10'),
        refetchInterval: 30000, // Poll every 30s
    });

    const unreadCount = alerts.length;

    // Mark as read mutation
    const readMutation = useMutation({
        mutationFn: (id: string) => apiClient('/alertas', {
            method: 'PATCH',
            body: JSON.stringify({ id, accion: 'MARCAR_LEIDA' })
        }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['alertas-unread'] });
        }
    });

    const getIcon = (severidad: string) => {
        switch (severidad) {
            case 'CRITICAL': return <AlertOctagon className="h-4 w-4 text-red-500" />;
            case 'WARNING': return <AlertTriangle className="h-4 w-4 text-amber-500" />;
            default: return <Info className="h-4 w-4 text-blue-500" />;
        }
    };

    const [mounted, setMounted] = useState(false);
    useEffect(() => {
        setMounted(true);
    }, []);

    if (!mounted) return (
        <Button variant="ghost" size="icon" className="relative opacity-50">
            <Bell className="h-5 w-5" />
        </Button>
    );

    return (
        <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
            <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="relative">
                    <Bell className="h-5 w-5" />
                    {unreadCount > 0 && (
                        <Badge
                            variant="destructive"
                            className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center rounded-full p-0 text-[10px]"
                        >
                            {unreadCount > 9 ? '9+' : unreadCount}
                        </Badge>
                    )}
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-80">
                <DropdownMenuLabel className="flex items-center justify-between">
                    <span>Notificaciones</span>
                    {unreadCount > 0 && (
                        <span className="text-xs text-muted-foreground font-normal">
                            {unreadCount} nuevas
                        </span>
                    )}
                </DropdownMenuLabel>
                <DropdownMenuSeparator />

                <ScrollArea className="h-[300px]">
                    {isLoading ? (
                        <div className="p-4 text-center text-sm text-muted-foreground">Cargando...</div>
                    ) : alerts.length === 0 ? (
                        <div className="p-4 text-center text-sm text-muted-foreground">
                            No tienes notificaciones nuevas
                        </div>
                    ) : (
                        <div className="py-1">
                            {alerts.map((alert) => (
                                <DropdownMenuItem
                                    key={alert.id}
                                    className="px-4 py-3 cursor-pointer items-start gap-3"
                                    onClick={() => readMutation.mutate(alert.id)}
                                >
                                    <div className="mt-1 shrink-0">
                                        {getIcon(alert.severidad)}
                                    </div>
                                    <div className="flex-1 space-y-1">
                                        <p className="text-sm font-medium leading-none">
                                            {alert.tipo.replace(/_/g, ' ')}
                                        </p>
                                        <p className="text-xs text-muted-foreground line-clamp-2">
                                            {alert.mensaje}
                                        </p>
                                        <p className="text-[10px] text-muted-foreground/70">
                                            {new Date(alert.creada_en).toLocaleDateString()}
                                        </p>
                                    </div>
                                    {!alert.leida && (
                                        <div className="shrink-0 h-2 w-2 rounded-full bg-blue-500 mt-2" />
                                    )}
                                </DropdownMenuItem>
                            ))}
                        </div>
                    )}
                </ScrollArea>

                <DropdownMenuSeparator />
                <DropdownMenuItem asChild className="w-full text-center cursor-pointer">
                    <Link href="/dashboard/alertas" className="w-full block text-center font-medium">
                        Ver todas las alertas
                    </Link>
                </DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
    );
}
