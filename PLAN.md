# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

duplicate-table-claims-fix

## Roadmap

### duplicate-table-claims-fix — Fix duplicate table row claims in document parser

Status: done

Acceptance:
- Table rows starting with `|` no longer generate duplicate claims
- Line-by-line claim extraction skips table rows
- _extract_table_claims exclusively handles table row parsing
- All existing tests pass
- Contradiction detection still works correctly

Implementation: `backend/app/services/document_parser.py`

Tests: `backend/tests/test_contradiction_detection.py::TestDocumentParser::test_extract_table_claims`

