# 📡 Guía de Integración | Webhooks GesNeu

GesNeu API ofrece un sistema de webhooks robusto para permitir que sistemas externos (ERP, CRM, Slack, etc.) reciban notificaciones en tiempo real sobre eventos críticos.

---

## 🚀 Configuración Inicial

1. Acceda al **Dashboard > Ajustes > Integraciones**.
2. Haga clic en **"+ Nuevo Webhook"**.
3. Complete los campos:
   - **Nombre**: Identificador amigable (ej: "SAP Connector").
   - **URL**: Endpoint HTTPS de su servidor que recibirá los POST requests.
   - **Eventos**: Seleccione los eventos a escuchar (ej: `ALERTA_CRITICAL`).
4. **Guarde el Secret Key**: Se mostrará una clave secreta (HMAC Secret). **Guárdela**, ya que se usa para verificar la autenticidad de los mensajes.

---

## 📦 Estructura del Payload

Todas las peticiones serán `POST` con `Content-Type: application/json`.

```json
{
  "id": "uuid-v4-unico-del-evento",
  "event": "ALERTA_CRITICAL",
  "created_at": "2026-01-07T12:00:00.000Z",
  "data": {
    "tipo": "PRESION_BAJA",
    "severidad": "CRITICAL",
    "mensaje": "Neumático ABC-123 tiene presión 70 PSI (mínimo: 96 PSI)",
    "neumatico": {
      "numero_serie": "ABC-123",
      "profundidad_mm": 16.5
    },
    "vehiculo": {
      "placa": "V-555",
      "codigo_interno": "T-01"
    }
  }
}
```

---

## 🔒 Seguridad (Verificación de Firma)

GesNeu firma cada petición usando **HMAC-SHA256**. Usted debe verificar esta firma para asegurarse de que el request proviene de nosotros.

### Headers Incluidos
*   `X-Webhook-Signature`: La firma HMAC en formato hexadecimal.
*   `X-Webhook-Event`: El tipo de evento (ej: `ALERTA_CRITICAL`).
*   `X-Webhook-Timestamp`: Timestamp Unix (ms).

### Algoritmo de Verificación
1. Capture el raw body del request.
2. Genere un HMAC-SHA256 usando su **Secret Key** y el raw body.
3. Compare su hash generado con el valor del header `X-Webhook-Signature`.

#### Ejemplo en Node.js (Express)

```javascript
const crypto = require('crypto');
const express = require('express');
const app = express();

// Middleware para guardar rawBody
app.use(express.json({
  verify: (req, res, buf) => { req.rawBody = buf }
}));

const WEBHOOK_SECRET = 'su_secreto_aqui';

app.post('/webhook', (req, res) => {
  const signature = req.headers['x-webhook-signature'];
  const hash = crypto
    .createHmac('sha256', WEBHOOK_SECRET)
    .update(req.rawBody)
    .digest('hex');

  if (hash !== signature) {
    return res.status(401).send('Firma inválida');
  }

  const event = req.body;
  console.log('Evento Recibido:', event.event);
  
  // Procesar evento (ej: enviar a Slack)
  
  res.status(200).send('OK'); // Responder rápido (< 5s)
});

app.listen(3000);
```

---

## ⚠️ Políticas de Reintento

Si su servidor responde con un código `>= 400` o tarda más de **10 segundos**, GesNeu reintentará la entrega con una estrategia de **Backoff Exponencial**:

1.  Intento 1: +1 minuto
2.  Intento 2: +5 minutos
3.  Intento 3: +15 minutos
4.  Intento 4: +60 minutos
5.  Intento 5: +3 horas

Después de 5 intentos fallidos, el webhook se marcará como `FAILED` y no se reintentará más.
