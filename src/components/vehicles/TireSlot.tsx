'use client';

import { useState } from 'react';

type TireState = 'OK' | 'WARNING' | 'CRITICAL' | 'EMPTY';

interface TireData {
    id: string;
    numero_serie: string;
    modelo: string;
    medida: string;
    profundidad_mm: number | null;
    profundidad_porcentaje: number;
    presion_psi: number | null;
    es_reencauchado: boolean;
    km_acumulado: number;
}

interface TireSlotProps {
    posicionId: string;
    numeroPositicion: number;
    lado: 'IZQUIERDO' | 'DERECHO';
    estado: TireState;
    neumatico: TireData | null;
    permiteReencauchado: boolean;
    onClick?: (posicionId: string) => void;
}

const stateStyles: Record<TireState, { bg: string; border: string; glow: string; animation: string }> = {
    OK: {
        bg: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
        border: '#10b981',
        glow: '0 0 20px rgba(16, 185, 129, 0.4)',
        animation: ''
    },
    WARNING: {
        bg: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
        border: '#f59e0b',
        glow: '0 0 20px rgba(245, 158, 11, 0.5)',
        animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite'
    },
    CRITICAL: {
        bg: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
        border: '#ef4444',
        glow: '0 0 25px rgba(239, 68, 68, 0.6)',
        animation: 'shake 0.5s ease-in-out infinite'
    },
    EMPTY: {
        bg: 'transparent',
        border: '#6b7280',
        glow: 'none',
        animation: ''
    }
};

export function TireSlot({
    posicionId,
    numeroPositicion,
    lado,
    estado,
    neumatico,
    permiteReencauchado,
    onClick
}: TireSlotProps) {
    const [showTooltip, setShowTooltip] = useState(false);
    const style = stateStyles[estado];

    return (
        <div
            className="tire-slot-container"
            onMouseEnter={() => setShowTooltip(true)}
            onMouseLeave={() => setShowTooltip(false)}
            onClick={() => onClick?.(posicionId)}
        >
            <div
                className={`tire-slot ${estado === 'EMPTY' ? 'empty' : ''}`}
                style={{
                    background: style.bg,
                    borderColor: style.border,
                    boxShadow: style.glow,
                    animation: style.animation
                }}
            >
                {estado === 'EMPTY' ? (
                    <span className="empty-label">+</span>
                ) : (
                    <>
                        <div className="tire-icon">🔘</div>
                        {neumatico?.es_reencauchado && (
                            <span className="badge reencauchado">R</span>
                        )}
                        {estado === 'CRITICAL' && (
                            <span className="badge critical">!</span>
                        )}
                    </>
                )}
            </div>

            {/* Tooltip Premium */}
            {showTooltip && neumatico && (
                <div className="tire-tooltip">
                    <div className="tooltip-header">
                        <span className="serie">{neumatico.numero_serie}</span>
                        <span className={`status-badge ${estado.toLowerCase()}`}>{estado}</span>
                    </div>
                    <div className="tooltip-body">
                        <div className="stat">
                            <span className="label">Modelo</span>
                            <span className="value">{neumatico.modelo}</span>
                        </div>
                        <div className="stat">
                            <span className="label">Medida</span>
                            <span className="value">{neumatico.medida}</span>
                        </div>
                        <div className="stat">
                            <span className="label">Profundidad</span>
                            <span className="value">
                                {neumatico.profundidad_mm?.toFixed(1) || '—'} mm
                                <span className="percent">({neumatico.profundidad_porcentaje}%)</span>
                            </span>
                        </div>
                        <div className="stat">
                            <span className="label">Presión</span>
                            <span className="value">{neumatico.presion_psi || '—'} PSI</span>
                        </div>
                        <div className="stat">
                            <span className="label">Km</span>
                            <span className="value">{neumatico.km_acumulado?.toLocaleString() || 0}</span>
                        </div>
                    </div>
                    {neumatico.es_reencauchado && (
                        <div className="tooltip-footer">
                            <span className="reencauche-badge">♻️ Reencauchado</span>
                        </div>
                    )}
                </div>
            )}

            {/* Tooltip para posición vacía */}
            {showTooltip && !neumatico && (
                <div className="tire-tooltip empty-tooltip">
                    <p>Posición vacía</p>
                    <p className="hint">Clic para montar neumático</p>
                    {!permiteReencauchado && (
                        <p className="restriction">⚠️ No permite reencauchados</p>
                    )}
                </div>
            )}

            <style jsx>{`
                .tire-slot-container {
                    position: relative;
                    display: inline-flex;
                    flex-direction: column;
                    align-items: center;
                    cursor: pointer;
                }

                .tire-slot {
                    width: 48px;
                    height: 48px;
                    border-radius: 12px;
                    border: 3px solid;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    position: relative;
                    backdrop-filter: blur(8px);
                }

                .tire-slot:hover {
                    transform: scale(1.1);
                    z-index: 10;
                }

                .tire-slot.empty {
                    border-style: dashed;
                    opacity: 0.6;
                }

                .empty-label {
                    font-size: 24px;
                    color: #6b7280;
                    font-weight: 300;
                }

                .tire-icon {
                    font-size: 20px;
                }

                .badge {
                    position: absolute;
                    width: 16px;
                    height: 16px;
                    border-radius: 50%;
                    font-size: 10px;
                    font-weight: bold;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                }

                .badge.reencauchado {
                    top: -4px;
                    right: -4px;
                    background: #8b5cf6;
                }

                .badge.critical {
                    bottom: -4px;
                    right: -4px;
                    background: #ef4444;
                    animation: pulse 1s infinite;
                }

                .tire-tooltip {
                    position: absolute;
                    bottom: calc(100% + 12px);
                    left: 50%;
                    transform: translateX(-50%);
                    width: 200px;
                    background: rgba(15, 23, 42, 0.95);
                    backdrop-filter: blur(16px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 12px;
                    padding: 12px;
                    z-index: 100;
                    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
                }

                .tire-tooltip::after {
                    content: '';
                    position: absolute;
                    top: 100%;
                    left: 50%;
                    transform: translateX(-50%);
                    border: 8px solid transparent;
                    border-top-color: rgba(15, 23, 42, 0.95);
                }

                .tooltip-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 8px;
                    padding-bottom: 8px;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                }

                .serie {
                    font-weight: 600;
                    color: white;
                    font-size: 13px;
                    font-family: monospace;
                }

                .status-badge {
                    font-size: 10px;
                    padding: 2px 6px;
                    border-radius: 4px;
                    font-weight: 600;
                }

                .status-badge.ok { background: #10b981; color: white; }
                .status-badge.warning { background: #f59e0b; color: black; }
                .status-badge.critical { background: #ef4444; color: white; }

                .tooltip-body {
                    display: flex;
                    flex-direction: column;
                    gap: 6px;
                }

                .stat {
                    display: flex;
                    justify-content: space-between;
                    font-size: 12px;
                }

                .label {
                    color: #94a3b8;
                }

                .value {
                    color: white;
                    font-weight: 500;
                }

                .percent {
                    color: #94a3b8;
                    margin-left: 4px;
                    font-size: 10px;
                }

                .tooltip-footer {
                    margin-top: 8px;
                    padding-top: 8px;
                    border-top: 1px solid rgba(255, 255, 255, 0.1);
                }

                .reencauche-badge {
                    font-size: 11px;
                    color: #a78bfa;
                }

                .empty-tooltip {
                    text-align: center;
                    width: 160px;
                }

                .empty-tooltip p {
                    margin: 4px 0;
                    color: #94a3b8;
                    font-size: 12px;
                }

                .hint {
                    color: #60a5fa !important;
                }

                .restriction {
                    color: #f59e0b !important;
                    font-size: 11px !important;
                }

                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.7; }
                }

                @keyframes shake {
                    0%, 100% { transform: translateX(0); }
                    25% { transform: translateX(-2px); }
                    75% { transform: translateX(2px); }
                }
            `}</style>
        </div>
    );
}
