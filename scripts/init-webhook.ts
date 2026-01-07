const { PrismaClient, WebhookEventType } = require('@prisma/client');

const prisma = new PrismaClient();

async function main() {
    const webhook = await prisma.webhookConfig.create({
        data: {
            nombre: "SAP Integration",
            url: "https://webhook.site/uuid-placeholder", // Usuario usó placeholder, mantengo placeholder
            secret: "mi_secreto_seguro",
            eventos: [WebhookEventType.ALL_EVENTS],
            activo: true
        }
    });

    console.log(`✅ Webhook creado con ID: ${webhook.id}`);
    console.log(webhook);
}

main()
    .catch(e => console.error(e))
    .finally(async () => await prisma.$disconnect());
