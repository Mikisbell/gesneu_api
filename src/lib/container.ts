import { NeumaticoService } from './services/neumatico.service';
import { AlertasService } from './services/alertas.service';
import { DashboardService } from './services/dashboard.service';
import { ReportesService } from './services/reportes.service';
import { EventoNeumaticoService } from './services/evento-neumatico.service';

import { UsuarioService } from './services/usuario.service';
import { VehiculoService } from './services/vehiculo.service';
import { AlmacenService } from './services/almacen.service';
import { ProveedorService } from './services/proveedor.service';
import { WebhookService } from './services/webhook.service';
import { TenantService } from './services/tenant.service';

/**
 * Dependency Injection Container (Singleton Definitions)
 * Centralizes service instantiation to ensure singletons and ease mocking.
 */

// Core Services
export const alertasService = new AlertasService();
export const eventoNeumaticoService = new EventoNeumaticoService();
export const webhookService = new WebhookService();
export const tenantService = new TenantService();

// Domain Services
export const neumaticoService = new NeumaticoService();
export const dashboardService = new DashboardService();
export const reportesService = new ReportesService();
export const usuarioService = new UsuarioService();
export const vehiculoService = new VehiculoService();
export const almacenService = new AlmacenService();
export const proveedorService = new ProveedorService();

// Note: Circular dependencies or cross-service usage should be handled via 
// Dependency Injection in constructors, passing these instances if needed.
// For now, services instantiate their deps internally (Legacy), 
// but we expose singletons here for Controllers/API Routes.
