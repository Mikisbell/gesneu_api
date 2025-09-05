'use client'

import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { 
  WrenchScrewdriverIcon, 
  ArrowRightIcon, 
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ClockIcon
} from '@heroicons/react/24/outline'

// Schema de validación
const montajeSchema = z.object({
  tipo_operacion: z.enum(['MONTAJE', 'DESMONTAJE', 'ROTACION']),
  vehiculo_origen_id: z.string().min(1, 'Selecciona vehículo origen'),
  posicion_origen_id: z.string().min(1, 'Selecciona posición origen'),
  vehiculo_destino_id: z.string().optional(),
  posicion_destino_id: z.string().optional(),
  motivo: z.enum(['DESGASTE', 'DAÑO', 'ROTACION_PROGRAMADA', 'MANTENIMIENTO', 'OTRO']),
  observaciones: z.string().optional(),
  kilometraje_actual: z.number().min(0).optional()
})

type MontajeForm = z.infer<typeof montajeSchema>

export default function MontajePage() {
  const [vehiculos, setVehiculos] = useState([])
  const [posicionesOrigen, setPosicionesOrigen] = useState([])
  const [posicionesDestino, setPosicionesDestino] = useState([])
  const [neumaticoOrigen, setNeumaticoOrigen] = useState(null)
  const [neumaticoDestino, setNeumaticoDestino] = useState(null)
  const [loading, setLoading] = useState(false)

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting }
  } = useForm<MontajeForm>({
    resolver: zodResolver(montajeSchema)
  })

  const tipoOperacion = watch('tipo_operacion')
  const vehiculoOrigenId = watch('vehiculo_origen_id')
  const posicionOrigenId = watch('posicion_origen_id')
  const vehiculoDestinoId = watch('vehiculo_destino_id')

  // Cargar vehículos
  useEffect(() => {
    fetch('/api/v1/vehiculos/')
      .then(res => res.json())
      .then(data => setVehiculos(data))
      .catch(console.error)
  }, [])

  // Cargar posiciones origen
  useEffect(() => {
    if (vehiculoOrigenId) {
      fetch('/api/v1/vehiculos/posiciones-neumatico')
        .then(res => res.json())
        .then(data => setPosicionesOrigen(data))
        .catch(console.error)
    }
  }, [vehiculoOrigenId])

  // Cargar posiciones destino
  useEffect(() => {
    if (vehiculoDestinoId && tipoOperacion !== 'DESMONTAJE') {
      fetch('/api/v1/vehiculos/posiciones-neumatico')
        .then(res => res.json())
        .then(data => setPosicionesDestino(data))
        .catch(console.error)
    }
  }, [vehiculoDestinoId, tipoOperacion])

  // Cargar neumático origen
  useEffect(() => {
    if (vehiculoOrigenId && posicionOrigenId) {
      setLoading(true)
      fetch(`/api/v1/neumaticos/?vehiculo_id=${vehiculoOrigenId}&posicion_id=${posicionOrigenId}`)
        .then(res => res.json())
        .then(data => {
          if (data.length > 0) {
            setNeumaticoOrigen(data[0])
          }
        })
        .catch(console.error)
        .finally(() => setLoading(false))
    }
  }, [vehiculoOrigenId, posicionOrigenId])

  const onSubmit = async (data: MontajeForm) => {
    try {
      // 1. Registrar evento de montaje/desmontaje
      const eventoData = {
        neumatico_id: neumaticoOrigen?.id,
        tipo_evento: data.tipo_operacion,
        descripcion: `${data.tipo_operacion} - Motivo: ${data.motivo}`,
        observaciones: data.observaciones,
        datos_adicionales: {
          vehiculo_origen_id: data.vehiculo_origen_id,
          posicion_origen_id: data.posicion_origen_id,
          vehiculo_destino_id: data.vehiculo_destino_id,
          posicion_destino_id: data.posicion_destino_id,
          motivo: data.motivo,
          kilometraje_actual: data.kilometraje_actual
        }
      }

      const eventoResponse = await fetch('/api/v1/eventos/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(eventoData)
      })

      if (!eventoResponse.ok) throw new Error('Error al registrar evento')

      // 2. Actualizar ubicación del neumático
      if (neumaticoOrigen) {
        let updateData = {}

        if (data.tipo_operacion === 'DESMONTAJE') {
          // Desmontaje: mover a almacén
          updateData = {
            ubicacion_actual_vehiculo_id: null,
            ubicacion_actual_posicion_id: null,
            estado_actual: 'EN_STOCK',
            kilometraje_acumulado: data.kilometraje_actual || neumaticoOrigen.kilometraje_acumulado
          }
        } else if (data.tipo_operacion === 'MONTAJE' || data.tipo_operacion === 'ROTACION') {
          // Montaje/Rotación: nueva ubicación
          updateData = {
            ubicacion_actual_vehiculo_id: data.vehiculo_destino_id || data.vehiculo_origen_id,
            ubicacion_actual_posicion_id: data.posicion_destino_id,
            estado_actual: 'INSTALADO',
            kilometraje_acumulado: data.kilometraje_actual || neumaticoOrigen.kilometraje_acumulado
          }
        }

        await fetch(`/api/v1/neumaticos/${neumaticoOrigen.id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(updateData)
        })

        // 3. Disparar predicción IA automática
        try {
          await fetch('/api/v1/ml/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ neumatico_id: neumaticoOrigen.id })
          })
        } catch (error) {
          console.warn('Predicción IA no disponible:', error)
        }
      }

      alert('Operación registrada exitosamente')
      window.location.reload()

    } catch (error) {
      console.error('Error:', error)
      alert('Error al registrar operación')
    }
  }

  const getMotivoColor = (motivo: string) => {
    const colors = {
      'DESGASTE': 'text-orange-600 bg-orange-100',
      'DAÑO': 'text-red-600 bg-red-100',
      'ROTACION_PROGRAMADA': 'text-blue-600 bg-blue-100',
      'MANTENIMIENTO': 'text-green-600 bg-green-100',
      'OTRO': 'text-gray-600 bg-gray-100'
    }
    return colors[motivo] || 'text-gray-600 bg-gray-100'
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Montaje y Desmontaje
        </h2>
        <p className="text-gray-600">
          Registra cambios de posición y reemplazos de neumáticos
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Formulario Principal */}
        <div className="lg:col-span-2">
          <form onSubmit={handleSubmit(onSubmit)} className="card p-6 space-y-6">
            {/* Tipo de Operación */}
            <div>
              <label className="form-label">Tipo de Operación</label>
              <div className="grid grid-cols-3 gap-4">
                {[
                  { value: 'MONTAJE', label: 'Montaje', icon: '🔧', color: 'border-green-500' },
                  { value: 'DESMONTAJE', label: 'Desmontaje', icon: '🔨', color: 'border-red-500' },
                  { value: 'ROTACION', label: 'Rotación', icon: '🔄', color: 'border-blue-500' }
                ].map((tipo) => (
                  <label key={tipo.value} className="cursor-pointer">
                    <input
                      type="radio"
                      {...register('tipo_operacion')}
                      value={tipo.value}
                      className="sr-only"
                    />
                    <div className={`border-2 rounded-lg p-4 text-center transition-colors ${
                      tipoOperacion === tipo.value 
                        ? `${tipo.color} bg-opacity-10` 
                        : 'border-gray-200 hover:border-gray-300'
                    }`}>
                      <div className="text-2xl mb-2">{tipo.icon}</div>
                      <div className="font-medium">{tipo.label}</div>
                    </div>
                  </label>
                ))}
              </div>
              {errors.tipo_operacion && (
                <p className="text-red-600 text-sm mt-1">{errors.tipo_operacion.message}</p>
              )}
            </div>

            {/* Ubicación Origen */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="form-label">Vehículo Origen</label>
                <select {...register('vehiculo_origen_id')} className="form-input">
                  <option value="">Seleccionar vehículo...</option>
                  {vehiculos.map((vehiculo: any) => (
                    <option key={vehiculo.id} value={vehiculo.id}>
                      {vehiculo.placa} - {vehiculo.marca}
                    </option>
                  ))}
                </select>
                {errors.vehiculo_origen_id && (
                  <p className="text-red-600 text-sm mt-1">{errors.vehiculo_origen_id.message}</p>
                )}
              </div>

              <div>
                <label className="form-label">Posición Origen</label>
                <select 
                  {...register('posicion_origen_id')} 
                  className="form-input"
                  disabled={!vehiculoOrigenId}
                >
                  <option value="">Seleccionar posición...</option>
                  {posicionesOrigen.map((posicion: any) => (
                    <option key={posicion.id} value={posicion.id}>
                      {posicion.nombre} ({posicion.eje})
                    </option>
                  ))}
                </select>
                {errors.posicion_origen_id && (
                  <p className="text-red-600 text-sm mt-1">{errors.posicion_origen_id.message}</p>
                )}
              </div>
            </div>

            {/* Ubicación Destino (solo para montaje y rotación) */}
            {tipoOperacion && tipoOperacion !== 'DESMONTAJE' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="form-label">Vehículo Destino</label>
                  <select {...register('vehiculo_destino_id')} className="form-input">
                    <option value="">Seleccionar vehículo...</option>
                    {vehiculos.map((vehiculo: any) => (
                      <option key={vehiculo.id} value={vehiculo.id}>
                        {vehiculo.placa} - {vehiculo.marca}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="form-label">Posición Destino</label>
                  <select 
                    {...register('posicion_destino_id')} 
                    className="form-input"
                    disabled={!vehiculoDestinoId}
                  >
                    <option value="">Seleccionar posición...</option>
                    {posicionesDestino.map((posicion: any) => (
                      <option key={posicion.id} value={posicion.id}>
                        {posicion.nombre} ({posicion.eje})
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            )}

            {/* Motivo y Kilometraje */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="form-label">Motivo</label>
                <select {...register('motivo')} className="form-input">
                  <option value="">Seleccionar motivo...</option>
                  <option value="DESGASTE">Desgaste normal</option>
                  <option value="DAÑO">Daño/Avería</option>
                  <option value="ROTACION_PROGRAMADA">Rotación programada</option>
                  <option value="MANTENIMIENTO">Mantenimiento</option>
                  <option value="OTRO">Otro</option>
                </select>
                {errors.motivo && (
                  <p className="text-red-600 text-sm mt-1">{errors.motivo.message}</p>
                )}
              </div>

              <div>
                <label className="form-label">Kilometraje Actual</label>
                <input
                  type="number"
                  {...register('kilometraje_actual', { valueAsNumber: true })}
                  className="form-input"
                  placeholder="Kilometraje del vehículo"
                />
              </div>
            </div>

            {/* Observaciones */}
            <div>
              <label className="form-label">Observaciones</label>
              <textarea
                {...register('observaciones')}
                rows={3}
                className="form-input"
                placeholder="Detalles adicionales de la operación..."
              />
            </div>

            {/* Botones */}
            <div className="flex space-x-4">
              <button
                type="submit"
                disabled={isSubmitting || loading}
                className="btn-primary flex-1"
              >
                {isSubmitting ? 'Procesando...' : 'Registrar Operación'}
              </button>
              
              <button
                type="button"
                className="btn-secondary"
                onClick={() => window.history.back()}
              >
                Cancelar
              </button>
            </div>
          </form>
        </div>

        {/* Panel de Información */}
        <div className="space-y-6">
          {/* Información del Neumático Origen */}
          {neumaticoOrigen && (
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <WrenchScrewdriverIcon className="w-5 h-5 text-gray-600 mr-2" />
                Neumático Seleccionado
              </h3>
              
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-600">Número de Serie</p>
                  <p className="font-medium">{neumaticoOrigen.numero_serie}</p>
                </div>
                
                <div>
                  <p className="text-sm text-gray-600">Estado Actual</p>
                  <span className={`status-badge ${
                    neumaticoOrigen.estado_actual === 'INSTALADO' ? 'status-active' :
                    neumaticoOrigen.estado_actual === 'EN_STOCK' ? 'status-warning' : 'status-danger'
                  }`}>
                    {neumaticoOrigen.estado_actual}
                  </span>
                </div>
                
                <div>
                  <p className="text-sm text-gray-600">Kilometraje Acumulado</p>
                  <p className="font-medium">{neumaticoOrigen.kilometraje_acumulado?.toLocaleString()} km</p>
                </div>
                
                <div>
                  <p className="text-sm text-gray-600">Vida Actual</p>
                  <p className="font-medium">{neumaticoOrigen.vida_actual}</p>
                </div>

                <div>
                  <p className="text-sm text-gray-600">Profundidad Actual</p>
                  <p className="font-medium">{neumaticoOrigen.profundidad_remanente_actual_mm} mm</p>
                </div>

                {/* Predicción IA si existe */}
                {neumaticoOrigen.vida_util_restante_km && (
                  <div className="border-t pt-3 mt-3">
                    <p className="text-sm text-gray-600">Vida Restante (IA)</p>
                    <p className="font-bold text-blue-600">
                      {neumaticoOrigen.vida_util_restante_km?.toLocaleString()} km
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Guía de Operaciones */}
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Guía de Operaciones
            </h3>
            
            <div className="space-y-4 text-sm">
              <div className="flex items-start">
                <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center mr-3 mt-0.5">
                  <span className="text-green-600 text-xs">M</span>
                </div>
                <div>
                  <p className="font-medium">Montaje</p>
                  <p className="text-gray-600">Instalar neumático de almacén a vehículo</p>
                </div>
              </div>

              <div className="flex items-start">
                <div className="w-6 h-6 bg-red-100 rounded-full flex items-center justify-center mr-3 mt-0.5">
                  <span className="text-red-600 text-xs">D</span>
                </div>
                <div>
                  <p className="font-medium">Desmontaje</p>
                  <p className="text-gray-600">Retirar neumático de vehículo a almacén</p>
                </div>
              </div>

              <div className="flex items-start">
                <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center mr-3 mt-0.5">
                  <span className="text-blue-600 text-xs">R</span>
                </div>
                <div>
                  <p className="font-medium">Rotación</p>
                  <p className="text-gray-600">Cambiar posición dentro del mismo vehículo</p>
                </div>
              </div>
            </div>
          </div>

          {/* Recordatorios */}
          <div className="card p-6 border-l-4 border-yellow-500">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <ExclamationTriangleIcon className="w-5 h-5 text-yellow-600 mr-2" />
              Recordatorios
            </h3>
            
            <ul className="space-y-2 text-sm text-gray-600">
              <li>• Verificar presión antes del montaje</li>
              <li>• Inspeccionar estado visual del neumático</li>
              <li>• Actualizar kilometraje del vehículo</li>
              <li>• Registrar observaciones importantes</li>
              <li>• La IA calculará automáticamente nueva predicción</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
