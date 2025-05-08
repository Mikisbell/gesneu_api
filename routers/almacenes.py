from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_session
from crud.crud_almacen import almacen as crud_almacen
from schemas.almacen import AlmacenCreate, AlmacenRead, AlmacenUpdate

router = APIRouter(
    prefix="/almacenes",
    tags=["almacenes"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[AlmacenRead])
async def read_almacenes(
    session: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve a list of almacenes.
    """
    almacenes = await crud_almacen.get_multi(session, skip=skip, limit=limit)
    return almacenes

@router.post("/", response_model=AlmacenRead, status_code=status.HTTP_201_CREATED)
async def create_almacen(
    *,
    session: AsyncSession = Depends(get_session),
    almacen_in: AlmacenCreate,
):
    """
    Create a new almacen.
    """
    # Optional: Add validation here if needed before creating
    # For example, check if an almacen with the same name already exists
    existing_almacen = await crud_almacen.get_by_name(session, name=almacen_in.nombre) # Assuming get_by_name exists or add it to crud_almacen
    if existing_almacen:
         raise HTTPException(
             status_code=status.HTTP_409_CONFLICT,
             detail="Almacen with this name already exists"
         )

    almacen = await crud_almacen.create(session, obj_in=almacen_in)
    return almacen

@router.get("/{almacen_id}", response_model=AlmacenRead)
async def read_almacen(
    *,
    session: AsyncSession = Depends(get_session),
    almacen_id: UUID,
):
    """
    Retrieve an almacen by ID.
    """
    almacen = await crud_almacen.get(session, id=almacen_id)
    if not almacen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Almacen not found"
        )
    return almacen

@router.put("/{almacen_id}", response_model=AlmacenRead)
async def update_almacen(
    *,
    session: AsyncSession = Depends(get_session),
    almacen_id: UUID,
    almacen_in: AlmacenUpdate,
):
    """
    Update an almacen.
    """
    almacen = await crud_almacen.get(session, id=almacen_id)
    if not almacen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Almacen not found"
        )
    # Optional: Add validation here if needed before updating
    # For example, check if updating the name conflicts with an existing almacen
    if almacen_in.nombre is not None and almacen_in.nombre != almacen.nombre:
         existing_almacen = await crud_almacen.get_by_name(session, name=almacen_in.nombre) # Assuming get_by_name exists or add it
         if existing_almacen and existing_almacen.id != almacen_id:
              raise HTTPException(
                  status_code=status.HTTP_409_CONFLICT,
                  detail="Almacen with this name already exists"
              )

    almacen = await crud_almacen.update(session, db_obj=almacen, obj_in=almacen_in)
    return almacen

@router.delete("/{almacen_id}", response_model=AlmacenRead)
async def delete_almacen(
    *,
    session: AsyncSession = Depends(get_session),
    almacen_id: UUID,
):
    """
    Delete an almacen.
    """
    almacen = await crud_almacen.get(session, id=almacen_id)
    if not almacen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Almacen not found"
        )
    # Optional: Add check if the almacen is in use before deleting
    # For example, check if any Neumaticos are located in this almacen

    almacen = await crud_almacen.remove(session, id=almacen_id)
    return almacen

# NOTE: The `get_by_name` method used in create and update is assumed to exist
# in crud/crud_almacen.py. You might need to add this method there.