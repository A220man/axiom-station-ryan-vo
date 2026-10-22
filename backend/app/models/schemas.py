from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum


class SectionType(str, Enum):
    HOOK = "hook"
    BODY = "body"
    TABLE = "table"
    EXERCISE = "exercise"
    LEARNING_OBJECTIVES = "learning_objectives"
    PROBLEM = "problem"
    CONCEPT = "concept"
    SHIP_IT = "ship_it"


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Claim(BaseModel):
    id: str
    section_type: SectionType
    text: str
    line_start: int
    line_end: int
    metadata: dict = Field(default_factory=dict)


class Contradiction(BaseModel):
    id: str
    lesson_id: str
    phase: str
    claim_a: Claim
    claim_b: Claim
    severity: Severity
    description: str
    suggestion: Optional[str] = None


class DocumentParseResult(BaseModel):
    phase: str
    lesson_id: str
    title: str
    claims: List[Claim]
    raw_sections: dict


class AnalysisRequest(BaseModel):
    content: str
    phase: str
    lesson_id: str


class AnalysisResponse(BaseModel):
    document: DocumentParseResult
    contradictions: List[Contradiction]
    summary: dict