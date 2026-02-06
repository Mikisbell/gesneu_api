// Event Constants
export const ReencaucheEvents = {
    SENT: 'REENCAUCHE.SENT',
    RETURNED: 'REENCAUCHE.RETURNED'
} as const;

// Payload Types
export interface ReencaucheSentPayload {
    neumaticoId: string;
    empresaId: string;
    usuarioId: string;
}

export interface ReencaucheReturnedPayload {
    neumaticoId: string;
    empresaId: string;
    nuevoReencaucheCount: number;
    nuevaProfundidad: number;
}
