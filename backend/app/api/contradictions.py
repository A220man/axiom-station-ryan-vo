from fastapi import APIRouter
from typing import List

from app.models.schemas import Contradiction

router = APIRouter()


@router.get("/", response_model=List[Contradiction])
async def list_contradictions(
    phase: str = None,
    lesson_id: str = None,
    severity: str = None,
):
    return []


@router.get("/stats")
async def get_stats():
    return {
        "total": 0,
        "by_phase": {},
        "by_severity": {},
    }