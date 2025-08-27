# ges_neu_api/catalogos/router.py

from uuid import UUID
from typing import List, Optional

from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

# Importaciones absolutas
from ges_neu_api.core.database import get_session
from ges_neu_api.auth.models.usuario import Usuario
from ges_neu_api.auth import service as auth_service
from ges_neu_api.catalogos import service
from ges_neu_api.catalogos.schemas import (
    FabricanteCreate, FabricanteRead, FabricanteUpdate,
    ModeloNeumaticoCreate, ModeloNeumaticoRead, ModeloNeumaticoUpdate,
    ProveedorCreate, ProveedorRead, ProveedorUpdate,
    MotivoDesechoCreate, MotivoDesechoRead, MotivoDesechoUpdate,
    AlmacenCreate, AlmacenRead, AlmacenUpdate,
    ParametroInventarioCreate, ParametroInventarioRead, ParametroInventarioUpdate
)
from ges_neu_api.catalogos.models import (
    Fabricante, ModeloNeumatico, Proveedor, MotivoDesecho, Almacen, ParametroInventario
)

router = APIRouter(tags=["Catálogos"])

# --- Endpoints para Fabricantes ---

@router.post(
    "/fabricantes/", 
    response_model=FabricanteRead, 
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo fabricante",
    description="Crea un nuevo fabricante en el sistema. Requiere autenticación."
)
async def create_fabricante(
    *,
    db: AsyncSession = Depends(get_session),
    fabricante_in: FabricanteCreate,
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    try:
        user_id = current_user.id if current_user else None
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se pudo identificar al usuario autenticado"
            )
            
        return await service.create_fabricante(
            db, fabricante_in=fabricante_in, user_id=user_id
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al crear el fabricante: {str(e)}"
        )

@router.get(
    "/fabricantes/", 
    response_model=List[FabricanteRead],
    summary="Listar fabricantes",
    description="Obtiene una lista de fabricantes con paginación. Requiere autenticación."
)
async def read_fabricantes(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=100, description="Número máximo de registros a devolver"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo"),
    db: AsyncSession = Depends(get_session),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    try:
        user_id = current_user.id if current_user else None
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se pudo identificar al usuario autenticado"
            )
            
        return await service.get_all_fabricantes(
            db, skip=skip, limit=limit, activo=activo
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los fabricantes: {str(e)}"
        )

@router.get(
    "/fabricantes/{fabricante_id}", 
    response_model=FabricanteRead,
    summary="Obtener un fabricante",
    description="Obtiene un fabricante por su ID. Requiere autenticación."
)
async def read_fabricante(
    *,
    db: AsyncSession = Depends(get_session),
    fabricante_id: UUID,
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    try:
        user_id = current_user.id if current_user else None
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se pudo identificar al usuario autenticado"
            )
            
        return await service.get_fabricante_by_id(db, fabricante_id=fabricante_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el fabricante: {str(e)}"
        )

@router.put(
    "/fabricantes/{fabricante_id}", 
    response_model=FabricanteRead,
    summary="Actualizar un fabricante",
    description="Actualiza un fabricante existente. Requiere autenticación."
)
async def update_fabricante(
    *,
    db: AsyncSession = Depends(get_session),
    fabricante_id: UUID,
    fabricante_in: FabricanteUpdate,
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    try:
        user_id = current_user.id if current_user else None
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se pudo identificar al usuario autenticado"
            )
            
        return await service.update_fabricante(
            db, fabricante_id=fabricante_id, fabricante_in=fabricante_in, user_id=user_id
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el fabricante: {str(e)}"
        )

@router.delete(
    "/fabricantes/{fabricante_id}",
    response_model=FabricanteRead,
    summary="Eliminar un fabricante",
    description="Elimina un fabricante. No se puede eliminar si tiene modelos asociados. Requiere autenticación."
)
async def delete_fabricante(
    *,
    db: AsyncSession = Depends(get_session),
    fabricante_id: UUID,
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    try:
        user_id = current_user.id if current_user else None
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se pudo identificar al usuario autenticado"
            )
            
        return await service.delete_fabricante(db, fabricante_id=fabricante_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar el fabricante: {str(e)}"
        )

# --- Endpoints para Modelos ---

@router.post(
    "/modelos/", 
    response_model=ModeloNeumaticoRead, 
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo modelo",
    description="Crea un nuevo modelo de neumático. Requiere autenticación."
)
async def create_modelo(
    *,
    db: AsyncSession = Depends(get_session),
    modelo_in: ModeloNeumaticoCreate,
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    try:
        user_id = current_user.id if current_user else None
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se pudo identificar al usuario autenticado"
            )
            
        return await service.create_modelo(
            db, modelo_in=modelo_in, user_id=user_id
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el modelo: {str(e)}"
        )

@router.get(
    "/modelos/", 
    response_model=List[ModeloNeumaticoRead],
    summary="Listar modelos",
    description="Obtiene una lista de modelos con filtros opcionales. Requiere autenticación."
)
async def read_modelos(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=100, description="Número máximo de registros a devolver"),
    fabricante_id: Optional[UUID] = Query(None, description="Filtrar por ID de fabricante"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo"),
    db: AsyncSession = Depends(get_session),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    try:
        user_id = current_user.id if current_user else None
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se pudo identificar al usuario autenticado"
            )
            
        return await service.get_all_modelos(
            db, 
            skip=skip, 
            limit=limit, 
            fabricante_id=fabricante_id,
            activo=activo
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los modelos: {str(e)}"
        )

@router.get(
    "/modelos/{modelo_id}", 
    response_model=ModeloNeumaticoRead,
    summary="Obtener un modelo",
    description="Obtiene un modelo por su ID. Requiere autenticación."
)
async def read_modelo(
    *,
    db: AsyncSession = Depends(get_session),
    modelo_id: UUID,
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    try:
        user_id = current_user.id if current_user else None
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se pudo identificar al usuario autenticado"
            )
            
        return await service.get_modelo_by_id(db, modelo_id=modelo_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el modelo: {str(e)}"
        )

@router.put(
    "/modelos/{modelo_id}", 
    response_model=ModeloNeumaticoRead,
    summary="Actualizar un modelo",
    description="Actualiza un modelo existente. Requiere autenticación."
)
async def update_modelo(
    *,
    db: AsyncSession = Depends(get_session),
    modelo_id: UUID,
    modelo_in: ModeloNeumaticoUpdate,
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    try:
        user_id = current_user.id if current_user else None
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se pudo identificar al usuario autenticado"
            )
            
        return await service.update_modelo(
            db, modelo_id=modelo_id, modelo_in=modelo_in, user_id=user_id
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el modelo: {str(e)}"
        )

@router.delete(
    "/modelos/{modelo_id}",
    response_model=ModeloNeumaticoRead,
    summary="Eliminar un modelo",
    description="Elimina un modelo. Requiere autenticación."
)
async def delete_modelo(
    *,
    db: AsyncSession = Depends(get_session),
    modelo_id: UUID,
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    try:
        user_id = current_user.id if current_user else None
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se pudo identificar al usuario autenticado"
            )
            
        return await service.delete_modelo(db, modelo_id=modelo_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar el modelo: {str(e)}"
        )

# --- Endpoints para Proveedores ---

@router.post(
    "/proveedores/",
    response_model=ProveedorRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo proveedor",
    description="""
    ## Descripción
    Crea un nuevo proveedor en el sistema con la información proporcionada.
    
    ## Permisos requeridos
    - `proveedores:crear`
    
    ## Parámetros de la solicitud
    - **nombre**: Nombre del proveedor (requerido, máximo 100 caracteres)
    - **ruc**: RUC del proveedor (opcional, debe ser único si se proporciona)
    - **email**: Correo electrónico de contacto (opcional, debe ser un email válido)
    - **telefono**: Número de teléfono (opcional, máximo 20 caracteres)
    - **direccion**: Dirección física (opcional, máximo 255 caracteres)
    - **tipo**: Tipo de proveedor (NACIONAL o INTERNACIONAL, requerido)
    - **activo**: Estado del proveedor (opcional, por defecto True)
    
    ## Ejemplo de solicitud
    ```json
    {
        "nombre": "Proveedor Ejemplo S.A.",
        "ruc": "20123456789",
        "email": "contacto@proveedorejemplo.com",
        "telefono": "+51999123456",
        "direccion": "Av. Ejemplo 123, Lima, Perú",
        "tipo": "NACIONAL",
        "activo": true
    }
    ```
    
    ## Respuestas
    - **201 Created**: Proveedor creado exitosamente
    - **400 Bad Request**: Datos de entrada inválidos
    - **401 Unauthorized**: No autenticado
    - **403 Forbidden**: No tiene permisos para crear proveedores
    - **409 Conflict**: Ya existe un proveedor con el mismo RUC o nombre
    - **422 Unprocessable Entity**: Error de validación en los datos de entrada
    
    ## Notas
    - El campo `tipo` solo acepta los valores: 'NACIONAL' o 'INTERNACIONAL'
    - El RUC debe ser único en el sistema
    - Solo usuarios autenticados pueden realizar esta operación
    """,
    responses={
        status.HTTP_201_CREATED: {
            "description": "Proveedor creado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "nombre": "Proveedor Ejemplo S.A.",
                        "ruc": "20123456789",
                        "email": "contacto@proveedorejemplo.com",
                        "telefono": "+51999123456",
                        "direccion": "Av. Ejemplo 123, Lima, Perú",
                        "tipo": "NACIONAL",
                        "activo": true,
                        "fecha_creacion": "2025-01-01T12:00:00",
                        "fecha_actualizacion": "2025-01-01T12:00:00",
                        "usuario_creacion_id": "123e4567-e89b-12d3-a456-426614174000",
                        "usuario_actualizacion_id": "123e4567-e89b-12d3-a456-426614174000"
                    }
                }
            }
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Datos de entrada inválidos",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "El RUC ya está registrado"
                    }
                }
            }
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "No autenticado",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "No se pudo validar el token de autenticación"
                    }
                }
            }
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "No tiene permisos para realizar esta acción",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "No tiene permisos para crear proveedores"
                    }
                }
            }
        },
        status.HTTP_409_CONFLICT: {
            "description": "Conflicto con los datos proporcionados",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Ya existe un proveedor con el RUC: 20123456789"
                    }
                }
            }
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Error de validación",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "tipo"],
                                "msg": "value is not a valid enumeration member; permitted: 'NACIONAL', 'INTERNACIONAL'",
                                "type": "type_error.enum",
                                "ctx": {"enum_values": ["NACIONAL", "INTERNACIONAL"]}
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def crear_proveedor(
    *,
    db: AsyncSession = Depends(get_session),
    proveedor_in: ProveedorCreate,
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    """
    Crea un nuevo proveedor en el sistema.
    
    Args:
        db: Sesión de base de datos
        proveedor_in: Datos del proveedor a crear
        current_user: Usuario autenticado
        
    Returns:
        ProveedorRead: El proveedor creado con su ID asignado
        
    Raises:
        HTTPException: Si ocurre un error durante la creación
    """
    try:
        user_id = current_user.id if current_user else None
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se pudo identificar al usuario autenticado"
            )
            
        # Verificar permisos
        if not await auth_service.tiene_permiso(
            db=db, 
            usuario_id=user_id, 
            permiso_codigo="proveedores:crear"
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para crear proveedores"
            )
            
        return await service.create_proveedor(
            db=db, 
            proveedor_in=proveedor_in, 
            usuario_id=user_id
        )
        
    except service.ProveedorYaExisteError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear proveedor: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error inesperado al crear el proveedor"
        )

@router.get(
    "/proveedores/",
    response_model=List[ProveedorRead],
    summary="Listar proveedores",
    description="""
    ## Descripción
    Obtiene una lista paginada de proveedores con opciones de filtrado.
    
    ## Permisos requeridos
    - `proveedores:leer`
    
    ## Parámetros de consulta
    - **skip** (int, opcional): Número de registros a saltar. Por defecto 0.
    - **limit** (int, opcional): Número máximo de registros a devolver (1-1000). Por defecto 100.
    - **activo** (bool, opcional): Filtrar por estado activo/inactivo.
    - **tipo** (str, opcional): Filtrar por tipo de proveedor (NACIONAL o INTERNACIONAL).
    - **buscar** (str, opcional): Término de búsqueda para filtrar por nombre o RUC.
    
    ## Ejemplo de solicitud
    ```
    GET /api/v1/catalogos/proveedores/?skip=0&limit=10&activo=true&tipo=NACIONAL&buscar=ejemplo
    ```
    
    ## Respuestas
    - **200 OK**: Lista de proveedores obtenida exitosamente
    - **401 Unauthorized**: No autenticado
    - **403 Forbidden**: No tiene permisos para ver proveedores
    - **422 Unprocessable Entity**: Error de validación en los parámetros de consulta
    
    ## Notas
    - Los resultados incluyen metadatos de paginación cuando corresponda
    - Solo se devuelven los proveedores a los que el usuario tiene acceso
    - El campo `tipo` es sensible a mayúsculas/minúsculas
    """,
    responses={
        status.HTTP_200_OK: {
            "description": "Lista de proveedores obtenida exitosamente",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "nombre": "Proveedor Ejemplo S.A.",
                            "ruc": "20123456789",
                            "email": "contacto@proveedorejemplo.com",
                            "telefono": "+51999123456",
                            "direccion": "Av. Ejemplo 123, Lima, Perú",
                            "tipo": "NACIONAL",
                            "activo": true,
                            "fecha_creacion": "2025-01-01T12:00:00",
                            "fecha_actualizacion": "2025-01-01T12:00:00"
                        },
                        {
                            "id": "660e8400-e29b-41d4-a716-446655441111",
                            "nombre": "Otro Proveedor S.A.C.",
                            "ruc": "20123456780",
                            "email": "contacto@otroproveedor.com",
                            "telefono": "+51999876543",
                            "direccion": "Calle Ejemplo 456, Lima, Perú",
                            "tipo": "INTERNACIONAL",
                            "activo": true,
                            "fecha_creacion": "2025-01-02T10:30:00",
                            "fecha_actualizacion": "2025-01-02T10:30:00"
                        }
                    ]
                }
            }
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "No autenticado",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "No se pudo validar el token de autenticación"
                    }
                }
            }
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "No tiene permisos para realizar esta acción",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "No tiene permisos para ver proveedores"
                    }
                }
            }
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Error de validación en los parámetros de consulta",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["query", "limit"],
                                "msg": "ensure this value is less than or equal to 1000",
                                "type": "value_error.number.not_le",
                                "ctx": {"limit_value": 1000}
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def listar_proveedores(
    skip: int = Query(
        0, 
        ge=0, 
        description="Número de registros a saltar"
    ),
    limit: int = Query(
        100, 
        ge=1, 
        le=1000, 
        description="Número máximo de registros a devolver"
    ),
    activo: Optional[bool] = Query(
        None, 
        description="Filtrar por estado activo/inactivo"
    ),
    tipo: Optional[str] = Query(
        None, 
        description="Filtrar por tipo de proveedor (NACIONAL o INTERNACIONAL)",
        regex="^(NACIONAL|INTERNACIONAL)$"
    ),
    buscar: Optional[str] = Query(
        None, 
        description="Término de búsqueda para filtrar por nombre o RUC",
        min_length=3,
        max_length=100
    ),
    db: AsyncSession = Depends(get_session),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    """
    Lista los proveedores con opciones de paginación y filtrado.
    
    Args:
        skip: Número de registros a saltar
        limit: Número máximo de registros a devolver (1-1000)
        activo: Filtrar por estado activo/inactivo
        tipo: Filtrar por tipo de proveedor
        buscar: Término de búsqueda para nombre o RUC
        db: Sesión de base de datos
        current_user: Usuario autenticado
        
    Returns:
        List[ProveedorRead]: Lista de proveedores que coinciden con los filtros
        
    Raises:
        HTTPException: Si ocurre un error durante la consulta
    """
    try:
        user_id = current_user.id if current_user else None
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se pudo identificar al usuario autenticado"
            )
            
        # Verificar permisos
        if not await auth_service.tiene_permiso(
            db=db, 
            usuario_id=user_id, 
            permiso_codigo="proveedores:leer"
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para ver proveedores"
            )
            
        # Aplicar filtros
        filtros = {}
        if activo is not None:
            filtros["activo"] = activo
        if tipo:
            filtros["tipo"] = tipo
            
        # Realizar búsqueda si se proporciona un término
        if buscar:
            return await service.buscar_proveedores(
                db=db,
                termino=buscar,
                skip=skip,
                limit=limit,
                **filtros
            )
            
        # Listar con filtros básicos
        return await service.get_proveedores(
            db=db,
            skip=skip,
            limit=limit,
            **filtros
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al listar proveedores: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error inesperado al listar los proveedores"
        )

@router.get(
    "/proveedores/{proveedor_id}",
    response_model=ProveedorRead,
    summary="Obtener un proveedor por ID",
    tags=["Proveedores"]
)
async def obtener_proveedor(
    *,
    db: AsyncSession = Depends(get_session),
    proveedor_id: UUID,
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    """
    Obtiene los detalles de un proveedor específico por su ID.
    """
    user_id = current_user.id if current_user else None
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo identificar al usuario autenticado"
        )
        
    return await service.get_proveedor_by_id(db=db, proveedor_id=proveedor_id)

@router.put(
    "/proveedores/{proveedor_id}",
    response_model=ProveedorRead,
    summary="Actualizar un proveedor",
    tags=["Proveedores"]
)
async def actualizar_proveedor(
    *,
    db: AsyncSession = Depends(get_session),
    proveedor_id: UUID,
    proveedor_in: ProveedorUpdate,
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    """
    Actualiza los datos de un proveedor existente.
    
    Solo se actualizarán los campos incluidos en la solicitud.
    """
    user_id = current_user.id if current_user else None
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo identificar al usuario autenticado"
        )
        
    return await service.update_proveedor(
        db=db,
        proveedor_id=proveedor_id,
        proveedor_in=proveedor_in,
        user_id=user_id
    )

@router.delete(
    "/proveedores/{proveedor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un proveedor",
    tags=["Proveedores"]
)
async def eliminar_proveedor(
    *,
    db: AsyncSession = Depends(get_session),
    proveedor_id: UUID,
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    """
    Elimina un proveedor del sistema.
    
    Esta operación solo se permite si el proveedor no tiene registros asociados.
    """
    user_id = current_user.id if current_user else None
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo identificar al usuario autenticado"
        )
        
    await service.delete_proveedor(
        db=db,
        proveedor_id=proveedor_id
    )
    return {"status_code": status.HTTP_204_NO_CONTENT}

# --- Endpoints para Motivos de Desecho ---

@router.post(
    "/motivos-desecho/",
    response_model=MotivoDesechoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo motivo de desecho",
    tags=["Motivos de Desecho"]
)
async def crear_motivo_desecho(
    *,
    db: AsyncSession = Depends(get_session),
    motivo_in: MotivoDesechoCreate,
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    """
    Crea un nuevo motivo de desecho en el sistema.
    
    - **codigo**: Código único del motivo (requerido)
    - **descripcion**: Descripción detallada del motivo (requerida)
    """
    user_id = current_user.id if current_user else None
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo identificar al usuario autenticado"
        )
        
    return await service.create_motivo_desecho(
        db=db,
        motivo_in=motivo_in,
        user_id=user_id
    )

@router.get(
    "/motivos-desecho/",
    response_model=List[MotivoDesechoRead],
    summary="Listar todos los motivos de desecho",
    tags=["Motivos de Desecho"]
)
async def listar_motivos_desecho(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a devolver"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo"),
    db: AsyncSession = Depends(get_session),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    """
    Obtiene una lista de motivos de desecho con paginación y filtros opcionales.
    """
    user_id = current_user.id if current_user else None
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo identificar al usuario autenticado"
        )
        
    return await service.get_all_motivos_desecho(
        db=db,
        skip=skip,
        limit=limit,
        activo=activo
    )

@router.get(
    "/motivos-desecho/{motivo_id}",
    response_model=MotivoDesechoRead,
    summary="Obtener un motivo de desecho por ID",
    tags=["Motivos de Desecho"]
)
async def obtener_motivo_desecho(
    *,
    db: AsyncSession = Depends(get_session),
    motivo_id: UUID,
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    """
    Obtiene los detalles de un motivo de desecho específico por su ID.
    """
    user_id = current_user.id if current_user else None
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo identificar al usuario autenticado"
        )
        
    return await service.get_motivo_desecho_by_id(db=db, motivo_id=motivo_id)

@router.put(
    "/motivos-desecho/{motivo_id}",
    response_model=MotivoDesechoRead,
    summary="Actualizar un motivo de desecho",
    tags=["Motivos de Desecho"]
)
async def actualizar_motivo_desecho(
    *,
    db: AsyncSession = Depends(get_session),
    motivo_id: UUID,
    motivo_in: MotivoDesechoUpdate,
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    """
    Actualiza los datos de un motivo de desecho existente.
    
    Solo se actualizarán los campos incluidos en la solicitud.
    """
    user_id = current_user.id if current_user else None
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo identificar al usuario autenticado"
        )
        
    return await service.update_motivo_desecho(
        db=db,
        motivo_id=motivo_id,
        motivo_in=motivo_in,
        user_id=user_id
    )

@router.delete(
    "/motivos-desecho/{motivo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un motivo de desecho",
    tags=["Motivos de Desecho"]
)
async def eliminar_motivo_desecho(
    *,
    db: AsyncSession = Depends(get_session),
    motivo_id: UUID,
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    """
    Elimina un motivo de desecho del sistema.
    
    Esta operación solo se permite si el motivo no está siendo utilizado por ningún registro.
    """
    user_id = current_user.id if current_user else None
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo identificar al usuario autenticado"
        )
        
    await service.delete_motivo_desecho(
        db=db,
        motivo_id=motivo_id
    )
    return {"status_code": status.HTTP_204_NO_CONTENT}

# --- Endpoints para Almacenes ---

@router.post(
    "/almacenes/",
    response_model=AlmacenRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo almacén",
    tags=["Almacenes"]
)
async def crear_almacen(
    *,
    db: AsyncSession = Depends(get_session),
    almacen_in: AlmacenCreate,
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    """
    Crea un nuevo almacén en el sistema.
    
    - **codigo**: Código único del almacén (requerido)
    - **nombre**: Nombre descriptivo del almacén (requerido)
    - **es_principal**: Indica si es el almacén principal (opcional, default=False)
    """
    user_id = current_user.id if current_user else None
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo identificar al usuario autenticado"
        )
        
    return await service.create_almacen(
        db=db,
        almacen_in=almacen_in,
        user_id=user_id
    )

@router.get(
    "/almacenes/",
    response_model=List[AlmacenRead],
    summary="Listar todos los almacenes",
    tags=["Almacenes"]
)
async def listar_almacenes(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a devolver"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo"),
    db: AsyncSession = Depends(get_session),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    """
    Obtiene una lista de almacenes con paginación y filtros opcionales.
    """
    user_id = current_user.id if current_user else None
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo identificar al usuario autenticado"
        )
        
    return await service.get_almacenes(
        db=db,
        skip=skip,
        limit=limit,
        activo=activo
    )

@router.get(
    "/almacenes/{almacen_id}",
    response_model=AlmacenRead,
    summary="Obtener un almacén por ID",
    tags=["Almacenes"]
)
async def obtener_almacen(
    *,
    db: AsyncSession = Depends(get_session),
    almacen_id: UUID,
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    """
    Obtiene los detalles de un almacén específico por su ID.
    """
    user_id = current_user.id if current_user else None
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo identificar al usuario autenticado"
        )
        
    return await service.get_almacen(db=db, almacen_id=almacen_id)

@router.put(
    "/almacenes/{almacen_id}",
    response_model=AlmacenRead,
    summary="Actualizar un almacén",
    tags=["Almacenes"]
)
async def actualizar_almacen(
    *,
    db: AsyncSession = Depends(get_session),
    almacen_id: UUID,
    almacen_in: AlmacenUpdate,
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    """
    Actualiza los datos de un almacén existente.
    
    Solo se actualizarán los campos incluidos en la solicitud.
    """
    user_id = current_user.id if current_user else None
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo identificar al usuario autenticado"
        )
        
    db_almacen = await service.get_almacen(db=db, almacen_id=almacen_id)
    
    return await service.update_almacen(
        db=db,
        db_almacen=db_almacen,
        almacen_in=almacen_in,
        user_id=user_id
    )

@router.delete(
    "/almacenes/{almacen_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un almacén",
    tags=["Almacenes"]
)
async def eliminar_almacen(
    *,
    db: AsyncSession = Depends(get_session),
    almacen_id: UUID,
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    """
    Elimina un almacén del sistema.
    
    No se puede eliminar el almacén principal ni si tiene registros asociados.
    """
    user_id = current_user.id if current_user else None
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo identificar al usuario autenticado"
        )
        
    db_almacen = await service.get_almacen(db=db, almacen_id=almacen_id)
    
    await service.delete_almacen(
        db=db,
        db_almacen=db_almacen,
        user_id=user_id
    )
    
    return {"status_code": status.HTTP_204_NO_CONTENT}
