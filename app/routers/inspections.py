from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.core.enums import DamageType, SeverityLevel, InspectionStatus, SortOrder
from app.models.user import User
from app.schemas.inspection import (
    InspectionCreate,
    InspectionUpdate,
    InspectionResponse,
    InspectionListResponse,
)
from app.services import inspection_service

router = APIRouter()


@router.get("/inspections", response_model=InspectionListResponse)
def get_inspections(
    severity: SeverityLevel | None = None,
    status: InspectionStatus | None = None,
    damage_type: DamageType | None = None,
    limit: int = 10,
    offset: int = 0,
    sort_by: str = "reported_at",
    order: SortOrder = SortOrder.desc,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return inspection_service.get_inspections(
        db=db,
        current_user=current_user,
        severity=severity,
        status=status,
        damage_type=damage_type,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        order=order,
    )


@router.get("/inspections/{inspection_id}", response_model=InspectionResponse)
def get_inspection(
    inspection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    inspection = inspection_service.get_inspection_by_id(
        inspection_id,
        db,
        current_user,
    )

    if inspection is None:
        raise HTTPException(status_code=404, detail="Inspection not found")

    return inspection


@router.post("/inspections", response_model=InspectionResponse)
def create_inspection(
    inspection: InspectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return inspection_service.create_inspection(
        inspection,
        db,
        current_user,
    )


@router.put("/inspections/{inspection_id}", response_model=InspectionResponse)
def update_inspection(
    inspection_id: int,
    inspection: InspectionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    updated_inspection = inspection_service.update_inspection(
        inspection_id,
        inspection,
        db,
        current_user,
    )

    if updated_inspection is None:
        raise HTTPException(status_code=404, detail="Inspection not found")

    return updated_inspection


@router.delete("/inspections/{inspection_id}")
def delete_inspection(
    inspection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    inspection = inspection_service.get_inspection_by_id(
        inspection_id,
        db,
        current_user,
    )

    if inspection is None:
        raise HTTPException(status_code=404, detail="Inspection not found")

    db.delete(inspection)
    db.commit()

    return {"message": "Inspection deleted"}