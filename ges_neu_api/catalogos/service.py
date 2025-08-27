# ges_neu_api/catalogos/service.py

from uuid import UUID
from typing import List, Optional, Union, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from . import crud, models, schemas
from ..core.contracts import CatalogServiceContract

class CatalogosService:
    """
    Servicio para la gestión de catálogos.
    
    Esta clase encapsula toda la lógica de negocio relacionada con
    los catálogos del sistema (Fabricantes, Modelos, Proveedores, etc.).
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    # --- Lógica de negocio para Fabricantes ---

    async def get_all_fabricantes(
        self, 
        skip: int = 0, 
        limit: int = 100,
        activo: Optional[bool] = None
    ) -> List[models.Fabricante]:
        """Obtiene todos los fabricantes con filtro opcional por estado."""
        return await crud.get_all_fabricantes(
            self.db, skip=skip, limit=limit, activo=activo
        )

    async def get_fabricante_by_id(
        self, 
        fabricante_id: UUID
    ) -> models.Fabricante:
        """Obtiene un fabricante por ID."""
        db_fabricante = await crud.get_fabricante(self.db, fabricante_id=fabricante_id)
        if not db_fabricante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Fabricante no encontrado"
            )
        return db_fabricante

    async def create_fabricante(
        self, 
        *, 
        fabricante_in: schemas.FabricanteCreate, 
        user_id: UUID
    ) -> models.Fabricante:
        """Crea un nuevo fabricante."""
        existing = await self.db.execute(
            select(models.Fabricante).where(
                (models.Fabricante.nombre == fabricante_in.nombre) |
                (models.Fabricante.codigo_abreviado == fabricante_in.codigo_abreviado)
            )
        )
        if existing.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un fabricante con este nombre o código"
            )
        return await crud.create_fabricante(
            self.db, obj_in=fabricante_in, user_id=user_id
        )

    async def update_fabricante(
        self, 
        *, 
        fabricante_id: UUID, 
        fabricante_in: schemas.FabricanteUpdate, 
        user_id: UUID
    ) -> models.Fabricante:
        """Actualiza un fabricante."""
        db_fabricante = await self.get_fabricante_by_id(fabricante_id)
        if fabricante_in.nombre or fabricante_in.codigo_abreviado:
            existing = await self.db.execute(
                select(models.Fabricante).where(
                    (models.Fabricante.id != fabricante_id) &
                    (
                        (models.Fabricante.nombre == fabricante_in.nombre) |
                        (models.Fabricante.codigo_abreviado == fabricante_in.codigo_abreviado)
                    )
                )
            )
            if existing.scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe otro fabricante con este nombre o código"
                )
        return await crud.update_fabricante(
            self.db, db_obj=db_fabricante, obj_in=fabricante_in, user_id=user_id
        )

    async def delete_fabricante(
        self, 
        *, 
        fabricante_id: UUID
    ) -> models.Fabricante:
        """Elimina un fabricante."""
        db_fabricante = await self.get_fabricante_by_id(fabricante_id)
        modelos = await self.get_all_modelos(
            fabricante_id=fabricante_id, limit=1
        )
        if modelos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar un fabricante con modelos asociados"
            )
        return await crud.remove_fabricante(self.db, db_obj=db_fabricante)

    # --- Lógica de negocio para Modelos ---

    async def get_all_modelos(
        self, 
        skip: int = 0, 
        limit: int = 100,
        fabricante_id: Optional[UUID] = None,
        activo: Optional[bool] = None
    ) -> List[models.ModeloNeumatico]:
        """Obtiene todos los modelos con filtros opcionales."""
        return await crud.get_all_modelos(
            self.db, 
            skip=skip, 
            limit=limit, 
            fabricante_id=fabricante_id,
            activo=activo
        )

    async def get_modelo_by_id(
        self, 
        modelo_id: UUID
    ) -> models.ModeloNeumatico:
        """Obtiene un modelo por ID."""
        db_modelo = await crud.get_modelo(self.db, modelo_id=modelo_id)
        if not db_modelo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Modelo no encontrado"
            )
        return db_modelo

    async def create_modelo(
        self, 
        *, 
        modelo_in: schemas.ModeloNeumaticoCreate, 
        user_id: UUID
    ) -> models.ModeloNeumatico:
        """Crea un nuevo modelo."""
        fabricante = await self.get_fabricante_by_id(modelo_in.fabricante_id)
        if not fabricante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El fabricante especificado no existe"
            )
        existing = await self.db.execute(
            select(models.ModeloNeumatico).where(
                (models.ModeloNeumatico.fabricante_id == modelo_in.fabricante_id) &
                (models.ModeloNeumatico.nombre_modelo == modelo_in.nombre_modelo)
            )
        )
        if existing.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un modelo con este nombre para el fabricante"
            )
        return await crud.create_modelo(self.db, obj_in=modelo_in, user_id=user_id)

    async def update_modelo(
        self, 
        *, 
        modelo_id: UUID, 
        modelo_in: schemas.ModeloNeumaticoUpdate, 
        user_id: UUID
    ) -> models.ModeloNeumatico:
        """Actualiza un modelo."""
        db_modelo = await self.get_modelo_by_id(modelo_id)
        if modelo_in.fabricante_id and modelo_in.fabricante_id != db_modelo.fabricante_id:
            fabricante = await self.get_fabricante_by_id(modelo_in.fabricante_id)
            if not fabricante:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="El fabricante especificado no existe"
                )
        if modelo_in.nombre_modelo:
            existing = await self.db.execute(
                select(models.ModeloNeumatico).where(
                    (models.ModeloNeumatico.id != modelo_id) &
                    (models.ModeloNeumatico.fabricante_id == (modelo_in.fabricante_id or db_modelo.fabricante_id)) &
                    (models.ModeloNeumatico.nombre_modelo == modelo_in.nombre_modelo)
                )
            )
            if existing.scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe otro modelo con este nombre para el fabricante"
                )
        return await crud.update_modelo(
            self.db, db_obj=db_modelo, obj_in=modelo_in, user_id=user_id
        )

    async def delete_modelo(
        self, 
        *, 
        modelo_id: UUID
    ) -> models.ModeloNeumatico:
        """Elimina un modelo."""
        db_modelo = await self.get_modelo_by_id(modelo_id)
        return await crud.remove_modelo(self.db, db_obj=db_modelo)

    # --- Lógica de negocio para Proveedores ---

    async def get_all_proveedores(
        self, 
        skip: int = 0, 
        limit: int = 100,
        activo: Optional[bool] = None,
        tipo: Optional[str] = None
    ) -> List[models.Proveedor]:
        """Obtiene todos los proveedores con filtros opcionales."""
        return await crud.get_all_proveedores(
            self.db, skip=skip, limit=limit, activo=activo, tipo=tipo
        )

    async def get_proveedor_by_id(
        self, 
        proveedor_id: UUID
    ) -> models.Proveedor:
        """Obtiene un proveedor por ID."""
        db_proveedor = await crud.get_proveedor(self.db, proveedor_id=proveedor_id)
        if not db_proveedor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Proveedor no encontrado"
            )
        return db_proveedor

    async def create_proveedor(
        self, 
        *, 
        proveedor_in: schemas.ProveedorCreate, 
        user_id: UUID
    ) -> models.Proveedor:
        """Crea un nuevo proveedor."""
        if proveedor_in.ruc:
            existing = await crud.get_proveedor_by_ruc(self.db, ruc=proveedor_in.ruc)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un proveedor con este RUC"
                )
        if proveedor_in.email:
            existing = await crud.get_proveedor_by_email(self.db, email=proveedor_in.email)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un proveedor con este email"
                )
        return await crud.create_proveedor(self.db, obj_in=proveedor_in, user_id=user_id)

    async def update_proveedor(
        self, 
        *, 
        proveedor_id: UUID, 
        proveedor_in: schemas.ProveedorUpdate, 
        user_id: UUID
    ) -> models.Proveedor:
        """Actualiza un proveedor existente."""
        db_proveedor = await self.get_proveedor_by_id(proveedor_id)
        if proveedor_in.ruc and proveedor_in.ruc != db_proveedor.ruc:
            existing = await crud.get_proveedor_by_ruc(self.db, ruc=proveedor_in.ruc)
            if existing and existing.id != proveedor_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe otro proveedor con este RUC"
                )
        if proveedor_in.email and proveedor_in.email != db_proveedor.email:
            existing = await crud.get_proveedor_by_email(self.db, email=proveedor_in.email)
            if existing and existing.id != proveedor_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe otro proveedor con este email"
                )
        return await crud.update_proveedor(
            self.db, db_obj=db_proveedor, obj_in=proveedor_in, user_id=user_id
        )

    async def delete_proveedor(
        self, 
        *, 
        proveedor_id: UUID
    ) -> models.Proveedor:
        """Elimina un proveedor."""
        db_proveedor = await self.get_proveedor_by_id(proveedor_id)
        return await crud.remove_proveedor(self.db, db_obj=db_proveedor)

    # --- Lógica de negocio para Motivos de Desecho ---

    async def get_all_motivos_desecho(
        self, 
        skip: int = 0, 
        limit: int = 100,
        activo: Optional[bool] = None
    ) -> List[models.MotivoDesecho]:
        """Obtiene todos los motivos de desecho con filtros opcionales."""
        return await crud.get_all_motivos_desecho(
            self.db, skip=skip, limit=limit, activo=activo
        )

    async def get_motivo_desecho_by_id(
        self, 
        motivo_id: UUID
    ) -> models.MotivoDesecho:
        """Obtiene un motivo de desecho por su ID."""
        db_motivo = await crud.get_motivo_desecho(self.db, motivo_id=motivo_id)
        if not db_motivo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Motivo de desecho no encontrado"
            )
        return db_motivo

    async def create_motivo_desecho(
        self, 
        *, 
        motivo_in: schemas.MotivoDesechoCreate, 
        user_id: UUID
    ) -> models.MotivoDesecho:
        """Crea un nuevo motivo de desecho."""
        existing = await crud.get_motivo_desecho_by_codigo(self.db, codigo=motivo_in.codigo)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un motivo de desecho con este código"
            )
        return await crud.create_motivo_desecho(
            self.db, obj_in=motivo_in, user_id=user_id
        )

    async def update_motivo_desecho(
        self, 
        *, 
        motivo_id: UUID, 
        motivo_in: Union[schemas.MotivoDesechoUpdate, Dict[str, Any]], 
        user_id: UUID
    ) -> models.MotivoDesecho:
        """Actualiza un motivo de desecho existente."""
        db_motivo = await self.get_motivo_desecho_by_id(motivo_id)
        if isinstance(motivo_in, dict):
            codigo = motivo_in.get('codigo')
        else:
            codigo = motivo_in.codigo
        if codigo and codigo != db_motivo.codigo:
            existing = await crud.get_motivo_desecho_by_codigo(self.db, codigo=codigo)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe otro motivo de desecho con este código"
                )
        return await crud.update_motivo_desecho(
            self.db, db_obj=db_motivo, obj_in=motivo_in, user_id=user_id
        )

    async def delete_motivo_desecho(
        self, 
        *, 
        motivo_id: UUID
    ) -> models.MotivoDesecho:
        """Elimina un motivo de desecho."""
        db_motivo = await self.get_motivo_desecho_by_id(motivo_id)
        return await crud.remove_motivo_desecho(self.db, db_obj=db_motivo)

    # --- Servicios para Almacen ---

    async def get_almacen(
        self,
        almacen_id: UUID
    ) -> models.Almacen:
        """Obtiene un almacén por su ID."""
        db_almacen = await crud.get_almacen(self.db, almacen_id=almacen_id)
        if not db_almacen:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Almacén con ID {almacen_id} no encontrado"
            )
        return db_almacen

    async def get_almacenes(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        activo: Optional[bool] = None
    ) -> List[models.Almacen]:
        """Obtiene una lista de almacenes con paginación y filtros opcionales."""
        return await crud.get_all_almacenes(
            self.db,
            skip=skip,
            limit=limit,
            activo=activo
        )
    
    # ... (otros métodos de Almacen y ParametroInventario seguirían el mismo patrón) ...
