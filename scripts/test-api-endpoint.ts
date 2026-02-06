import 'dotenv/config';

// Requires the server to be running on localhost:3005
const API_URL = 'http://localhost:3005/api/v1/neumaticos';

async function testApi() {
    console.log('🧪 Testing API Endpoint via Fetch...');

    // 1. Need a valid manufacturer and model ID. 
    // We'll fetch them first or hardcode if we know them from seed.
    // Fetching avoids hardcoding errors.

    console.log('🔍 Fetching dependencies (Fabricantes/Modelos)...');

    const [fabricantesRes, modelosRes] = await Promise.all([
        fetch('http://localhost:3005/api/v1/catalogos/fabricantes'),
        fetch('http://localhost:3005/api/v1/catalogos/modelos-neumatico')
    ]);

    if (!fabricantesRes.ok || !modelosRes.ok) {
        throw new Error('Failed to fetch dependencies. Is server running?');
    }

    const fabricantes = await fabricantesRes.json();
    const modelos = await modelosRes.json();

    const michelin = fabricantes.data.find((f: any) => f.nombre === 'Michelin');
    const modelX = modelos.data.find((m: any) => m.nombre_modelo === 'X Multi Z');

    if (!modelX) {
        throw new Error('Model X Multi Z not found. Run seed?');
    }

    console.log(`✅ Using Model: ${modelX.nombre_modelo} (ID: ${modelX.id})`);

    // 2. Prepare Payload (Exactly matching the corrected Frontend)
    const payload = {
        modelo_id: modelX.id,
        medida: modelX.medida,
        numero_serie: `API-TEST-${Date.now()}`,
        dot: '3024',
        es_reencauchado: false,

        // The critical fields we fixed:
        profundidad_inicial_mm: 20,
        profundidad_actual_mm: 20, // FIXED
        fecha_compra: new Date().toISOString(), // FIXED

        costo_compra: 450,
        moneda_compra: 'USD',

        ubicacion_almacen_id: undefined // Optional
    };

    console.log('📤 Sending POST request...');
    console.log('   Payload:', JSON.stringify(payload, null, 2));

    const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            // Mock authentication headers if needed or ensure development mode bypasses
            // Assuming NextAuth session might be needed, but dev environment might have bypass
            // or we might hit 401. Let's see. 
            // If 401, we know API is reachable at least.
        },
        body: JSON.stringify(payload)
    });

    console.log(`📥 Status: ${response.status} ${response.statusText}`);

    const data = await response.json();

    if (response.ok) {
        console.log('✅ SUCCESS! Tire created via API.');
        console.log('   Response ID:', data.data?.id);
    } else {
        console.error('❌ FAILED.');
        console.error('   Error:', data);
    }
}

testApi().catch(console.error);
