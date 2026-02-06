import { CacheObserver } from '../observers/cache.observer';
import { AlertObserver } from '../observers/alerta.observer';
import { NeumaticoUpdateObserver } from '../observers/neumatico-update.observer';
import { AuditObserver } from '../observers/audit.observer';
import { NotificationObserver } from '../observers/notification.observer';
import { AnalyticsObserver } from '../observers/analytics.observer';

let initialized = false;

export const registerObservers = () => {
    if (initialized) return;

    // Original observers (Inspections + Retread)
    CacheObserver.init();
    AlertObserver.init();
    NeumaticoUpdateObserver.init();

    // New observers (Tire Operations)
    AuditObserver.init();
    NotificationObserver.init();
    AnalyticsObserver.init();

    initialized = true;
    console.log("✅ [System] All 6 Observers Registered (Cache, Alert, Sync, Audit, Notification, Analytics)");
};
