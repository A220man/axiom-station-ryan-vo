import re
from typing import List, Dict, Optional, Tuple
from difflib import SequenceMatcher

from app.models.schemas import Claim, Contradiction, Severity, DocumentParseResult, SectionType


class ContradictionEngine:
    def __init__(self):
        self.numeric_pattern = re.compile(r"(\d+(?:\.\d+)?)\s*(billion|million|thousand|k|m|b|gpu|hours?|years?|params?|tokens?|entries|pairs|context|ms|mb|gb|kb)")
        self.comparison_pattern = re.compile(r"(vs|versus|compared to|conflicts with|contradicts|sum to|total|maximum|minimum|exceeds|fills|reaches)")
        self.quantity_pattern = re.compile(r"(\d+(?:,\d{3})*(?:\.\d+)?)\s*(billion|million|thousand|k|m|b|gpu|hours?|years?|params?|tokens?|entries|pairs|context|ms|mb|gb|kb)")

    def analyze(self, document: DocumentParseResult) -> List[Contradiction]:
        contradictions = []
        claims_by_section = self._group_claims_by_section(document.claims)

        for section_a, claims_a in claims_by_section.items():
            for section_b, claims_b in claims_by_section.items():
                if section_a >= section_b:
                    continue
                contradictions.extend(self._compare_sections(document, claims_a, claims_b, section_a, section_b))

        contradictions.extend(self._check_self_contradictions(document))
        contradictions.extend(self._check_numeric_consistency(document))
        contradictions.extend(self._check_count_consistency(document))

        return contradictions

    def _group_claims_by_section(self, claims: List[Claim]) -> Dict[SectionType, List[Claim]]:
        grouped = {}
        for claim in claims:
            if claim.section_type not in grouped:
                grouped[claim.section_type] = []
            grouped[claim.section_type].append(claim)
        return grouped

    def _compare_sections(
        self,
        document: DocumentParseResult,
        claims_a: List[Claim],
        claims_b: List[Claim],
        section_a: SectionType,
        section_b: SectionType,
    ) -> List[Contradiction]:
        contradictions = []

        for claim_a in claims_a:
            for claim_b in claims_b:
                contradiction = self._check_claim_pair(document, claim_a, claim_b)
                if contradiction:
                    contradictions.append(contradiction)

        return contradictions

    def _check_claim_pair(
        self, document: DocumentParseResult, claim_a: Claim, claim_b: Claim
    ) -> Optional[Contradiction]:
        text_a = claim_a.text.lower()
        text_b = claim_b.text.lower()

        nums_a = self._extract_quantities(text_a)
        nums_b = self._extract_quantities(text_b)

        for qty_a in nums_a:
            for qty_b in nums_b:
                if self._quantities_conflict(qty_a, qty_b, text_a, text_b):
                    return Contradiction(
                        id=f"contr-{document.lesson_id}-{claim_a.id}-{claim_b.id}",
                        lesson_id=document.lesson_id,
                        phase=document.phase,
                        claim_a=claim_a,
                        claim_b=claim_b,
                        severity=Severity.ERROR,
                        description=f"Numeric contradiction: '{qty_a['original']}' vs '{qty_b['original']}'",
                        suggestion=f"Verify which value is correct: {qty_a['original']} ({claim_a.section_type.value}) or {qty_b['original']} ({claim_b.section_type.value})",
                    )

        if self._semantic_conflict(text_a, text_b):
            return Contradiction(
                id=f"contr-{document.lesson_id}-{claim_a.id}-{claim_b.id}",
                lesson_id=document.lesson_id,
                phase=document.phase,
                claim_a=claim_a,
                claim_b=claim_b,
                severity=Severity.WARNING,
                description=f"Potential semantic contradiction between {claim_a.section_type.value} and {claim_b.section_type.value}",
                suggestion="Review both statements for consistency",
            )

        return None

    def _extract_quantities(self, text: str) -> List[Dict]:
        quantities = []
        for match in self.quantity_pattern.finditer(text):
            value_str = match.group(1).replace(",", "")
            unit = match.group(2)
            try:
                value = float(value_str)
                normalized = self._normalize_quantity(value, unit)
                quantities.append({
                    "value": value,
                    "unit": unit,
                    "normalized": normalized,
                    "original": match.group(0),
                })
            except ValueError:
                pass
        return quantities

    def _normalize_quantity(self, value: float, unit: str) -> float:
        multipliers = {
            "billion": 1e9, "b": 1e9,
            "million": 1e6, "m": 1e6,
            "thousand": 1e3, "k": 1e3,
            "gpu": 1, "hours": 1, "hour": 1,
            "years": 1, "year": 1,
            "params": 1, "tokens": 1, "entries": 1, "pairs": 1,
            "context": 1, "ms": 1, "mb": 1, "gb": 1, "kb": 1,
        }
        return value * multipliers.get(unit, 1)

    def _quantities_conflict(self, qty_a: Dict, qty_b: Dict, text_a: str, text_b: str) -> bool:
        if qty_a["unit"] != qty_b["unit"]:
            return False

        if abs(qty_a["normalized"] - qty_b["normalized"]) < 0.01 * max(qty_a["normalized"], qty_b["normalized"]):
            return False

        if "sum to" in text_a or "total" in text_a:
            return False

        if self._are_related_quantities(text_a, text_b):
            return True

        return True

    def _are_related_quantities(self, text_a: str, text_b: str) -> bool:
        keywords = ["llm", "model", "params", "tokens", "context", "codebook", "gpu", "hours", "years", "pairs", "entries"]
        return any(kw in text_a and kw in text_b for kw in keywords)

    def _semantic_conflict(self, text_a: str, text_b: str) -> bool:
        conflict_pairs = [
            ("in one forward pass", "diffusion loop"),
            ("annual", "per quarter"),
            ("three", "four"),
            ("2x", "4x"),
            ("half", "quarter"),
        ]
        for a, b in conflict_pairs:
            if a in text_a and b in text_b:
                return True
            if a in text_b and b in text_a:
                return True
        return False

    def _check_self_contradictions(self, document: DocumentParseResult) -> List[Contradiction]:
        contradictions = []
        claims = document.claims

        for i, claim_a in enumerate(claims):
            for claim_b in claims[i+1:]:
                if claim_a.section_type == claim_b.section_type:
                    continue
                text_a = claim_a.text.lower()
                text_b = claim_b.text.lower()

                if "three" in text_a and "four" in text_b:
                    contradictions.append(Contradiction(
                        id=f"contr-{document.lesson_id}-self-{claim_a.id}-{claim_b.id}",
                        lesson_id=document.lesson_id,
                        phase=document.phase,
                        claim_a=claim_a,
                        claim_b=claim_b,
                        severity=Severity.ERROR,
                        description="Count mismatch: 'three' vs 'four'",
                        suggestion="Verify the correct count",
                    ))

                if "annual" in text_a and "quarter" in text_b:
                    contradictions.append(Contradiction(
                        id=f"contr-{document.lesson_id}-self-{claim_a.id}-{claim_b.id}",
                        lesson_id=document.lesson_id,
                        phase=document.phase,
                        claim_a=claim_a,
                        claim_b=claim_b,
                        severity=Severity.ERROR,
                        description="Frequency contradiction: 'annual' vs 'per quarter'",
                        suggestion="Use consistent frequency terminology",
                    ))

        return contradictions

    def _check_numeric_consistency(self, document: DocumentParseResult) -> List[Contradiction]:
        contradictions = []
        table_claims = [c for c in document.claims if c.section_type == SectionType.TABLE]
        other_claims = [c for c in document.claims if c.section_type != SectionType.TABLE]

        for t_claim in table_claims:
            for o_claim in other_claims:
                t_nums = self._extract_quantities(t_claim.text.lower())
                o_nums = self._extract_quantities(o_claim.text.lower())

                for tq in t_nums:
                    for oq in o_nums:
                        if tq["unit"] == oq["unit"] and self._quantities_conflict(tq, oq, t_claim.text, o_claim.text):
                            contradictions.append(Contradiction(
                                id=f"contr-{document.lesson_id}-num-{t_claim.id}-{o_claim.id}",
                                lesson_id=document.lesson_id,
                                phase=document.phase,
                                claim_a=t_claim,
                                claim_b=o_claim,
                                severity=Severity.ERROR,
                                description=f"Table vs body numeric conflict: {tq['original']} vs {oq['original']}",
                                suggestion="Verify table data matches body text",
                            ))

        return contradictions

    def _check_count_consistency(self, document: DocumentParseResult) -> List[Contradiction]:
        contradictions = []
        exercise_claims = [c for c in document.claims if c.section_type == SectionType.EXERCISE]
        other_claims = [c for c in document.claims if c.section_type != SectionType.EXERCISE]

        for e_claim in exercise_claims:
            for o_claim in other_claims:
                e_text = e_claim.text.lower()
                o_text = o_claim.text.lower()

                if ("action" in e_text or "item" in e_text or "lists" in e_text) and ("action" in o_text or "item" in o_text or "lists" in o_text):
                    e_nums = self._extract_quantities(e_text)
                    o_nums = self._extract_quantities(o_text)
                    for eq in e_nums:
                        for oq in o_nums:
                            if eq["unit"] in ("", "items", "actions") and oq["unit"] in ("", "items", "actions"):
                                if eq["value"] != oq["value"]:
                                    contradictions.append(Contradiction(
                                        id=f"contr-{document.lesson_id}-count-{e_claim.id}-{o_claim.id}",
                                        lesson_id=document.lesson_id,
                                        phase=document.phase,
                                        claim_a=e_claim,
                                        claim_b=o_claim,
                                        severity=Severity.WARNING,
                                        description=f"Count mismatch: {eq['original']} vs {oq['original']}",
                                        suggestion="Verify list count matches stated number",
                                    ))

        return contradictions


def analyze_document(document: DocumentParseResult) -> List[Contradiction]:
    engine = ContradictionEngine()
    return engine.analyze(document)