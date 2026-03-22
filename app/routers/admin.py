from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.core.enums import DamageType, SeverityLevel, InspectionStatus, SortOrder, InspectionSortField
from app.models.user import User
from app.schemas.inspection import InspectionUpdate, InspectionAdminListResponse, InspectionResponse
from app.services.inspection_service import get_all_inspections, admin_update_inspection, admin_delete_inspection

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/inspections", response_model=InspectionAdminListResponse)
def list_all_inspections(
    severity: SeverityLevel | None = None,
    status: InspectionStatus | None = None,
    damage_type: DamageType | None = None,
    limit: int = 10,
    offset: int = 0,
    sort_by: InspectionSortField = InspectionSortField.reported_at,
    order: SortOrder = SortOrder.desc,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return get_all_inspections(
        db=db,
        severity=severity,
        status=status,
        damage_type=damage_type,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        order=order,
    )


@router.put("/inspections/{inspection_id}", response_model=InspectionResponse)
def update_any_inspection(
    inspection_id: int,
    inspection: InspectionUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    updated = admin_update_inspection(inspection_id, inspection, db)

    if updated is None:
        raise HTTPException(status_code=404, detail="Inspection not found")

    return updated


@router.delete("/inspections/{inspection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_any_inspection(
    inspection_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    inspection = admin_delete_inspection(inspection_id, db)

    if inspection is None:
        raise HTTPException(status_code=404, detail="Inspection not found")

    db.delete(inspection)
    db.commit()
