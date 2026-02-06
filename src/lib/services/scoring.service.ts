
import { PrismaClient } from '@prisma/client';
import { prisma } from '@/lib/prisma';

export type ScoringResult = {
    score: number; // 0-100
    recommendation: 'APTO_REENCAUCHE' | 'EVALUAR_MANUAL' | 'DESECHO';
    factors: {
        brand_tier: string;
        age_penalty: number;
        retread_penalty: number;
        condition_penalty: number;
    };
    max_retreads_allowed: number;
};

export class ScoringService {
    /**
     * Evalúa si una carcasa es apta para reencauche
     */
    static async calculateScasingScore(neumaticoId: string): Promise<ScoringResult> {
        const neumatico = await prisma.neumatico.findUnique({
            where: { id: neumaticoId },
            include: { modelo: { include: { fabricante: true } } }
        });

        if (!neumatico) throw new Error('Neumático no encontrado');

        let score = 100;
        const reencauches = neumatico.reencauches_realizados;
        const fechaCompra = neumatico.fecha_compra;
        const marca = neumatico.modelo.fabricante.nombre.toUpperCase();

        // 1. Brand Tier Logic (Simplificada para MVP)
        // Premium: Michelin, Bridgestone, Goodyear, Continental (Soportan 3 reencauches)
        // Budget: Cualquiera que no sea premium (Soportan 1 reencauche)
        const premiumBrands = ['MICHELIN', 'BRIDGESTONE', 'GOODYEAR', 'CONTINENTAL', 'DUNLOP', 'PIRELLI'];
        const isPremium = premiumBrands.some(pb => marca.includes(pb));
        const tier = isPremium ? 'PREMIUM' : 'STANDARD';
        const maxRetreads = isPremium ? 3 : 1;

        // 2. Penalidad por Reencauches Previos
        let retreadPenalty = 0;
        if (reencauches >= maxRetreads) {
            retreadPenalty = 100; // Automatic kill
        } else {
            retreadPenalty = reencauches * (isPremium ? 20 : 40);
        }
        score -= retreadPenalty;

        // 3. Penalidad por Edad (> 5 años es crítico)
        const yearsOld = (new Date().getTime() - new Date(fechaCompra).getTime()) / (1000 * 60 * 60 * 24 * 365);
        let agePenalty = 0;
        if (yearsOld > 5) {
            agePenalty = 50; // Heavy penalty
        } else if (yearsOld > 3) {
            agePenalty = 20;
        }
        score -= agePenalty;

        // 4. Penalidad por Kilometraje (Heurística)
        // Asumimos 150k km por vida aprox para TRACTO.
        // Si tiene muchos km para sus vidas, sospechoso. (No implementado en MVP v1, se asume cubierto por estado visual que sería manual)

        // Recomendación Final
        let recommendation: ScoringResult['recommendation'] = 'APTO_REENCAUCHE';

        if (score <= 40 || reencauches >= maxRetreads) {
            recommendation = 'DESECHO';
        } else if (score < 70) {
            recommendation = 'EVALUAR_MANUAL';
        }

        return {
            score: Math.max(0, score),
            recommendation,
            factors: {
                brand_tier: tier,
                age_penalty: agePenalty,
                retread_penalty: retreadPenalty,
                condition_penalty: 0 // Placeholder para futura inspección visual
            },
            max_retreads_allowed: maxRetreads
        };
    }
}
