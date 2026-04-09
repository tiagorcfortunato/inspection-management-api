"""
app.routers.admin — Admin-Only Inspection Endpoints

Provides cross-user inspection management for admins. Unlike the user
endpoints, these are not scoped to the current user — admins can list,
update, and delete any inspection across all users.

All endpoints require the admin role (enforced via require_admin dependency).
The admin list response includes user_email for accountability.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.core.enums import DamageType, SeverityLevel, InspectionStatus, SortOrder, InspectionSortField
from app.models.user import User
from app.schemas.inspection import InspectionUpdate, InspectionAdminListResponse, InspectionResponse
from app.services.inspection_service import get_all_inspections, admin_update_inspection, get_inspection_by_id_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/inspections", response_model=InspectionAdminListResponse)
def list_all_inspections(
    severity: SeverityLevel | None = None,
    status: InspectionStatus | None = None,
    damage_type: DamageType | None = None,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
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
    inspection = get_inspection_by_id_admin(inspection_id, db)

    if inspection is None:
        raise HTTPException(status_code=404, detail="Inspection not found")

    db.delete(inspection)
    db.commit()
