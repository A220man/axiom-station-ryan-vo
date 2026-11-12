import pytest
from app.services.document_parser import parse_document
from app.models.schemas import Claim, SectionType


class TestEnhancedTableClaims:
    def test_table_claims_exact_count_and_no_duplicates(self):
        \"\"\"Test that table rows generate exactly 2 claims and no duplicates.
        
        Verifies the duplicate-table-claims-fix by ensuring:
        1. Each table row generates exactly one claim (2 rows = 2 claims)
        2. No duplicate claims across all document content
        3. Claims are correctly extracted from table structure
        \"\"\"
        content = \"\"\"# Test

## Comparison Table
| Model | Params |
|-------|--------|
| A     | 1.3B   |
| B     | 4.4B   |
\"\"\"
        result = parse_document(content, \"phase-12\", \"04-flamingo-gated-cross-attention\")
        table_claims = [c for c in result.claims if c.section_type == SectionType.TABLE]
        
        # Verify exactly 2 table claims for rows A and B (no more, no less)
        assert len(table_claims) == 2, f\"Expected exactly 2 table claims, got {len(table_claims)}\"
        
        # Verify each table claim has correct structure
        for claim in table_claims:
            assert claim.section_type == SectionType.TABLE
            assert claim.text.startswith(\"Table row:\")
            assert \"table_header\" in claim.metadata
            assert \"row_data\" in claim.metadata
        
        # Verify no duplicate claims in the entire document
        claim_texts = [c.text for c in result.claims]
        unique_texts = set(claim_texts)
        assert len(claim_texts) == len(unique_texts), f\"Found duplicate claims: {claim_texts}\"