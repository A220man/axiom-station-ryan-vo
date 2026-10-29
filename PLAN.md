# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

contradiction-detection-engine

## Roadmap

### contradiction-detection-engine — Contradiction Detection Engine

Status: done

Acceptance:
- Parse markdown documents with structured lesson metadata
- Detect self-contradictions between hook/body/table/exercise sections
- Report factual inconsistencies with severity levels
- Expose REST API for document analysis

Implementation: `backend/app/services/document_parser.py`, `backend/app/services/contradiction_engine.py`, `backend/app/api/documents.py`, `backend/app/api/contradictions.py`, `backend/app/models/schemas.py`

Tests: `backend/tests/test_contradiction_detection.py`, `backend/tests/test_api.py`

### document-parser — Markdown Document Parser

Status: done

Acceptance:
- Extract phase, lesson, section structure from markdown
- Handle cross-reference links and tables
- Output structured JSON for analysis

Implementation: `backend/app/services/document_parser.py`

Tests: `backend/tests/test_contradiction_detection.py::TestDocumentParser`

### web-dashboard — Web Dashboard for Contradiction Review

Status: done

Acceptance:
- Display detected contradictions with source context
- Filter by phase, lesson, severity
- Export findings as JSON/CSV

Implementation: `frontend/src/components/Analyzer.tsx`, `frontend/src/components/ContradictionTable.tsx`, `frontend/src/components/FilterBar.tsx`, `frontend/src/hooks/useAnalysis.ts`, `frontend/src/api/client.ts`

Tests: `frontend/src/components/Analyzer.test.tsx`

