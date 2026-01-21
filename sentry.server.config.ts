import * as Sentry from "@sentry/nextjs";

// Only initialize Sentry in production to reduce dev startup overhead
if (process.env.NODE_ENV === 'production' && process.env.SENTRY_DSN) {
    Sentry.init({
        dsn: process.env.SENTRY_DSN,
        tracesSampleRate: 1.0,
        debug: false,
    });
}
