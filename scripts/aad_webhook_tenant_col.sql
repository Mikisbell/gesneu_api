
-- Migration to add multi-tenancy to webhooks
ALTER TABLE "webhook_configs" ADD COLUMN "empresa_id" UUID DEFAULT '00000000-0000-0000-0000-000000000000';

-- Constraint (Optional: strictly enforce it points to valid enterprise, but we use default 00..00 for legacy items)
-- ALTER TABLE "webhook_configs" ADD CONSTRAINT "fk_webhook_empresa" FOREIGN KEY ("empresa_id") REFERENCES "empresas"("id");
