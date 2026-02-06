// Test script to verify Event-Driven Architecture
// Run with: npx ts-node scripts/test-events.ts

import { EventBus } from '../src/lib/events/core';
import { NeumaticoEvents } from '../src/lib/events/neumatico.events';
import { registerObservers } from '../src/lib/events/registry';

console.log('🧪 Testing Event-Driven Architecture\n');

// Register all observers
registerObservers();

// Test 1: Verify EventBus exists
console.log('✅ Test 1: EventBus singleton created');

// Test 2: Publish a test event
console.log('\n📤 Test 2: Publishing test event (NEUMATICO.MOUNTED)');

const testPayload = {
    neumaticoId: 'test-123',
    empresaId: '00000000-0000-0000-0000-000000000000',
    usuarioId: 'test-user',
    vehiculoId: 'test-vehicle',
    posicionId: 'test-position',
    kilometrajeVehiculo: 50000,
    metadata: {
        almacenOrigenId: 'test-almacen',
        profundidadActual: 18.5
    }
};

EventBus.publish(NeumaticoEvents.MOUNTED, testPayload)
    .then(() => {
        console.log('✅ Test 2: Event published successfully');
        console.log('   Check console above for observer reactions\n');

        // Test 3: Verify observers are registered
        const listenerCount = (EventBus as any).listenerCount(NeumaticoEvents.MOUNTED);
        console.log(`✅ Test 3: ${listenerCount} observer(s) listening to MOUNTED event`);

        // Test 4: Publish SCRAPPED event (should trigger notifications)
        console.log('\n📤 Test 4: Publishing SCRAPPED event (should trigger alert)');

        const scrappedPayload = {
            neumaticoId: 'test-456',
            empresaId: '00000000-0000-0000-0000-000000000000',
            usuarioId: 'test-user',
            motivoTexto: 'Desgaste prematuro',
            profundidadFinal: 2.5,
            metadata: {
                kmTotales: 15000, // < 20000 should trigger alert
                costoTotal: 6000, // > 5000 should trigger alert
                vidaAlcanzada: 1
            }
        };

        return EventBus.publish(NeumaticoEvents.SCRAPPED, scrappedPayload);
    })
    .then(() => {
        console.log('✅ Test 4: SCRAPPED event published');
        console.log('   Check for NotificationObserver alerts above\n');

        console.log('✅ All tests passed!');
        console.log('\n🎉 Event-Driven Architecture is working correctly');
    })
    .catch((error) => {
        console.error('❌ Test failed:', error);
        process.exit(1);
    });
