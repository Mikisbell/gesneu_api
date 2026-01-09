'use client';

import { getColumns } from './columns';
import { WebhookConfig } from '@prisma/client';
import { DataTable } from '@/components/ui/data-table';

interface WebhooksClientProps {
    data: WebhookConfig[];
}

export function WebhooksClient({ data }: WebhooksClientProps) {
    const columns = getColumns();

    return (
        <DataTable searchKey="nombre" columns={columns} data={data} />
    );
}
