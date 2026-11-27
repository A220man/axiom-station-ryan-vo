# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

table-row-claims-fix

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

### table-row-claims-fix — Extract per-row table claims so table cell values feed contradiction detection

Status: done

Acceptance:
- Each table data row produces exactly one claim with 'Table row:' text
- Table claim metadata includes table_header and row_data
- Numeric values inside table cells (e.g. 1.3B vs 4.4B) are detected as contradictions
- No duplicate claims across document content
- All existing backend tests pass

Implementation: `backend/app/services/document_parser.py`

Tests: `backend/tests/test_table_claims_enhanced.py::TestEnhancedTableClaims::test_table_claims_exact_count_and_no_duplicates`

