"""Репозиторий для операций со статусами пользователя."""

from datetime import datetime
from typing import Any, Dict, Optional

from ..models import Status
from ..session import get_session


def get_status_by_user_id(user_id: int) -> Optional[Status]:
    with get_session() as session:
        status = session.query(Status).filter(Status.user_vk_id == user_id).first()
        if status:
            _ = status.step
            _ = status.search_criteria
            _ = status.list_applicants
        return status


def create_status(
    user_id: int,
    step: str,
    search_criteria: Optional[Dict[str, Any]] = None,
    list_applicants: Optional[list[int]] = None,
) -> Status:
    with get_session() as session:
        status = Status(
            user_vk_id=user_id,
            step=step,
            search_criteria=search_criteria or {},
            list_applicants=list_applicants or [],
            step_datetime=datetime.now(),
        )
        session.add(status)
        return status


def update_status_step(status: Status, step: str) -> Status:
    with get_session() as session:
        db_status = session.merge(status)
        db_status.step = step
        db_status.step_datetime = datetime.now()
        return db_status


def update_search_criteria(status: Status, criteria: Dict[str, Any]) -> Status:
    with get_session() as session:
        db_status = session.merge(status)
        db_status.search_criteria = criteria
        db_status.step_datetime = datetime.now()
        return db_status


def update_list_applicants(status: Status, ids_list: Optional[list[int]]) -> Status:
    with get_session() as session:
        db_status = session.merge(status)
        db_status.list_applicants = ids_list
        return db_status
