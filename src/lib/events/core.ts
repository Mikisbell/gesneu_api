import { EventEmitter } from 'events';

// Generic Event Definition
export interface DomainEvent<T = any> {
    name: string;
    payload: T;
    timestamp: Date;
}

// Type-Safe Event Handler
export type EventHandler<T = any> = (event: DomainEvent<T>) => Promise<void> | void;

class TypedEventBus extends EventEmitter {
    constructor() {
        super();
        this.setMaxListeners(20); // Avoid leaks warnings
    }

    /**
     * Publish an event.
     * We await all listeners to ensure side-effects (like cache invalidation) 
     * complete before the HTTP response is sent (Critical for Serverless).
     */
    async publish<T>(eventName: string, payload: T) {
        const event: DomainEvent<T> = {
            name: eventName,
            payload,
            timestamp: new Date()
        };

        const listeners = this.listeners(eventName) as Function[];

        // Execute all listeners in parallel
        await Promise.all(
            listeners.map(listener => {
                try {
                    return listener(event);
                } catch (error) {
                    console.error(`[EventBus] Error in listener for ${eventName}:`, error);
                    return Promise.resolve();
                }
            })
        );
    }

    /**
     * Subscribe to an event
     */
    subscribe<T>(eventName: string, handler: EventHandler<T>) {
        this.on(eventName, handler);
        return () => this.off(eventName, handler); // Return unsubscribe function
    }
}

export const EventBus = new TypedEventBus();
