module.exports = {
    // Archivos Excel
    FILES: {
        CONTROL_MANTENIMIENTO: 'CONTROL DE MANTENIMIENTO NEUMÁTICOS_Rev. A.xlsx',
        DATA_INSPECCION: 'Data Inspección SOLTRAK - Abr24 ECOSEM.xlsx'
    },

    // Hojas importantes
    SHEETS: {
        TABLAS: 'Tablas',
        NEUMATICOS_TRACTOS: 'Neumaticos_Tractos',
        NEUMATICOS_VOLQUETE: 'Neumaticos_Volquete',
        NEUMATICOS_LINEA_AMARILLA: 'Neumaticos_Linea Amarilla'
    },

    // Mapeo de tipos de vehículo a tipo_medicion
    TIPOS_KILOMETRAJE: [
        'TRACTO',
        'VOLQUETE',
        'CAMIONETA',
        'GRUPO ELECTROGENO',
        'CAMION',
        'BUS'
    ],

    TIPOS_HOROMETRO: [
        'CARGADOR',
        'EXCAVADORA',
        'MOTONIVELADORA',
        'RODILLO',
        'RETROEXCAVADORA',
        'COMPACTADOR',
        'MINICARGADOR'
    ],

    // Configuración de importación
    DRY_RUN: false, // Cambiar a true para preview sin guardar
    BATCH_SIZE: 50, // Registros por batch

    // Almacenes por defecto a crear
    DEFAULT_ALMACENES: [
        { nombre: 'Almacén Central', tipo: 'PRINCIPAL', ubicacion: 'Huaraucaca' },
        { nombre: 'En Tránsito', tipo: 'TEMPORAL', ubicacion: 'N/A' },
        { nombre: 'Reparación Externa', tipo: 'EXTERNO', ubicacion: 'Proveedor' }
    ]
};
