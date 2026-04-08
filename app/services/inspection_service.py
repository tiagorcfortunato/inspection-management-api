from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.services.ai_service import get_ai_service

from app.core.enums import (
    DamageType,
    SeverityLevel,
    InspectionStatus,
    SortOrder,
    InspectionSortField,
)
from app.models.inspection import Inspection
from app.models.user import User
from app.schemas.inspection import InspectionCreate, InspectionUpdate


def get_inspections(
    db: Session,
    current_user: User,
    severity: SeverityLevel | None = None,
    status: InspectionStatus | None = None,
    damage_type: DamageType | None = None,
    limit: int = 10,
    offset: int = 0,
    sort_by: InspectionSortField = InspectionSortField.reported_at,
    order: SortOrder = SortOrder.desc,
):
    query = db.query(Inspection).filter(Inspection.user_id == current_user.id)

    if severity is not None:
        query = query.filter(Inspection.severity == severity.value)

    if status is not None:
        query = query.filter(Inspection.status == status.value)

    if damage_type is not None:
        query = query.filter(Inspection.damage_type == damage_type.value)

    total = query.count()

    allowed_sort_fields = {
        "id": Inspection.id,
        "reported_at": Inspection.reported_at,
        "severity": Inspection.severity,
        "status": Inspection.status,
        "damage_type": Inspection.damage_type,
        "location_code": Inspection.location_code,
    }

    sort_column = allowed_sort_fields[sort_by.value]

    if order == SortOrder.asc:
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    inspections = query.limit(limit).offset(offset).all()

    return {
        "total": total,
        "items": inspections,
    }


def get_all_inspections(
    db: Session,
    severity: SeverityLevel | None = None,
    status: InspectionStatus | None = None,
    damage_type: DamageType | None = None,
    limit: int = 10,
    offset: int = 0,
    sort_by: InspectionSortField = InspectionSortField.reported_at,
    order: SortOrder = SortOrder.desc,
):
    query = db.query(Inspection)

    if severity is not None:
        query = query.filter(Inspection.severity == severity.value)

    if status is not None:
        query = query.filter(Inspection.status == status.value)

    if damage_type is not None:
        query = query.filter(Inspection.damage_type == damage_type.value)

    total = query.count()

    allowed_sort_fields = {
        "id": Inspection.id,
        "reported_at": Inspection.reported_at,
        "severity": Inspection.severity,
        "status": Inspection.status,
        "damage_type": Inspection.damage_type,
        "location_code": Inspection.location_code,
    }

    sort_column = allowed_sort_fields[sort_by.value]

    if order == SortOrder.asc:
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    raw = query.limit(limit).offset(offset).all()

    items = [
        {
            "id": insp.id,
            "location_code": insp.location_code,
            "damage_type": insp.damage_type,
            "severity": insp.severity,
            "status": insp.status,
            "notes": insp.notes,
            "reported_at": insp.reported_at,
            "user_id": insp.user_id,
            "user_email": insp.owner.email if insp.owner else "unknown",
        }
        for insp in raw
    ]

    return {
        "total": total,
        "items": items,
    }


def admin_update_inspection(
    inspection_id: int,
    inspection_data: InspectionUpdate,
    db: Session,
):
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()

    if inspection is None:
        return None

    if inspection_data.location_code is not None:
        inspection.location_code = inspection_data.location_code

    if inspection_data.damage_type is not None:
        inspection.damage_type = inspection_data.damage_type.value

    if inspection_data.severity is not None:
        inspection.severity = inspection_data.severity.value

    if inspection_data.status is not None:
        inspection.status = inspection_data.status.value

    if inspection_data.notes is not None:
        inspection.notes = inspection_data.notes

    db.commit()
    db.refresh(inspection)

    return inspection


def admin_delete_inspection(inspection_id: int, db: Session):
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    return inspection


def get_inspection_by_id(inspection_id: int, db: Session, current_user: User):
    return (
        db.query(Inspection)
        .filter(
            Inspection.id == inspection_id,
            Inspection.user_id == current_user.id,
        )
        .first()
    )


def create_inspection(
    inspection_data: InspectionCreate,
    db: Session,
    current_user: User,
):
    db_inspection = Inspection(
        location_code=inspection_data.location_code,
        damage_type=inspection_data.damage_type.value if inspection_data.damage_type else DamageType.pothole.value,
        severity=inspection_data.severity.value if inspection_data.severity else SeverityLevel.medium.value,
        status=InspectionStatus.reported.value,
        notes=inspection_data.notes,
        image_data=inspection_data.image_data,
        user_id=current_user.id,
    )

    db.add(db_inspection)
    db.commit()
    db.refresh(db_inspection)

    return db_inspection


async def process_inspection_with_ai(inspection_id: int) -> None:
    db = SessionLocal()
    try:
        inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()

        if inspection is None or (not inspection.notes and not inspection.image_data):
            return

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
    except Exception as e:
        print(f"[AI] process_inspection_with_ai failed for id={inspection_id}: {e}")
    finally:
        db.close()


def update_inspection(
    inspection_id: int,
    inspection_data: InspectionUpdate,
    db: Session,
    current_user: User,
):
    inspection = (
        db.query(Inspection)
        .filter(
            Inspection.id == inspection_id,
            Inspection.user_id == current_user.id,
        )
        .first()
    )

    if inspection is None:
        return None

    if inspection_data.location_code is not None:
        inspection.location_code = inspection_data.location_code

    if inspection_data.damage_type is not None:
        inspection.damage_type = inspection_data.damage_type.value

    if inspection_data.severity is not None:
        inspection.severity = inspection_data.severity.value

    if inspection_data.status is not None:
        inspection.status = inspection_data.status.value

    if inspection_data.notes is not None:
        inspection.notes = inspection_data.notes

    db.commit()
    db.refresh(inspection)

    return inspection