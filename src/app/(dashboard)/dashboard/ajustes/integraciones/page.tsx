import { getWebhooks } from '@/lib/actions/webhook.actions';
import { WebhookDialog } from './webhook-dialog';
import { PageHeader } from '@/components/layout/page-header';
import { WebhooksClient } from './webhooks-client';

export default async function WebhooksPage() {
    const data = await getWebhooks();

    return (
        <div className="flex-1 space-y-4  p-4 md:p-8 pt-6">
            <PageHeader
                title={`Integraciones (${data.length})`}
                description="Gestiona webhooks para notificar eventos a sistemas externos (ERP, Slack, etc)."
            >
                <WebhookDialog />
            </PageHeader>
            <WebhooksClient data={data} />
        </div>
    );
}
