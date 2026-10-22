from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List
import json

from app.models.schemas import AnalysisRequest, AnalysisResponse, Contradiction, DocumentParseResult
from app.services.document_parser import parse_document
from app.services.contradiction_engine import analyze_document

router = APIRouter()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_document_endpoint(request: AnalysisRequest):
    try:
        document = parse_document(request.content, request.phase, request.lesson_id)
        contradictions = analyze_document(document)

        summary = {
            "total_claims": len(document.claims),
            "total_contradictions": len(contradictions),
            "by_severity": {},
            "by_section": {},
        }

        for c in contradictions:
            sev = c.severity.value
            summary["by_severity"][sev] = summary["by_severity"].get(sev, 0) + 1
            sec = c.claim_a.section_type.value
            summary["by_section"][sec] = summary["by_section"].get(sec, 0) + 1

        return AnalysisResponse(
            document=document,
            contradictions=contradictions,
            summary=summary,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyze/file", response_model=AnalysisResponse)
async def analyze_file_endpoint(
    file: UploadFile = File(...),
    phase: str = Form(...),
    lesson_id: str = Form(...),
):
    content = await file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded")

    request = AnalysisRequest(content=text, phase=phase, lesson_id=lesson_id)
    return await analyze_document_endpoint(request)


@router.get("/contradictions/{lesson_id}", response_model=List[Contradiction])
async def get_contradictions(lesson_id: str):
    return []


@router.get("/documents/{lesson_id}", response_model=DocumentParseResult)
async def get_document(lesson_id: str):
    raise HTTPException(status_code=404, detail="Document not found. Use POST /analyze to analyze a document.")