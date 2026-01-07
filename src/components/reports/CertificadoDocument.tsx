import { Document, Page, Text, View, StyleSheet, Image, Font } from '@react-pdf/renderer';
import React from 'react';

// Registrar fuentes si es necesario (opcional, usa standard por defecto)
// Font.register({ family: 'Roboto', src: '...' });

const styles = StyleSheet.create({
    page: { padding: 30, fontFamily: 'Helvetica' },
    header: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 20, borderBottomWidth: 1, borderBottomColor: '#ccc', paddingBottom: 10 },
    title: { fontSize: 24, fontWeight: 'bold', color: '#1e293b' },
    subtitle: { fontSize: 10, color: '#64748b' },
    section: { margin: 10, padding: 10, flexGrow: 1 },
    row: { flexDirection: 'row', marginBottom: 5 },
    label: { width: 100, fontSize: 10, fontWeight: 'bold' },
    value: { fontSize: 10 },
    table: { display: "flex", width: "auto", borderStyle: "solid", borderWidth: 1, borderRightWidth: 0, borderBottomWidth: 0, marginTop: 20 },
    tableRow: { margin: "auto", flexDirection: "row" },
    tableCol: { width: "25%", borderStyle: "solid", borderWidth: 1, borderLeftWidth: 0, borderTopWidth: 0 },
    tableCell: { margin: "auto", marginTop: 5, fontSize: 10 }
});

interface CertificadoProps {
    vehiculo: {
        placa: string;
        tipo: string;
        marca: string;
        modelo: string;
        kilometraje: number;
    };
    inspeccion: {
        fecha: string;
        inspector: string;
        resultado: string;
    };
    neumaticos: Array<{
        posicion: string;
        marca: string;
        modelo: string;
        presion: number;
        profundidad: number;
        estado: string;
    }>;
}

export const CertificadoOperatividadDocument = ({ vehiculo, inspeccion, neumaticos }: CertificadoProps) => (
    <Document>
        <Page size="A4" style={styles.page}>

            {/* Header */}
            <View style={styles.header}>
                <View>
                    <Text style={styles.title}>CERTIFICADO DE DE OPERATIVIDAD</Text>
                    <Text style={styles.subtitle}>GesNeu Logistics - Control de Flota</Text>
                </View>
                <View>
                    <Text style={{ fontSize: 10 }}>Fecha: {new Date().toLocaleDateString()}</Text>
                    <Text style={{ fontSize: 10 }}>Folio: {Math.floor(Math.random() * 100000)}</Text>
                </View>
            </View>

            {/* Vehículo Info */}
            <View style={{ marginBottom: 20 }}>
                <Text style={{ fontSize: 14, fontWeight: 'bold', marginBottom: 10, backgroundColor: '#f1f5f9', padding: 5 }}>Información del Vehículo</Text>
                <View style={styles.row}><Text style={styles.label}>Placa:</Text><Text style={styles.value}>{vehiculo.placa}</Text></View>
                <View style={styles.row}><Text style={styles.label}>Tipo:</Text><Text style={styles.value}>{vehiculo.tipo}</Text></View>
                <View style={styles.row}><Text style={styles.label}>Marca/Modelo:</Text><Text style={styles.value}>{vehiculo.marca} - {vehiculo.modelo}</Text></View>
                <View style={styles.row}><Text style={styles.label}>Odómetro:</Text><Text style={styles.value}>{vehiculo.kilometraje} Km</Text></View>
            </View>

            {/* Inspección Info */}
            <View style={{ marginBottom: 20 }}>
                <Text style={{ fontSize: 14, fontWeight: 'bold', marginBottom: 10, backgroundColor: '#f1f5f9', padding: 5 }}>Detalle de Inspección</Text>
                <View style={styles.row}><Text style={styles.label}>Fecha Inspección:</Text><Text style={styles.value}>{inspeccion.fecha}</Text></View>
                <View style={styles.row}><Text style={styles.label}>Inspector:</Text><Text style={styles.value}>{inspeccion.inspector}</Text></View>
                <View style={styles.row}><Text style={styles.label}>Resultado Global:</Text><Text style={{ ...styles.value, color: inspeccion.resultado === 'APTO' ? 'green' : 'red', fontWeight: 'bold' }}>{inspeccion.resultado}</Text></View>
            </View>

            {/* Tabla Neumáticos */}
            <Text style={{ fontSize: 14, fontWeight: 'bold', marginTop: 10 }}>Estado de Neumáticos</Text>
            <View style={styles.table}>
                <View style={styles.tableRow}>
                    <View style={styles.tableCol}><Text style={{ ...styles.tableCell, fontWeight: 'bold' }}>Posición</Text></View>
                    <View style={styles.tableCol}><Text style={{ ...styles.tableCell, fontWeight: 'bold' }}>Neumático</Text></View>
                    <View style={styles.tableCol}><Text style={{ ...styles.tableCell, fontWeight: 'bold' }}>Presión (PSI)</Text></View>
                    <View style={styles.tableCol}><Text style={{ ...styles.tableCell, fontWeight: 'bold' }}>Condición</Text></View>
                </View>
                {neumaticos.map((neu, idx) => (
                    <View key={idx} style={styles.tableRow}>
                        <View style={styles.tableCol}><Text style={styles.tableCell}>{neu.posicion}</Text></View>
                        <View style={styles.tableCol}><Text style={styles.tableCell}>{neu.marca} {neu.modelo}</Text></View>
                        <View style={styles.tableCol}><Text style={styles.tableCell}>{neu.presion}</Text></View>
                        <View style={styles.tableCol}><Text style={{ ...styles.tableCell, color: neu.estado === 'CRITICO' ? 'red' : 'black' }}>{neu.estado}</Text></View>
                    </View>
                ))}
            </View>

            {/* Footer / Firma */}
            <View style={{ marginTop: 50, alignItems: 'center' }}>
                <View style={{ width: 200, borderBottomWidth: 1, borderBottomColor: 'black', marginBottom: 5 }}></View>
                <Text style={{ fontSize: 10 }}>Firma Supervisor de Flota</Text>
                <Text style={{ fontSize: 8, color: 'gray', marginTop: 20 }}>Este documento es un reporte técnico generado por GesNeu Logistics.</Text>
            </View>

        </Page>
    </Document>
);
