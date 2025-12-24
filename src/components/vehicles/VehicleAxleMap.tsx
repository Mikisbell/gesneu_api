'use client';

import { useEffect, useState } from 'react';
import { TireSlot } from './TireSlot';

interface MontajeResponse {
    vehiculo: {
        id: string;
        placa: string;
        codigo_interno: string;
        marca: string;
        modelo: string;
        tipo: string;
    };
    ejes: {
        numero_eje: number;
        tipo_eje: 'DIRECCION' | 'TRACCION' | 'LIBRE';
        permite_reencauchados: boolean;
        posiciones: {
            id: string;
            numero_posicion: number;
            lado: 'IZQUIERDO' | 'DERECHO';
            permite_reencauchado: boolean;
            estado: 'OK' | 'WARNING' | 'CRITICAL' | 'EMPTY';
            neumatico: {
                id: string;
                numero_serie: string;
                modelo: string;
                medida: string;
                profundidad_mm: number | null;
                profundidad_porcentaje: number;
                presion_psi: number | null;
                es_reencauchado: boolean;
                km_acumulado: number;
            } | null;
        }[];
    }[];
    resumen: {
        total_posiciones: number;
        montados: number;
        vacios: number;
        criticos: number;
        warnings: number;
    };
}

interface VehicleAxleMapProps {
    vehiculoId: string;
    onSlotClick?: (posicionId: string) => void;
}

export function VehicleAxleMap({ vehiculoId, onSlotClick }: VehicleAxleMapProps) {
    const [data, setData] = useState<MontajeResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchMontaje();
    }, [vehiculoId]);

    async function fetchMontaje() {
        try {
            setLoading(true);
            const res = await fetch(`/api/v1/vehiculos/${vehiculoId}/montaje`);
            if (!res.ok) throw new Error('Error al cargar datos');
            const json = await res.json();
            setData(json.data);
        } catch (e: any) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    }

    if (loading) {
        return (
            <div className="axle-map-skeleton">
                <div className="skeleton-pulse" />
            </div>
        );
    }

    if (error || !data) {
        return (
            <div className="axle-map-error">
                <span>⚠️</span>
                <p>{error || 'Error al cargar el mapa'}</p>
            </div>
        );
    }

    const { vehiculo, ejes, resumen } = data;

    return (
        <div className="vehicle-axle-map">
            {/* Header Premium */}
            <div className="map-header">
                <div className="vehicle-info">
                    <h2 className="placa">{vehiculo.placa}</h2>
                    <span className="tipo">{vehiculo.tipo}</span>
                </div>
                <div className="vehicle-meta">
                    <span>{vehiculo.marca} {vehiculo.modelo}</span>
                    <span className="codigo">{vehiculo.codigo_interno}</span>
                </div>
            </div>

            {/* Stats Bar */}
            <div className="stats-bar">
                <div className="stat">
                    <span className="stat-value">{resumen.montados}</span>
                    <span className="stat-label">Montados</span>
                </div>
                <div className="stat">
                    <span className="stat-value empty">{resumen.vacios}</span>
                    <span className="stat-label">Vacíos</span>
                </div>
                {resumen.criticos > 0 && (
                    <div className="stat critical">
                        <span className="stat-value">{resumen.criticos}</span>
                        <span className="stat-label">Críticos</span>
                    </div>
                )}
                {resumen.warnings > 0 && (
                    <div className="stat warning">
                        <span className="stat-value">{resumen.warnings}</span>
                        <span className="stat-label">Alertas</span>
                    </div>
                )}
            </div>

            {/* Cabina Visual */}
            <div className="vehicle-body">
                <div className="cabin">
                    <div className="cabin-icon">🚛</div>
                    <span>CABINA</span>
                </div>

                {/* Ejes */}
                <div className="axles">
                    {ejes.map((eje, idx) => {
                        const izquierdas = eje.posiciones.filter(p => p.lado === 'IZQUIERDO');
                        const derechas = eje.posiciones.filter(p => p.lado === 'DERECHO');

                        return (
                            <div key={eje.numero_eje} className="axle-row">
                                {/* Lado Izquierdo */}
                                <div className="axle-side left">
                                    {izquierdas.map(pos => (
                                        <TireSlot
                                            key={pos.id}
                                            posicionId={pos.id}
                                            numeroPositicion={pos.numero_posicion}
                                            lado={pos.lado}
                                            estado={pos.estado}
                                            neumatico={pos.neumatico}
                                            permiteReencauchado={pos.permite_reencauchado}
                                            onClick={onSlotClick}
                                        />
                                    ))}
                                </div>

                                {/* Info del Eje */}
                                <div className="axle-center">
                                    <div className="axle-line" />
                                    <span className="axle-label">
                                        {eje.tipo_eje === 'DIRECCION' ? '🔵 Dirección' :
                                            eje.tipo_eje === 'TRACCION' ? '🟢 Tracción' : '⚪ Libre'}
                                    </span>
                                    {!eje.permite_reencauchados && (
                                        <span className="axle-restriction">⚠️ No reencauches</span>
                                    )}
                                </div>

                                {/* Lado Derecho */}
                                <div className="axle-side right">
                                    {derechas.map(pos => (
                                        <TireSlot
                                            key={pos.id}
                                            posicionId={pos.id}
                                            numeroPositicion={pos.numero_posicion}
                                            lado={pos.lado}
                                            estado={pos.estado}
                                            neumatico={pos.neumatico}
                                            permiteReencauchado={pos.permite_reencauchado}
                                            onClick={onSlotClick}
                                        />
                                    ))}
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Leyenda */}
            <div className="legend">
                <div className="legend-item">
                    <span className="dot ok" />
                    <span>OK</span>
                </div>
                <div className="legend-item">
                    <span className="dot warning" />
                    <span>Advertencia</span>
                </div>
                <div className="legend-item">
                    <span className="dot critical" />
                    <span>Crítico</span>
                </div>
                <div className="legend-item">
                    <span className="dot empty" />
                    <span>Vacío</span>
                </div>
            </div>

            <style jsx>{`
                .vehicle-axle-map {
                    background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.9) 100%);
                    backdrop-filter: blur(20px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 24px;
                    padding: 24px;
                    color: white;
                    font-family: 'Inter', -apple-system, sans-serif;
                    max-width: 600px;
                    margin: 0 auto;
                }

                .map-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-start;
                    margin-bottom: 20px;
                }

                .vehicle-info {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }

                .placa {
                    font-size: 28px;
                    font-weight: 700;
                    margin: 0;
                    background: linear-gradient(135deg, #60a5fa, #a78bfa);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                }

                .tipo {
                    background: rgba(255, 255, 255, 0.1);
                    padding: 4px 10px;
                    border-radius: 20px;
                    font-size: 12px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }

                .vehicle-meta {
                    text-align: right;
                    font-size: 13px;
                    color: #94a3b8;
                    display: flex;
                    flex-direction: column;
                    gap: 4px;
                }

                .codigo {
                    font-family: monospace;
                    color: #60a5fa;
                }

                .stats-bar {
                    display: flex;
                    gap: 16px;
                    padding: 16px;
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 12px;
                    margin-bottom: 24px;
                }

                .stat {
                    text-align: center;
                    flex: 1;
                }

                .stat-value {
                    font-size: 24px;
                    font-weight: 700;
                    display: block;
                }

                .stat-value.empty { color: #6b7280; }
                .stat.critical .stat-value { color: #ef4444; }
                .stat.warning .stat-value { color: #f59e0b; }

                .stat-label {
                    font-size: 11px;
                    color: #94a3b8;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }

                .vehicle-body {
                    position: relative;
                }

                .cabin {
                    background: linear-gradient(180deg, rgba(59, 130, 246, 0.2) 0%, transparent 100%);
                    border: 2px solid rgba(59, 130, 246, 0.3);
                    border-radius: 16px 16px 0 0;
                    padding: 20px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    gap: 8px;
                }

                .cabin-icon {
                    font-size: 40px;
                }

                .cabin span {
                    font-size: 11px;
                    color: #60a5fa;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }

                .axles {
                    display: flex;
                    flex-direction: column;
                    gap: 24px;
                    padding: 24px 0;
                }

                .axle-row {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 0;
                }

                .axle-side {
                    display: flex;
                    gap: 8px;
                }

                .axle-side.left {
                    justify-content: flex-end;
                    min-width: 120px;
                }

                .axle-side.right {
                    justify-content: flex-start;
                    min-width: 120px;
                }

                .axle-center {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    min-width: 140px;
                    position: relative;
                }

                .axle-line {
                    width: 100%;
                    height: 4px;
                    background: linear-gradient(90deg, transparent, #475569, #475569, transparent);
                    border-radius: 2px;
                }

                .axle-label {
                    margin-top: 8px;
                    font-size: 11px;
                    color: #94a3b8;
                }

                .axle-restriction {
                    font-size: 10px;
                    color: #f59e0b;
                    margin-top: 4px;
                }

                .legend {
                    display: flex;
                    justify-content: center;
                    gap: 20px;
                    margin-top: 24px;
                    padding-top: 16px;
                    border-top: 1px solid rgba(255, 255, 255, 0.1);
                }

                .legend-item {
                    display: flex;
                    align-items: center;
                    gap: 6px;
                    font-size: 12px;
                    color: #94a3b8;
                }

                .dot {
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                }

                .dot.ok { background: #10b981; }
                .dot.warning { background: #f59e0b; }
                .dot.critical { background: #ef4444; }
                .dot.empty { 
                    background: transparent; 
                    border: 2px dashed #6b7280;
                }

                .axle-map-skeleton,
                .axle-map-error {
                    background: rgba(15, 23, 42, 0.9);
                    border-radius: 24px;
                    padding: 48px;
                    text-align: center;
                    color: #94a3b8;
                }

                .skeleton-pulse {
                    width: 200px;
                    height: 200px;
                    margin: 0 auto;
                    background: linear-gradient(90deg, #1e293b 25%, #334155 50%, #1e293b 75%);
                    background-size: 200% 100%;
                    animation: shimmer 1.5s infinite;
                    border-radius: 16px;
                }

                @keyframes shimmer {
                    0% { background-position: 200% 0; }
                    100% { background-position: -200% 0; }
                }

                .axle-map-error span {
                    font-size: 48px;
                    display: block;
                    margin-bottom: 12px;
                }

                @media (max-width: 640px) {
                    .vehicle-axle-map {
                        padding: 16px;
                        border-radius: 16px;
                    }

                    .map-header {
                        flex-direction: column;
                        gap: 12px;
                    }

                    .vehicle-meta {
                        text-align: left;
                    }

                    .axle-center {
                        min-width: 80px;
                    }

                    .axle-side {
                        min-width: 80px;
                    }

                    .legend {
                        flex-wrap: wrap;
                        gap: 12px;
                    }
                }
            `}</style>
        </div>
    );
}
