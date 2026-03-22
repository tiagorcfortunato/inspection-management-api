from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.core.enums import DamageType, SeverityLevel, InspectionStatus, SortOrder, InspectionSortField
from app.models.user import User
from app.schemas.inspection import InspectionListResponse
from app.services.inspection_service import get_all_inspections

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/inspections", response_model=InspectionListResponse)
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
