
import { InspeccionService } from "@/lib/services/inspeccion.service";
import { prisma } from "@/lib/prisma";
import { TipoAlertaEnum, SeveridadAlertaEnum } from "@prisma/client";

// Mocks
const inspeccionService = new InspeccionService();

describe("Alertas Dinamicas de Presion", () => {
    let empresaId: string;
    let fabricanteId: string;
    let modeloId: string; // Recomendada: 100 PSI (80% = 80 PSI)
    let almacenId: string;
    let usuarioId: string;

    beforeAll(async () => {
        // Setup data
        const empresa = await prisma.empresa.create({
            data: { nombre: "Test Alertas Corp", ruc: `20${Date.now()}123456789`.substring(0, 20) }
        });
        empresaId = empresa.id;

        const usuario = await prisma.usuario.create({
            data: {
                empresa_id: empresa.id,
                username: "inspector_alertas",
                email: "alertas@test.com",
                password_hash: "hash",
                nombre_completo: "Inspector Gadget"
            }
        });
        usuarioId = usuario.id;

        const fab = await prisma.fabricanteNeumatico.create({
            data: { nombre: "Michelin Test" }
        });
        fabricanteId = fab.id;

        // Modelo con 100 PSI recomendado
        const mod = await prisma.modeloNeumatico.create({
            data: {
                fabricante_id: fab.id,
                nombre_modelo: "X Multi Z Test",
                medida: "295/80R22.5",
                profundidad_original_mm: 16.0,
                profundidad_minima_retiro_mm: 3.0,
                presion_recomendada_psi: 100.0 // Umbral alerta será 80 PSI
            }
        });
        modeloId = mod.id;

        const alm = await prisma.almacen.create({
            data: {
                empresa_id: empresa.id,
                codigo: `ALM-ALERT-${Date.now().toString().slice(-8)}`,
                nombre: "Almacen Test"
            }
        });
        almacenId = alm.id;
    });

    afterAll(async () => {
        // Cleanup robusto - only if IDs were set
        if (fabricanteId) {
            await prisma.alerta.deleteMany({ where: { neumatico: { modelo: { fabricante_id: fabricanteId } } } }).catch(() => {});
            await prisma.eventoNeumatico.deleteMany({ where: { neumatico: { modelo: { fabricante_id: fabricanteId } } } }).catch(() => {});
            await prisma.lecturaPresion.deleteMany({ where: { neumatico: { modelo: { fabricante_id: fabricanteId } } } }).catch(() => {});
            await prisma.neumatico.deleteMany({ where: { modelo: { fabricante_id: fabricanteId } } }).catch(() => {});
            await prisma.modeloNeumatico.deleteMany({ where: { fabricante_id: fabricanteId } }).catch(() => {});
            await prisma.fabricanteNeumatico.delete({ where: { id: fabricanteId } }).catch(() => {});
        }
        if (usuarioId) {
            await prisma.usuario.delete({ where: { id: usuarioId } }).catch(() => {});
        }
        if (empresaId) {
            await prisma.empresa.delete({ where: { id: empresaId } }).catch(() => {});
        }
    });

    it("Debe generar alerta CRITICAL si presion (70) < 80% de recomendada (100)", async () => {
        // 1. Crear Neumático
        const neumatico = await prisma.neumatico.create({
            data: {
                empresa_id: empresaId,
                modelo_id: modeloId,
                numero_serie: "SERIE-LOW-PRESSURE",
                fecha_compra: new Date(),
                profundidad_remanente_actual_mm: 16,
                estado_actual: "EN_STOCK",
                ubicacion_almacen_id: almacenId
            }
        });

        // 2. Registrar Inspección con 70 PSI (Umbral es 80)
        await inspeccionService.registrarManual({
            neumatico_id: neumatico.id,
            presion_psi: 70,
            temperatura_c: 25,
            observaciones: "Presión baja test"
        }, usuarioId);

        // 3. Verificar Alerta
        const alerta = await prisma.alerta.findFirst({
            where: {
                neumatico_id: neumatico.id,
                tipo: TipoAlertaEnum.PRESION_BAJA
            }
        });

        expect(alerta).toBeDefined();
        expect(alerta?.severidad).toBe(SeveridadAlertaEnum.WARNING);
        expect(alerta?.resuelta).toBeFalsy();
    });

    it("Debe generar alerta para Modelo Alta Presión (120 PSI) con lectura 90 PSI (Umbral 96)", async () => {
        // Modelo Alta Presión
        const modeloHigh = await prisma.modeloNeumatico.create({
            data: {
                fabricante_id: fabricanteId,
                nombre_modelo: "High Pressure Model",
                medida: "12R22.5",
                profundidad_original_mm: 16.0,
                profundidad_minima_retiro_mm: 3.0,
                presion_recomendada_psi: 120.0
            }
        });

        const neumaticoHigh = await prisma.neumatico.create({
            data: {
                empresa_id: empresaId,
                modelo_id: modeloHigh.id,
                numero_serie: "SERIE-HIGH-P",
                fecha_compra: new Date(),
                profundidad_remanente_actual_mm: 16,
                estado_actual: "EN_STOCK",
                ubicacion_almacen_id: almacenId
            }
        });

        // 90 PSI sería OK para el estándar de 80, pero BAJO para este modelo (Umbral 96)
        await inspeccionService.registrarManual({
            neumatico_id: neumaticoHigh.id,
            presion_psi: 90,
            temperatura_c: 25,
            observaciones: "Test Alta Presión"
        }, usuarioId);

        const alerta = await prisma.alerta.findFirst({
            where: {
                neumatico_id: neumaticoHigh.id,
                tipo: TipoAlertaEnum.PRESION_BAJA
            }
        });

        expect(alerta).toBeDefined();
        expect(alerta?.mensaje).toContain("mínimo: 96");
    });

    it("NO debe generar alerta si presion (90) > 80% de recomendada (100)", async () => {
        // 1. Crear Neumático
        const neumatico = await prisma.neumatico.create({
            data: {
                empresa_id: empresaId,
                modelo_id: modeloId,
                numero_serie: "SERIE-OK-PRESSURE",
                fecha_compra: new Date(),
                profundidad_remanente_actual_mm: 16,
                estado_actual: "EN_STOCK",
                ubicacion_almacen_id: almacenId
            }
        });

        // 2. Registrar Inspección con 90 PSI (Umbral es 80)
        await inspeccionService.registrarManual({
            neumatico_id: neumatico.id,
            presion_psi: 90,
            temperatura_c: 25,
            observaciones: "Presión normal test"
        }, usuarioId);

        // 3. Verificar Alerta Inexistente
        const alerta = await prisma.alerta.findFirst({
            where: {
                neumatico_id: neumatico.id,
                tipo: TipoAlertaEnum.PRESION_BAJA
            }
        });

        expect(alerta).toBeNull();
    });
});
