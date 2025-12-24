import { Resend } from 'resend';

// Inicializar Resend de forma lazy para evitar errores en build si falta la KEY
const getResendClient = () => {
    if (!process.env.RESEND_API_KEY) return null;
    return new Resend(process.env.RESEND_API_KEY);
};

// Dominio de origen para emails (configurable)
const FROM_EMAIL = process.env.EMAIL_FROM || 'GesNeu <alertas@gesneu.com>';
const APP_URL = process.env.NEXTAUTH_URL || 'https://gesneu.vercel.app';

interface AlertaEmailData {
    tipo: string;
    severidad: 'CRITICA' | 'ALTA' | 'MEDIA' | 'BAJA';
    mensaje: string;
    neumatico?: {
        numero_serie: string;
        profundidad_mm?: number;
    };
    vehiculo?: {
        placa: string;
        codigo_interno?: string;
    };
}

interface EmailRecipient {
    email: string;
    nombre?: string;
}

/**
 * Servicio de Email para GesNeu
 * Utiliza Resend para envío de emails transaccionales
 */
export const EmailService = {
    /**
     * Envía notificación de alerta crítica
     */
    async sendAlertNotification(
        recipients: EmailRecipient[],
        alerta: AlertaEmailData
    ): Promise<{ success: boolean; messageId?: string; error?: string }> {
        const resend = getResendClient();
        if (!resend) {
            console.warn('[EmailService] RESEND_API_KEY no configurada, email no enviado');
            return { success: false, error: 'API key no configurada' };
        }

        // Solo enviar para alertas críticas
        if (alerta.severidad !== 'CRITICA') {
            return { success: true, messageId: 'skipped-not-critical' };
        }

        const emails = recipients.map(r => r.email).filter(Boolean);
        if (emails.length === 0) {
            return { success: false, error: 'No hay destinatarios' };
        }

        try {
            const html = generateAlertEmailHtml(alerta);
            const subject = `🚨 Alerta Crítica: ${alerta.tipo} - ${alerta.neumatico?.numero_serie || 'Sistema'}`;

            const { data, error } = await resend.emails.send({
                from: FROM_EMAIL,
                to: emails,
                subject,
                html,
            });

            if (error) {
                console.error('[EmailService] Error enviando email:', error);
                return { success: false, error: error.message };
            }

            console.log('[EmailService] Email enviado:', data?.id);
            return { success: true, messageId: data?.id };

        } catch (error: any) {
            console.error('[EmailService] Excepción:', error);
            return { success: false, error: error.message };
        }
    },

    /**
     * Envía email de prueba
     */
    async sendTestEmail(to: string): Promise<{ success: boolean; error?: string }> {
        const resend = getResendClient();
        if (!resend) {
            return { success: false, error: 'RESEND_API_KEY no configurada' };
        }

        try {
            const { error } = await resend.emails.send({
                from: FROM_EMAIL,
                to,
                subject: '✅ GesNeu - Email de Prueba',
                html: `
                    <div style="font-family: -apple-system, sans-serif; max-width: 600px; margin: 0 auto;">
                        <h1 style="color: #10b981;">✅ Conexión Exitosa</h1>
                        <p>El sistema de notificaciones por email está configurado correctamente.</p>
                        <p style="color: #6b7280; font-size: 14px;">— Equipo GesNeu</p>
                    </div>
                `,
            });

            if (error) {
                return { success: false, error: error.message };
            }

            return { success: true };
        } catch (error: any) {
            return { success: false, error: error.message };
        }
    }
};

/**
 * Genera HTML del email de alerta
 */
function generateAlertEmailHtml(alerta: AlertaEmailData): string {
    const severityColor = {
        CRITICA: '#ef4444',
        ALTA: '#f97316',
        MEDIA: '#f59e0b',
        BAJA: '#3b82f6'
    };

    const color = severityColor[alerta.severidad] || '#6b7280';

    return `
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body style="margin: 0; padding: 0; background-color: #f3f4f6; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
        <div style="max-width: 600px; margin: 0 auto; padding: 40px 20px;">
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); border-radius: 16px 16px 0 0; padding: 32px; text-align: center;">
                <h1 style="margin: 0; color: white; font-size: 24px;">🚨 Alerta ${alerta.severidad}</h1>
            </div>
            
            <!-- Content -->
            <div style="background: white; padding: 32px; border-radius: 0 0 16px 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <!-- Tipo de Alerta -->
                <div style="background: ${color}15; border-left: 4px solid ${color}; padding: 16px; margin-bottom: 24px; border-radius: 0 8px 8px 0;">
                    <strong style="color: ${color}; font-size: 16px;">${alerta.tipo}</strong>
                </div>

                <!-- Mensaje -->
                <p style="font-size: 16px; color: #374151; line-height: 1.6; margin: 0 0 24px 0;">
                    ${alerta.mensaje}
                </p>

                <!-- Detalles -->
                ${alerta.neumatico || alerta.vehiculo ? `
                <div style="background: #f9fafb; border-radius: 12px; padding: 20px; margin-bottom: 24px;">
                    <h3 style="margin: 0 0 16px 0; color: #1f2937; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px;">Detalles</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        ${alerta.neumatico ? `
                        <tr>
                            <td style="padding: 8px 0; color: #6b7280; font-size: 14px;">Neumático</td>
                            <td style="padding: 8px 0; color: #1f2937; font-size: 14px; font-weight: 600; text-align: right; font-family: monospace;">${alerta.neumatico.numero_serie}</td>
                        </tr>
                        ${alerta.neumatico.profundidad_mm !== undefined ? `
                        <tr>
                            <td style="padding: 8px 0; color: #6b7280; font-size: 14px;">Profundidad</td>
                            <td style="padding: 8px 0; color: ${color}; font-size: 14px; font-weight: 600; text-align: right;">${alerta.neumatico.profundidad_mm} mm</td>
                        </tr>
                        ` : ''}
                        ` : ''}
                        ${alerta.vehiculo ? `
                        <tr>
                            <td style="padding: 8px 0; color: #6b7280; font-size: 14px;">Vehículo</td>
                            <td style="padding: 8px 0; color: #1f2937; font-size: 14px; font-weight: 600; text-align: right;">${alerta.vehiculo.placa}</td>
                        </tr>
                        ` : ''}
                    </table>
                </div>
                ` : ''}

                <!-- CTA Button -->
                <div style="text-align: center; margin-top: 32px;">
                    <a href="${APP_URL}/panel" style="display: inline-block; background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%); color: white; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-weight: 600; font-size: 16px;">
                        Ver en Dashboard
                    </a>
                </div>
            </div>

            <!-- Footer -->
            <div style="text-align: center; padding: 24px; color: #9ca3af; font-size: 12px;">
                <p style="margin: 0 0 8px 0;">Este email fue enviado automáticamente por GesNeu</p>
                <p style="margin: 0;">Sistema de Gestión de Neumáticos</p>
            </div>
        </div>
    </body>
    </html>
    `;
}
