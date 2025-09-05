'use client'

import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { 
  MagnifyingGlassIcon, 
  CameraIcon, 
  CheckCircleIcon,
  ExclamationTriangleIcon 
} from '@heroicons/react/24/outline'

// Schema de validación
const inspeccionSchema = z.object({
  vehiculo_id: z.string().min(1, 'Selecciona un vehículo'),
  posicion_id: z.string().min(1, 'Selecciona una posición'),
  profundidad_mm: z.number().min(0).max(20, 'Profundidad debe estar entre 0-20mm'),
  estado_visual: z.enum(['EXCELENTE', 'BUENO', 'REGULAR', 'MALO', 'CRITICO']),
  observaciones: z.string().optional(),
  temperatura_ambiente: z.number().optional(),
  presion_psi: z.number().min(0).max(150).optional()
})

type InspeccionForm = z.infer<typeof inspeccionSchema>

export default function InspeccionPage() {
  const [vehiculos, setVehiculos] = useState([])
  const [posiciones, setPosiciones] = useState([])
  const [neumatico, setNeumatico] = useState(null)
  const [loading, setLoading] = useState(false)
  const [prediccionIA, setPrediccionIA] = useState(null)

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting }
  } = useForm<InspeccionForm>({
    resolver: zodResolver(inspeccionSchema)
  })

  const vehiculoSeleccionado = watch('vehiculo_id')
  const posicionSeleccionada = watch('posicion_id')

  // Cargar vehículos al montar
  useEffect(() => {
    fetch('/api/v1/vehiculos/')
      .then(res => res.json())
      .then(data => setVehiculos(data))
      .catch(console.error)
  }, [])

  // Cargar posiciones cuando se selecciona vehículo
  useEffect(() => {
    if (vehiculoSeleccionado) {
      fetch('/api/v1/vehiculos/posiciones-neumatico')
        .then(res => res.json())
        .then(data => setPosiciones(data))
        .catch(console.error)
    }
  }, [vehiculoSeleccionado])

  // Cargar neumático actual cuando se selecciona posición
  useEffect(() => {
    if (vehiculoSeleccionado && posicionSeleccionada) {
      setLoading(true)
      // Buscar neumático en esa posición
      fetch(`/api/v1/neumaticos/?vehiculo_id=${vehiculoSeleccionado}&posicion_id=${posicionSeleccionada}`)
        .then(res => res.json())
        .then(data => {
          if (data.length > 0) {
            setNeumatico(data[0])
            // Cargar predicción IA si existe
            if (data[0].prediccion_fecha_reemplazo) {
              setPrediccionIA({
                vida_restante: data[0].vida_util_restante_km,
                fecha_reemplazo: data[0].prediccion_fecha_reemplazo,
                confianza: data[0].confianza_prediccion
              })
            }
          }
        })
        .catch(console.error)
        .finally(() => setLoading(false))
    }
  }, [vehiculoSeleccionado, posicionSeleccionada])

  const onSubmit = async (data: InspeccionForm) => {
    try {
      // 1. Registrar evento de inspección
      const eventoData = {
        neumatico_id: neumatico?.id,
        tipo_evento: 'INSPECCION',
        descripcion: `Inspección - Profundidad: ${data.profundidad_mm}mm, Estado: ${data.estado_visual}`,
        observaciones: data.observaciones,
        datos_adicionales: {
          profundidad_mm: data.profundidad_mm,
          estado_visual: data.estado_visual,
          temperatura_ambiente: data.temperatura_ambiente,
          presion_psi: data.presion_psi
        }
      }

      const eventoResponse = await fetch('/api/v1/eventos/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(eventoData)
      })

      if (!eventoResponse.ok) throw new Error('Error al registrar evento')

      // 2. Actualizar medición de profundidad en neumático
      if (neumatico) {
        const updateData = {
          profundidad_remanente_actual_mm: data.profundidad_mm,
          fecha_ultima_medicion_profundidad: new Date().toISOString()
        }

        await fetch(`/api/v1/neumaticos/${neumatico.id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(updateData)
        })

        // 3. Disparar predicción IA automática
        try {
          const prediccionResponse = await fetch('/api/v1/ml/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ neumatico_id: neumatico.id })
          })

          if (prediccionResponse.ok) {
            const prediccion = await prediccionResponse.json()
            setPrediccionIA({
              vida_restante: prediccion.vida_util_restante_km,
              fecha_reemplazo: prediccion.fecha_estimada_reemplazo,
              confianza: prediccion.confianza_prediccion
            })
          }
        } catch (error) {
          console.warn('Predicción IA no disponible:', error)
        }
      }

      // Mostrar éxito y limpiar formulario
      alert('Inspección registrada exitosamente')
      window.location.reload()

    } catch (error) {
      console.error('Error:', error)
      alert('Error al registrar inspección')
    }
  }

  const getEstadoColor = (estado: string) => {
    const colors = {
      'EXCELENTE': 'text-green-600 bg-green-100',
      'BUENO': 'text-blue-600 bg-blue-100',
      'REGULAR': 'text-yellow-600 bg-yellow-100',
      'MALO': 'text-orange-600 bg-orange-100',
      'CRITICO': 'text-red-600 bg-red-100'
    }
    return colors[estado] || 'text-gray-600 bg-gray-100'
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Inspección de Neumáticos
        </h2>
        <p className="text-gray-600">
          Registra mediciones de profundidad y estado visual
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Formulario Principal */}
        <div className="lg:col-span-2">
          <form onSubmit={handleSubmit(onSubmit)} className="card p-6 space-y-6">
            {/* Selección de Vehículo */}
            <div>
              <label className="form-label">Vehículo</label>
              <select 
                {...register('vehiculo_id')}
                className="form-input"
              >
                <option value="">Seleccionar vehículo...</option>
                {vehiculos.map((vehiculo: any) => (
                  <option key={vehiculo.id} value={vehiculo.id}>
                    {vehiculo.placa} - {vehiculo.marca} {vehiculo.modelo}
                  </option>
                ))}
              </select>
              {errors.vehiculo_id && (
                <p className="text-red-600 text-sm mt-1">{errors.vehiculo_id.message}</p>
              )}
            </div>

            {/* Selección de Posición */}
            <div>
              <label className="form-label">Posición del Neumático</label>
              <select 
                {...register('posicion_id')}
                className="form-input"
                disabled={!vehiculoSeleccionado}
              >
                <option value="">Seleccionar posición...</option>
                {posiciones.map((posicion: any) => (
                  <option key={posicion.id} value={posicion.id}>
                    {posicion.nombre} ({posicion.eje})
                  </option>
                ))}
              </select>
              {errors.posicion_id && (
                <p className="text-red-600 text-sm mt-1">{errors.posicion_id.message}</p>
              )}
            </div>

            {/* Medición de Profundidad */}
            <div>
              <label className="form-label">Profundidad de Banda (mm)</label>
              <div className="relative">
                <input
                  type="number"
                  step="0.1"
                  {...register('profundidad_mm', { valueAsNumber: true })}
                  className="form-input pr-12"
                  placeholder="0.0"
                />
                <div className="absolute inset-y-0 right-0 flex items-center pr-3">
                  <span className="text-gray-500 text-sm">mm</span>
                </div>
              </div>
              {errors.profundidad_mm && (
                <p className="text-red-600 text-sm mt-1">{errors.profundidad_mm.message}</p>
              )}
            </div>

            {/* Estado Visual */}
            <div>
              <label className="form-label">Estado Visual</label>
              <select {...register('estado_visual')} className="form-input">
                <option value="">Seleccionar estado...</option>
                <option value="EXCELENTE">Excelente</option>
                <option value="BUENO">Bueno</option>
                <option value="REGULAR">Regular</option>
                <option value="MALO">Malo</option>
                <option value="CRITICO">Crítico</option>
              </select>
              {errors.estado_visual && (
                <p className="text-red-600 text-sm mt-1">{errors.estado_visual.message}</p>
              )}
            </div>

            {/* Mediciones Adicionales */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="form-label">Presión (PSI)</label>
                <input
                  type="number"
                  {...register('presion_psi', { valueAsNumber: true })}
                  className="form-input"
                  placeholder="0"
                />
              </div>
              <div>
                <label className="form-label">Temperatura Ambiente (°C)</label>
                <input
                  type="number"
                  {...register('temperatura_ambiente', { valueAsNumber: true })}
                  className="form-input"
                  placeholder="0"
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
                placeholder="Observaciones adicionales..."
              />
            </div>

            {/* Botones de Acción */}
            <div className="flex space-x-4">
              <button
                type="submit"
                disabled={isSubmitting || loading}
                className="btn-primary flex-1"
              >
                {isSubmitting ? 'Registrando...' : 'Registrar Inspección'}
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
          {/* Información del Neumático */}
          {neumatico && (
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Información del Neumático
              </h3>
              
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-600">Número de Serie</p>
                  <p className="font-medium">{neumatico.numero_serie}</p>
                </div>
                
                <div>
                  <p className="text-sm text-gray-600">Kilometraje Actual</p>
                  <p className="font-medium">{neumatico.kilometraje_acumulado?.toLocaleString()} km</p>
                </div>
                
                <div>
                  <p className="text-sm text-gray-600">Vida Actual</p>
                  <p className="font-medium">{neumatico.vida_actual}</p>
                </div>
                
                <div>
                  <p className="text-sm text-gray-600">Última Medición</p>
                  <p className="font-medium">
                    {neumatico.profundidad_remanente_actual_mm} mm
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Predicción IA */}
          {prediccionIA && (
            <div className="card p-6 border-l-4 border-blue-500">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <CheckCircleIcon className="w-5 h-5 text-blue-600 mr-2" />
                Predicción IA
              </h3>
              
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-600">Vida Restante Estimada</p>
                  <p className="font-bold text-lg text-blue-600">
                    {prediccionIA.vida_restante?.toLocaleString()} km
                  </p>
                </div>
                
                <div>
                  <p className="text-sm text-gray-600">Fecha Estimada de Reemplazo</p>
                  <p className="font-medium">
                    {new Date(prediccionIA.fecha_reemplazo).toLocaleDateString()}
                  </p>
                </div>
                
                <div>
                  <p className="text-sm text-gray-600">Confianza de Predicción</p>
                  <div className="flex items-center">
                    <div className="flex-1 bg-gray-200 rounded-full h-2 mr-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{ width: `${(prediccionIA.confianza * 100)}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium">
                      {Math.round(prediccionIA.confianza * 100)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Guía de Medición */}
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Guía de Medición
            </h3>
            
            <div className="space-y-3 text-sm">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
                <span><strong>≥ 4mm:</strong> Excelente estado</span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 bg-blue-500 rounded-full mr-2"></div>
                <span><strong>3-4mm:</strong> Buen estado</span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 bg-yellow-500 rounded-full mr-2"></div>
                <span><strong>2-3mm:</strong> Regular - Monitorear</span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 bg-orange-500 rounded-full mr-2"></div>
                <span><strong>1-2mm:</strong> Malo - Planificar cambio</span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
                <span><strong>< 1mm:</strong> Crítico - Cambio inmediato</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
