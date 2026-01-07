'use client';

import { useEffect, useState } from 'react';
import { VehicleAxleMap } from '@/components/vehicles/VehicleAxleMap';
import { InspectionModal } from '@/components/inspections/InspectionModal';

interface VehiculoSimple {
    id: string;
    placa: string;
    codigo_interno: string;
    marca: string;
    modelo: string;
}

interface SelectedTire {
    id: string;
    serial: string;
}

export default function MapaEjesPage() {
    const [vehiculos, setVehiculos] = useState<VehiculoSimple[]>([]);
    const [selectedId, setSelectedId] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);

    // Estado para modal de inspección
    const [selectedTire, setSelectedTire] = useState<SelectedTire | null>(null);
    const [isInspectionOpen, setIsInspectionOpen] = useState(false);

    useEffect(() => {
        fetchVehiculos();
    }, []);

    async function fetchVehiculos() {
        try {
            const res = await fetch('/api/v1/vehiculos?limit=20');
            const json = await res.json();
            if (json.data) {
                setVehiculos(json.data);
                if (json.data.length > 0) {
                    setSelectedId(json.data[0].id);
                }
            }
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    }

    function handleSlotClick(posicionId: string, neaumaticoId?: string, serial?: string) {
        if (neaumaticoId && serial) {
            // Si hay neumático montado, abrir modal de inspección
            setSelectedTire({ id: neaumaticoId, serial });
            setIsInspectionOpen(true);
        } else {
            // Posición vacía - lógica de montaje (futuro)
            alert(`Posición: ${posicionId}\nAquí se abriría el modal de montaje.`);
        }
    }

    return (
        <div className="mapa-ejes-page">
            <header className="page-header">
                <div className="header-content">
                    <h1>🔧 Mapa de Ejes</h1>
                    <p>Visualización interactiva del estado de neumáticos por vehículo</p>
                </div>
            </header>

            <main className="page-content">
                {/* Selector de Vehículo */}
                <div className="vehicle-selector">
                    <label>Seleccionar Vehículo</label>
                    <select
                        value={selectedId || ''}
                        onChange={(e) => setSelectedId(e.target.value)}
                        disabled={loading}
                    >
                        {loading && <option>Cargando...</option>}
                        {vehiculos.map(v => (
                            <option key={v.id} value={v.id}>
                                {v.placa} - {v.marca} {v.modelo}
                            </option>
                        ))}
                    </select>
                </div>

                {/* Mapa de Ejes */}
                {selectedId ? (
                    <VehicleAxleMap
                        vehiculoId={selectedId}
                        onSlotClick={handleSlotClick}
                    />
                ) : (
                    <div className="no-selection">
                        <span>🚛</span>
                        <p>Selecciona un vehículo para ver su mapa de ejes</p>
                    </div>
                )}

                {/* Info */}
                <div className="info-card">
                    <h3>💡 ¿Cómo usar?</h3>
                    <ul>
                        <li><strong>Hover</strong> sobre un neumático para ver detalles</li>
                        <li><strong>Click</strong> en un neumático montado para registrar inspección de presión</li>
                        <li>🟢 Verde = OK | 🟡 Amarillo = Advertencia | 🔴 Rojo = Crítico</li>
                    </ul>
                </div>
            </main>

            {/* Modal de Inspección */}
            {selectedTire && (
                <InspectionModal
                    neumaticoId={selectedTire.id}
                    serial={selectedTire.serial}
                    isOpen={isInspectionOpen}
                    onClose={() => {
                        setIsInspectionOpen(false);
                        setSelectedTire(null);
                    }}
                    onSuccess={() => {
                        // Refrescar el mapa después de registrar lectura
                        window.location.reload();
                    }}
                />
            )}

            <style jsx>{`
                .mapa-ejes-page {
                    min-height: 100vh;
                    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
                    color: white;
                }

                .page-header {
                    background: rgba(0, 0, 0, 0.3);
                    backdrop-filter: blur(10px);
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                    padding: 32px 24px;
                }

                .header-content {
                    max-width: 800px;
                    margin: 0 auto;
                }

                .page-header h1 {
                    font-size: 32px;
                    margin: 0 0 8px 0;
                    background: linear-gradient(135deg, #60a5fa, #a78bfa, #f472b6);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                }

                .page-header p {
                    margin: 0;
                    color: #94a3b8;
                    font-size: 16px;
                }

                .page-content {
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 32px 24px;
                    display: flex;
                    flex-direction: column;
                    gap: 24px;
                }

                .vehicle-selector {
                    display: flex;
                    flex-direction: column;
                    gap: 8px;
                }

                .vehicle-selector label {
                    font-size: 14px;
                    color: #94a3b8;
                    font-weight: 500;
                }

                .vehicle-selector select {
                    padding: 12px 16px;
                    border-radius: 12px;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    background: rgba(255, 255, 255, 0.05);
                    color: white;
                    font-size: 16px;
                    cursor: pointer;
                    transition: all 0.2s;
                }

                .vehicle-selector select:hover {
                    background: rgba(255, 255, 255, 0.1);
                }

                .vehicle-selector select:focus {
                    outline: none;
                    border-color: #60a5fa;
                    box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.2);
                }

                .no-selection {
                    text-align: center;
                    padding: 64px;
                    background: rgba(255, 255, 255, 0.02);
                    border: 2px dashed rgba(255, 255, 255, 0.1);
                    border-radius: 24px;
                }

                .no-selection span {
                    font-size: 64px;
                    display: block;
                    margin-bottom: 16px;
                }

                .no-selection p {
                    color: #94a3b8;
                    font-size: 16px;
                }

                .info-card {
                    background: rgba(255, 255, 255, 0.03);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 16px;
                    padding: 20px 24px;
                }

                .info-card h3 {
                    margin: 0 0 12px 0;
                    font-size: 16px;
                    color: #e2e8f0;
                }

                .info-card ul {
                    margin: 0;
                    padding-left: 20px;
                }

                .info-card li {
                    color: #94a3b8;
                    font-size: 14px;
                    margin-bottom: 8px;
                }

                .info-card strong {
                    color: #60a5fa;
                }

                @media (max-width: 640px) {
                    .page-header {
                        padding: 24px 16px;
                    }

                    .page-header h1 {
                        font-size: 24px;
                    }

                    .page-content {
                        padding: 16px;
                    }
                }
            `}</style>
        </div>
    );
}

