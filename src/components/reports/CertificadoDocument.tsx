import { Document, Page, Text, View, StyleSheet } from '@react-pdf/renderer';
import React from 'react';

const styles = StyleSheet.create({
    page: { padding: 30, fontFamily: 'Helvetica' },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: 20,
        borderBottomWidth: 1,
        borderBottomColor: '#ccc',
        paddingBottom: 10,
    },
    title: { fontSize: 22, fontWeight: 'bold', color: '#1e293b' },
    subtitle: { fontSize: 10, color: '#64748b' },
    folioBox: { alignItems: 'flex-end' },
    folioLabel: { fontSize: 8, color: '#64748b' },
    folioValue: { fontSize: 14, fontWeight: 'bold', color: '#1e293b' },
    row: { flexDirection: 'row', marginBottom: 5 },
    label: { width: 110, fontSize: 10, fontWeight: 'bold' },
    value: { fontSize: 10, flex: 1 },
    sectionTitle: {
        fontSize: 13,
        fontWeight: 'bold',
        marginBottom: 10,
        marginTop: 10,
        backgroundColor: '#f1f5f9',
        padding: 5,
    },
    resultadoBox: {
        marginTop: 10,
        marginBottom: 15,
        padding: 10,
        borderRadius: 4,
        alignItems: 'center',
    },
    resultadoText: { fontSize: 18, fontWeight: 'bold' },
    razonesBox: { marginTop: 8, paddingLeft: 10 },
    razon: { fontSize: 9, color: '#64748b', marginBottom: 2 },
    table: {
        width: 'auto',
        borderStyle: 'solid',
        borderWidth: 1,
        borderRightWidth: 0,
        borderBottomWidth: 0,
        marginTop: 10,
    },
    tableRow: { flexDirection: 'row' },
    tableColPos: {
        width: '10%',
        borderStyle: 'solid',
        borderWidth: 1,
        borderLeftWidth: 0,
        borderTopWidth: 0,
    },
    tableColNeum: {
        width: '35%',
        borderStyle: 'solid',
        borderWidth: 1,
        borderLeftWidth: 0,
        borderTopWidth: 0,
    },
    tableColMed: {
        width: '20%',
        borderStyle: 'solid',
        borderWidth: 1,
        borderLeftWidth: 0,
        borderTopWidth: 0,
    },
    tableColEstado: {
        width: '15%',
        borderStyle: 'solid',
        borderWidth: 1,
        borderLeftWidth: 0,
        borderTopWidth: 0,
    },
    tableCell: { marginTop: 4, marginBottom: 4, marginLeft: 4, fontSize: 9 },
    tableHeader: { fontWeight: 'bold', backgroundColor: '#f1f5f9' },
});

// Mapeo de estado a color (consistente con convención web)
const ESTADO_COLORS: Record<string, string> = {
    APTO: '#15803d', // green-700
    CONDICIONAL: '#b45309', // amber-700
    NO_APTO: '#b91c1c', // red-700
};

const ESTADO_BG_COLORS: Record<string, string> = {
    APTO: '#dcfce7', // green-100
    CONDICIONAL: '#fef3c7', // amber-100
    NO_APTO: '#fee2e2', // red-100
};

const ESTADO_LABELS: Record<string, string> = {
    APTO: 'APTO',
    CONDICIONAL: 'CONDICIONAL',
    NO_APTO: 'NO APTO',
};

export interface CertificadoProps {
    folio: number;
    fechaEmision: string;
    vehiculo: {
        placa: string;
        tipo: string;
        marca: string;
        modelo: string;
        kilometraje: number;
    };
    inspeccion: {
        fecha: string | null;
        inspector: string;
    };
    resultado: {
        estado: 'APTO' | 'CONDICIONAL' | 'NO_APTO';
        razones: string[];
    };
    neumaticos: Array<{
        posicion: string;
        marca: string;
        modelo: string;
        presion_psi: number;
        profundidad_mm: number;
        estado: 'APTO' | 'CONDICIONAL' | 'NO_APTO';
    }>;
}

const formatFolio = (folio: number): string =>
    `N° ${folio.toString().padStart(6, '0')}`;

export const CertificadoOperatividadDocument = ({
    folio,
    fechaEmision,
    vehiculo,
    inspeccion,
    resultado,
    neumaticos,
}: CertificadoProps) => (
    <Document>
        <Page size="A4" style={styles.page}>
            {/* Header */}
            <View style={styles.header}>
                <View>
                    <Text style={styles.title}>CERTIFICADO DE OPERATIVIDAD</Text>
                    <Text style={styles.subtitle}>
                        GesNeu Logistics — Control de Flota de Neumáticos
                    </Text>
                </View>
                <View style={styles.folioBox}>
                    <Text style={styles.folioLabel}>FOLIO</Text>
                    <Text style={styles.folioValue}>{formatFolio(folio)}</Text>
                    <Text style={{ fontSize: 9, marginTop: 4 }}>
                        Emitido: {fechaEmision}
                    </Text>
                </View>
            </View>

            {/* Información del Vehículo */}
            <Text style={styles.sectionTitle}>Información del Vehículo</Text>
            <View style={styles.row}>
                <Text style={styles.label}>Placa:</Text>
                <Text style={styles.value}>{vehiculo.placa}</Text>
            </View>
            <View style={styles.row}>
                <Text style={styles.label}>Tipo:</Text>
                <Text style={styles.value}>{vehiculo.tipo}</Text>
            </View>
            <View style={styles.row}>
                <Text style={styles.label}>Marca / Modelo:</Text>
                <Text style={styles.value}>
                    {vehiculo.marca} — {vehiculo.modelo}
                </Text>
            </View>
            <View style={styles.row}>
                <Text style={styles.label}>Odómetro:</Text>
                <Text style={styles.value}>
                    {vehiculo.kilometraje.toLocaleString()} km
                </Text>
            </View>

            {/* Inspección */}
            <Text style={styles.sectionTitle}>Última Inspección</Text>
            <View style={styles.row}>
                <Text style={styles.label}>Fecha Inspección:</Text>
                <Text style={styles.value}>
                    {inspeccion.fecha ?? 'Sin inspección previa registrada'}
                </Text>
            </View>
            <View style={styles.row}>
                <Text style={styles.label}>Inspector:</Text>
                <Text style={styles.value}>{inspeccion.inspector}</Text>
            </View>

            {/* Resultado Global */}
            <View
                style={[
                    styles.resultadoBox,
                    { backgroundColor: ESTADO_BG_COLORS[resultado.estado] },
                ]}
            >
                <Text
                    style={[
                        styles.resultadoText,
                        { color: ESTADO_COLORS[resultado.estado] },
                    ]}
                >
                    RESULTADO: {ESTADO_LABELS[resultado.estado]}
                </Text>
            </View>

            {/* Razones del resultado */}
            {resultado.razones.length > 0 && (
                <View style={styles.razonesBox}>
                    {resultado.razones.map((razon, idx) => (
                        <Text key={idx} style={styles.razon}>
                            • {razon}
                        </Text>
                    ))}
                </View>
            )}

            {/* Tabla Neumáticos */}
            <Text style={styles.sectionTitle}>
                Estado de Neumáticos Instalados
            </Text>
            <View style={styles.table}>
                <View style={styles.tableRow}>
                    <View style={styles.tableColPos}>
                        <Text style={[styles.tableCell, styles.tableHeader]}>
                            Pos.
                        </Text>
                    </View>
                    <View style={styles.tableColNeum}>
                        <Text style={[styles.tableCell, styles.tableHeader]}>
                            Neumático
                        </Text>
                    </View>
                    <View style={styles.tableColMed}>
                        <Text style={[styles.tableCell, styles.tableHeader]}>
                            Presión (PSI)
                        </Text>
                    </View>
                    <View style={styles.tableColMed}>
                        <Text style={[styles.tableCell, styles.tableHeader]}>
                            Prof. (mm)
                        </Text>
                    </View>
                    <View style={styles.tableColEstado}>
                        <Text style={[styles.tableCell, styles.tableHeader]}>
                            Estado
                        </Text>
                    </View>
                </View>
                {neumaticos.map((neu, idx) => (
                    <View key={idx} style={styles.tableRow}>
                        <View style={styles.tableColPos}>
                            <Text style={styles.tableCell}>{neu.posicion}</Text>
                        </View>
                        <View style={styles.tableColNeum}>
                            <Text style={styles.tableCell}>
                                {neu.marca} {neu.modelo}
                            </Text>
                        </View>
                        <View style={styles.tableColMed}>
                            <Text style={styles.tableCell}>
                                {neu.presion_psi.toFixed(1)}
                            </Text>
                        </View>
                        <View style={styles.tableColMed}>
                            <Text style={styles.tableCell}>
                                {neu.profundidad_mm.toFixed(1)}
                            </Text>
                        </View>
                        <View style={styles.tableColEstado}>
                            <Text
                                style={[
                                    styles.tableCell,
                                    {
                                        color: ESTADO_COLORS[neu.estado],
                                        fontWeight: 'bold',
                                    },
                                ]}
                            >
                                {ESTADO_LABELS[neu.estado]}
                            </Text>
                        </View>
                    </View>
                ))}
            </View>

            {/* Footer / Firma */}
            <View style={{ marginTop: 40, alignItems: 'center' }}>
                <View
                    style={{
                        width: 200,
                        borderBottomWidth: 1,
                        borderBottomColor: 'black',
                        marginBottom: 5,
                    }}
                />
                <Text style={{ fontSize: 10 }}>Firma Supervisor de Flota</Text>
                <Text
                    style={{
                        fontSize: 8,
                        color: 'gray',
                        marginTop: 20,
                        textAlign: 'center',
                    }}
                >
                    Certificado emitido con folio único trazable. Este documento
                    refleja el estado de los neumáticos al momento de la emisión.
                </Text>
                <Text
                    style={{
                        fontSize: 7,
                        color: 'gray',
                        marginTop: 4,
                    }}
                >
                    GesNeu Logistics — Control de Flota
                </Text>
            </View>
        </Page>
    </Document>
);
