'use client';

import { ColumnDef } from '@tanstack/react-table';
import { WebhookConfig } from '@prisma/client';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { MoreHorizontal, Power, Trash } from 'lucide-react';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { deleteWebhook, toggleWebhook } from '@/lib/actions/webhook.actions';
import { toast } from 'sonner';

export const getColumns = (): ColumnDef<WebhookConfig>[] => [
    {
        accessorKey: 'nombre',
        header: 'Nombre',
    },
    {
        accessorKey: 'url',
        header: 'URL Endpoint',
        cell: ({ row }) => <div className="font-mono text-xs">{row.original.url}</div>,
    },
    {
        accessorKey: 'eventos',
        header: 'Eventos Suscritos',
        cell: ({ row }) => (
            <div className="flex flex-wrap gap-1">
                {row.original.eventos.map((e) => (
                    <Badge key={e} variant="outline" className="text-[10px]">
                        {e}
                    </Badge>
                ))}
            </div>
        ),
    },
    {
        accessorKey: 'activo',
        header: 'Estado',
        cell: ({ row }) => (
            <Badge variant={row.original.activo ? 'default' : 'secondary'}>
                {row.original.activo ? 'Activo' : 'Inactivo'}
            </Badge>
        ),
    },
    {
        id: 'actions',
        cell: ({ row }) => {
            const webhook = row.original;

            return (
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <Button variant="ghost" className="h-8 w-8 p-0">
                            <span className="sr-only">Open menu</span>
                            <MoreHorizontal className="h-4 w-4" />
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                        <DropdownMenuLabel>Acciones</DropdownMenuLabel>
                        <DropdownMenuItem
                            onClick={() => {
                                navigator.clipboard.writeText(webhook.secret);
                                toast.success('Secret copiado al portapapeles');
                            }}
                        >
                            Copiar Secret (HMAC)
                        </DropdownMenuItem>
                        <DropdownMenuItem
                            onClick={async () => {
                                await toggleWebhook(webhook.id, !webhook.activo);
                                toast.success(`Webhook ${webhook.activo ? 'desactivado' : 'activado'}`);
                            }}
                        >
                            <Power className="mr-2 h-4 w-4" />
                            {webhook.activo ? 'Desactivar' : 'Activar'}
                        </DropdownMenuItem>
                        <DropdownMenuItem
                            className="text-red-600 focus:text-red-600"
                            onClick={async () => {
                                await deleteWebhook(webhook.id);
                                toast.success('Webhook eliminado');
                            }}
                        >
                            <Trash className="mr-2 h-4 w-4" />
                            Eliminar
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            );
        },
    },
];
