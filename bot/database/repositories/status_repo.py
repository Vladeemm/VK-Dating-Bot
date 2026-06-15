"""Репозиторий для операций со статусами пользователя."""

from typing import Any, Dict, Optional
from datetime import datetime
from bot.database.models import Status
from bot.database.session import session


def get_status_by_user_id(user_id: int) -> Optional[Status]:
    return session.query(Status).filter(Status.user_vk_id == user_id).first()


def create_status(user_id: int, step: str, search_criteria: Optional[Dict[str, Any]] = None,
                  list_applicants: Optional[list[int]] = None) -> Status:
    status = Status(
        user_vk_id=user_id,
        step=step,
        search_criteria=search_criteria or {},
        list_applicants=list_applicants or [],
        step_datetime=datetime.now()
    )
    session.add(status)
    session.commit()
    return status


def update_status_step(status: Status, step: str) -> Status:
    status.step = step
    status.step_datetime = datetime.now()
    session.commit()
    return status


def update_search_criteria(status: Status, criteria: Dict[str, Any]) -> Status:
    status.search_criteria = criteria
    status.step_datetime = datetime.now()
    session.commit()
    return status


def update_list_applicants(status: Status, ids_list: Optional[list[int]]) -> Status:
    status.list_applicants = ids_list
    session.commit()
    return status
