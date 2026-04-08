from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.core.enums import (
    DamageType,
    SeverityLevel,
    InspectionStatus,
    SortOrder,
    InspectionSortField,
)
from app.models.user import User
from app.schemas.inspection import (
    InspectionCreate,
    InspectionUpdate,
    InspectionResponse,
    InspectionListResponse,
)
from app.services import inspection_service

router = APIRouter(tags=["inspections"])


@router.get("/inspections", response_model=InspectionListResponse)
def get_inspections(
    severity: SeverityLevel | None = None,
    status: InspectionStatus | None = None,
    damage_type: DamageType | None = None,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    sort_by: InspectionSortField = InspectionSortField.reported_at,
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


@router.post(
    "/inspections",
    response_model=InspectionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_inspection(
    inspection: InspectionCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    created = inspection_service.create_inspection(inspection, db, current_user)
    background_tasks.add_task(
        inspection_service.process_inspection_with_ai,
        inspection_id=created.id,
    )
    return created


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


@router.post("/inspections/{inspection_id}/retry-ai")
async def retry_ai(
    inspection_id: int,
    db: Session = Depends(get_db),
):
    """Debug endpoint: retry AI processing and return the error if it fails."""
    import traceback
    from app.models.inspection import Inspection
    from app.services.ai_service import get_ai_service

    inspection = db.query(Inspection).filter(
        Inspection.id == inspection_id,
    ).first()

    if inspection is None:
        raise HTTPException(status_code=404, detail="Inspection not found")

    try:
        ai_service = get_ai_service()
        result = await ai_service.classify_inspection(
            notes=inspection.notes,
            image_data=inspection.image_data,
        )
        inspection.damage_type = result.damage_type.value
        inspection.severity = result.severity.value
        inspection.ai_rationale = result.rationale
        inspection.is_ai_processed = True
        db.commit()
        return {"status": "success", "result": result.model_dump()}
    except Exception as e:
        return {"status": "error", "error": str(e), "traceback": traceback.format_exc()}


@router.delete("/inspections/{inspection_id}", status_code=status.HTTP_204_NO_CONTENT)
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