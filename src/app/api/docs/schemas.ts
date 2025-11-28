/**
 * @swagger
 * components:
 *   schemas:
 *     Neumatico:
 *       type: object
 *       properties:
 *         id:
 *           type: string
 *           format: uuid
 *           description: ID único del neumático
 *         numero_serie:
 *           type: string
 *           description: Número de serie del neumático
 *         modelo_id:
 *           type: string
 *           format: uuid
 *           description: ID del modelo del neumático
 *         estado_actual:
 *           type: string
 *           enum: [STOCK, MONTADO, REPARACION, REENCAUCHE, DESECHO]
 *           description: Estado actual del neumático
 *         ubicacion_almacen_id:
 *           type: string
 *           format: uuid
 *           nullable: true
 *           description: ID del almacén donde se encuentra (si está en stock)
 *         ubicacion_vehiculo_id:
 *           type: string
 *           format: uuid
 *           nullable: true
 *           description: ID del vehículo donde está montado (si está montado)
 *         posicion_montaje:
 *           type: integer
 *           nullable: true
 *           description: Posición en el vehículo (1-indexed)
 *         kilometraje_actual:
 *           type: number
 *           description: Kilometraje acumulado del neumático
 *         profundidad_actual_izquierda:
 *           type: number
 *           nullable: true
 *           description: Profundidad actual del lado izquierdo
 *         profundidad_actual_centro:
 *           type: number
 *           nullable: true
 *           description: Profundidad actual del centro
 *         profundidad_actual_derecha:
 *           type: number
 *           nullable: true
 *           description: Profundidad actual del lado derecho
 *         fecha_fabricacion:
 *           type: string
 *           format: date
 *           description: Fecha de fabricación
 *         fecha_compra:
 *           type: string
 *           format: date
 *           description: Fecha de compra
 *         proveedor_id:
 *           type: string
 *           format: uuid
 *           nullable: true
 *           description: ID del proveedor
 *         costo_compra:
 *           type: number
 *           nullable: true
 *           description: Costo de compra
 *         activo:
 *           type: boolean
 *           description: Indica si el neumático está activo en el sistema
 *         created_at:
 *           type: string
 *           format: date-time
 *           description: Fecha de creación
 *         updated_at:
 *           type: string
 *           format: date-time
 *           description: Fecha de última actualización
 *
 *     CreateNeumaticoDTO:
 *       type: object
 *       required:
 *         - numero_serie
 *         - modelo_id
 *         - estado_actual
 *         - ubicacion_almacen_id
 *       properties:
 *         numero_serie:
 *           type: string
 *         modelo_id:
 *           type: string
 *           format: uuid
 *         estado_actual:
 *           type: string
 *           enum: [STOCK, MONTADO, REPARACION, REENCAUCHE, DESECHO]
 *         ubicacion_almacen_id:
 *           type: string
 *           format: uuid
 *         dot:
 *           type: string
 *         marca_id:
 *           type: string
 *           format: uuid
 *         medida_id:
 *           type: string
 *           format: uuid
 *         diseno_id:
 *           type: string
 *           format: uuid
 *         fecha_fabricacion:
 *           type: string
 *           format: date
 *         fecha_compra:
 *           type: string
 *           format: date
 *         proveedor_id:
 *           type: string
 *           format: uuid
 *         costo_compra:
 *           type: number
 *         profundidad_inicial:
 *           type: number
 *
 *     UpdateNeumaticoDTO:
 *       type: object
 *       properties:
 *         numero_serie:
 *           type: string
 *         estado_actual:
 *           type: string
 *           enum: [STOCK, MONTADO, REPARACION, REENCAUCHE, DESECHO]
 *         ubicacion_almacen_id:
 *           type: string
 *           format: uuid
 *         ubicacion_vehiculo_id:
 *           type: string
 *           format: uuid
 *         posicion_montaje:
 *           type: integer
 *         kilometraje_actual:
 *           type: number
 *         profundidad_actual_izquierda:
 *           type: number
 *         profundidad_actual_centro:
 *           type: number
 *         profundidad_actual_derecha:
 *           type: number
 *         activo:
 *           type: boolean
 *
 *     MontajeNeumaticoDTO:
 *       type: object
 *       required:
 *         - neumatico_id
 *         - vehiculo_id
 *         - posicion_id
 *         - kilometraje_vehiculo
 *         - fecha_evento
 *       properties:
 *         neumatico_id:
 *           type: string
 *           format: uuid
 *         vehiculo_id:
 *           type: string
 *           format: uuid
 *         posicion_id:
 *           type: string
 *           format: uuid
 *         kilometraje_vehiculo:
 *           type: number
 *         presion_psi:
 *           type: number
 *         observaciones:
 *           type: string
 *         fecha_evento:
 *           type: string
 *           format: date-time
 *
 *     DesmontajeNeumaticoDTO:
 *       type: object
 *       required:
 *         - neumatico_id
 *         - destino
 *         - kilometraje_vehiculo
 *         - fecha_evento
 *       properties:
 *         neumatico_id:
 *           type: string
 *           format: uuid
 *         destino:
 *           type: string
 *           enum: [STOCK, REPARACION, REENCAUCHE, DESECHO]
 *         kilometraje_vehiculo:
 *           type: number
 *         almacen_destino_id:
 *           type: string
 *           format: uuid
 *           description: Requerido si destino es STOCK
 *         motivo_id:
 *           type: string
 *           format: uuid
 *           description: Requerido si destino es DESECHO
 *         profundidad_remanente_mm:
 *           type: number
 *         presion_psi:
 *           type: number
 *         observaciones:
 *           type: string
 *         fecha_evento:
 *           type: string
 *           format: date-time
 *
 *     MovimientoRotacion:
 *       type: object
 *       required:
 *         - neumatico_id
 *         - posicion_destino_id
 *       properties:
 *         neumatico_id:
 *           type: string
 *           format: uuid
 *         posicion_destino_id:
 *           type: string
 *           format: uuid
 *
 *     RotacionNeumaticoDTO:
 *       type: object
 *       required:
 *         - vehiculo_id
 *         - kilometraje_vehiculo
 *         - movimientos
 *       properties:
 *         vehiculo_id:
 *           type: string
 *           format: uuid
 *         kilometraje_vehiculo:
 *           type: number
 *         movimientos:
 *           type: array
 *           items:
 *             $ref: '#/components/schemas/MovimientoRotacion'
 *         observaciones:
 *           type: string
 *
 *     Vehiculo:
 *       type: object
 *       properties:
 *         id:
 *           type: string
 *           format: uuid
 *         placa:
 *           type: string
 *         marca:
 *           type: string
 *         modelo:
 *           type: string
 *         anio:
 *           type: integer
 *         tipo_vehiculo_id:
 *           type: string
 *           format: uuid
 *         kilometraje_actual:
 *           type: number
 *         activo:
 *           type: boolean
 *         created_at:
 *           type: string
 *           format: date-time
 *         updated_at:
 *           type: string
 *           format: date-time
 *
 *     CreateVehiculoDTO:
 *       type: object
 *       required:
 *         - placa
 *         - marca
 *         - modelo
 *         - anio
 *         - tipo_vehiculo_id
 *       properties:
 *         placa:
 *           type: string
 *         marca:
 *           type: string
 *         modelo:
 *           type: string
 *         anio:
 *           type: integer
 *         tipo_vehiculo_id:
 *           type: string
 *           format: uuid
 *         kilometraje_actual:
 *           type: number
 *
 *     UpdateVehiculoDTO:
 *       type: object
 *       properties:
 *         placa:
 *           type: string
 *         marca:
 *           type: string
 *         modelo:
 *           type: string
 *         anio:
 *           type: integer
 *         tipo_vehiculo_id:
 *           type: string
 *           format: uuid
 *         kilometraje_actual:
 *           type: number
 *         activo:
 *           type: boolean
 *
 *     Almacen:
 *       type: object
 *       properties:
 *         id:
 *           type: string
 *           format: uuid
 *         nombre:
 *           type: string
 *         codigo:
 *           type: string
 *         descripcion:
 *           type: string
 *         ubicacion:
 *           type: string
 *         activo:
 *           type: boolean
 *         created_at:
 *           type: string
 *           format: date-time
 *         updated_at:
 *           type: string
 *           format: date-time
 *
 *     CreateAlmacenDTO:
 *       type: object
 *       required:
 *         - nombre
 *         - codigo
 *       properties:
 *         nombre:
 *           type: string
 *         codigo:
 *           type: string
 *         descripcion:
 *           type: string
 *         ubicacion:
 *           type: string
 *         activo:
 *           type: boolean
 *
 *     UpdateAlmacenDTO:
 *       type: object
 *       properties:
 *         nombre:
 *           type: string
 *         ubicacion:
 *           type: string
 *         activo:
 *           type: boolean
 *
 *     Proveedor:
 *       type: object
 *       properties:
 *         id:
 *           type: string
 *           format: uuid
 *         tipo:
 *           type: string
 *           enum: [FABRICANTE, DISTRIBUIDOR, TALLER, OTRO]
 *         nombre:
 *           type: string
 *         ruc:
 *           type: string
 *         contacto_principal:
 *           type: string
 *         telefono:
 *           type: string
 *         email:
 *           type: string
 *         direccion:
 *           type: string
 *         activo:
 *           type: boolean
 *         created_at:
 *           type: string
 *           format: date-time
 *         updated_at:
 *           type: string
 *           format: date-time
 *
 *     CreateProveedorDTO:
 *       type: object
 *       required:
 *         - nombre
 *         - tipo
 *       properties:
 *         tipo:
 *           type: string
 *           enum: [FABRICANTE, DISTRIBUIDOR, TALLER, OTRO]
 *         nombre:
 *           type: string
 *         ruc:
 *           type: string
 *         contacto_principal:
 *           type: string
 *         telefono:
 *           type: string
 *         email:
 *           type: string
 *         direccion:
 *           type: string
 *         activo:
 *           type: boolean
 *
 *     UpdateProveedorDTO:
 *       type: object
 *       properties:
 *         tipo:
 *           type: string
 *           enum: [FABRICANTE, DISTRIBUIDOR, TALLER, OTRO]
 *         nombre:
 *           type: string
 *         ruc:
 *           type: string
 *         contacto_principal:
 *           type: string
 *         telefono:
 *           type: string
 *         email:
 *           type: string
 *         direccion:
 *           type: string
 *         activo:
 *           type: boolean
 */
export { }

/**
 * @swagger
 * components:
 *   schemas:
 *     Usuario:
 *       type: object
 *       properties:
 *         id:
 *           type: string
 *           format: uuid
 *         username:
 *           type: string
 *         nombre_completo:
 *           type: string
 *         email:
 *           type: string
 *           format: email
 *         ultimo_login:
 *           type: string
 *           format: date-time
 *           nullable: true
 *         activo:
 *           type: boolean
 *         creado_en:
 *           type: string
 *           format: date-time
 *         roles:
 *           type: array
 *           items:
 *             type: object
 *             properties:
 *               rol:
 *                 type: object
 *                 properties:
 *                   id:
 *                     type: string
 *                     format: uuid
 *                   nombre:
 *                     type: string
 *
 *     CreateUsuarioDTO:
 *       type: object
 *       required:
 *         - username
 *         - nombre_completo
 *         - email
 *         - password
 *         - roles
 *       properties:
 *         username:
 *           type: string
 *           minLength: 3
 *           maxLength: 50
 *         nombre_completo:
 *           type: string
 *           minLength: 3
 *           maxLength: 200
 *         email:
 *           type: string
 *           format: email
 *           maxLength: 100
 *         password:
 *           type: string
 *           minLength: 6
 *         roles:
 *           type: array
 *           items:
 *             type: string
 *             format: uuid
 *           minItems: 1
 *
 *     UpdateUsuarioDTO:
 *       type: object
 *       properties:
 *         nombre_completo:
 *           type: string
 *           minLength: 3
 *           maxLength: 200
 *         email:
 *           type: string
 *           format: email
 *           maxLength: 100
 *         password:
 *           type: string
 *           minLength: 6
 *         roles:
 *           type: array
 *           items:
 *             type: string
 *             format: uuid
 *         activo:
 *           type: boolean
 */

/**
 * @swagger
 * components:
 *   schemas:
 *     InspeccionNeumaticoDTO:
 *       type: object
 *       required:
 *         - neumatico_id
 *       properties:
 *         neumatico_id:
 *           type: string
 *           format: uuid
 *         profundidad_izquierda_mm:
 *           type: number
 *         profundidad_centro_mm:
 *           type: number
 *         profundidad_derecha_mm:
 *           type: number
 *         presion_psi:
 *           type: number
 *         kilometraje_vehiculo:
 *           type: integer
 *         observaciones:
 *           type: string
 *         fecha_evento:
 *           type: string
 *           format: date-time
 *
 *     ReparacionEntradaDTO:
 *       type: object
 *       required:
 *         - neumatico_id
 *         - proveedor_id
 *       properties:
 *         neumatico_id:
 *           type: string
 *           format: uuid
 *         proveedor_id:
 *           type: string
 *           format: uuid
 *         kilometraje_vehiculo:
 *           type: integer
 *         costo_estimado:
 *           type: number
 *         observaciones:
 *           type: string
 *         fecha_evento:
 *           type: string
 *           format: date-time
 *
 *     ReparacionSalidaDTO:
 *       type: object
 *       required:
 *         - neumatico_id
 *         - almacen_destino_id
 *       properties:
 *         neumatico_id:
 *           type: string
 *           format: uuid
 *         almacen_destino_id:
 *           type: string
 *           format: uuid
 *         costo_real:
 *           type: number
 *         profundidad_nueva_mm:
 *           type: number
 *         observaciones:
 *           type: string
 *         fecha_evento:
 *           type: string
 *           format: date-time
 *
 *     ReencaucheEntradaDTO:
 *       type: object
 *       required:
 *         - neumatico_id
 *         - proveedor_id
 *       properties:
 *         neumatico_id:
 *           type: string
 *           format: uuid
 *         proveedor_id:
 *           type: string
 *           format: uuid
 *         kilometraje_vehiculo:
 *           type: integer
 *         costo_estimado:
 *           type: number
 *         observaciones:
 *           type: string
 *         fecha_evento:
 *           type: string
 *           format: date-time
 *
 *     ReencaucheSalidaDTO:
 *       type: object
 *       required:
 *         - neumatico_id
 *         - almacen_destino_id
 *         - profundidad_nueva_mm
 *       properties:
 *         neumatico_id:
 *           type: string
 *           format: uuid
 *         almacen_destino_id:
 *           type: string
 *           format: uuid
 *         costo_real:
 *           type: number
 *         profundidad_nueva_mm:
 *           type: number
 *         observaciones:
 *           type: string
 *         fecha_evento:
 *           type: string
 *           format: date-time
 *
 *     DesechoNeumaticoDTO:
 *       type: object
 *       required:
 *         - neumatico_id
 *         - motivo_id
 *       properties:
 *         neumatico_id:
 *           type: string
 *           format: uuid
 *         motivo_id:
 *           type: string
 *           format: uuid
 *         kilometraje_vehiculo:
 *           type: integer
 *         observaciones:
 *           type: string
 *         fecha_evento:
 *           type: string
 *           format: date-time
 */
