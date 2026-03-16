from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate


def get_tasks(
    db: Session,
    current_user: User,
    limit: int,
    offset: int,
    completed: bool | None = None,
):
    query = db.query(Task).filter(Task.user_id == current_user.id)

    if completed is not None:
        query = query.filter(Task.completed == completed)

    total = query.count()

    items = query.order_by(Task.id).offset(offset).limit(limit).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": items,
    }


def get_task_by_id(task_id: int, db: Session, current_user: User):
    return (
        db.query(Task)
        .filter(Task.id == task_id, Task.user_id == current_user.id)
        .first()
    )


def create_task(task_data: TaskCreate, db: Session, current_user: User):
    db_task = Task(
        title=task_data.title,
        description=task_data.description,
        completed=task_data.completed,
        user_id=current_user.id,
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task


def update_task(task_id: int, updated_task: TaskUpdate, db: Session, current_user: User):
    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.user_id == current_user.id)
        .first()
    )

    if task is None:
        return None

    if updated_task.title is not None:
        task.title = updated_task.title

    if updated_task.description is not None:
        task.description = updated_task.description

    if updated_task.completed is not None:
        task.completed = updated_task.completed

    db.commit()
    db.refresh(task)

    return task


def delete_task(task_id: int, db: Session, current_user: User):
    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.user_id == current_user.id)
        .first()
    )

    if task is None:
        return None

    db.delete(task)
    db.commit()

    return task