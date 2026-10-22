import re
from typing import List, Dict, Optional, Tuple
from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin
from mdit_py_plugins.footnote import footnote_plugin

from app.models.schemas import Claim, DocumentParseResult, SectionType


class DocumentParser:
    def __init__(self):
        self.md = (
            MarkdownIt("commonmark")
            .use(front_matter_plugin)
            .use(footnote_plugin)
            .enable("table")
        )

    def parse(self, content: str, phase: str, lesson_id: str) -> DocumentParseResult:
        tokens = self.md.parse(content)
        sections = self._extract_sections(tokens, content)
        claims = self._extract_claims(sections, content)
        title = self._extract_title(tokens, content) or lesson_id

        return DocumentParseResult(
            phase=phase,
            lesson_id=lesson_id,
            title=title,
            claims=claims,
            raw_sections=sections,
        )

    def _extract_sections(self, tokens, content: str) -> Dict[SectionType, List[Dict]]:
        sections = {st: [] for st in SectionType}
        lines = content.split("\n")
        current_section = None
        section_content = []
        section_start = 0

        for i, line in enumerate(lines):
            header_match = re.match(r"^(#{1,3})\s+(.+)$", line)
            if header_match:
                if current_section and section_content:
                    sections[current_section].append({
                        "title": current_title,
                        "content": "\n".join(section_content),
                        "line_start": section_start,
                        "line_end": i - 1,
                    })
                level = len(header_match.group(1))
                current_title = header_match.group(2).strip()
                current_section = self._classify_section(current_title, level)
                section_content = []
                section_start = i + 1
            else:
                section_content.append(line)

        if current_section and section_content:
            sections[current_section].append({
                "title": current_title,
                "content": "\n".join(section_content),
                "line_start": section_start,
                "line_end": len(lines) - 1,
            })

        return sections

    def _classify_section(self, title: str, level: int) -> SectionType:
        title_lower = title.lower()
        if "hook" in title_lower:
            return SectionType.HOOK
        elif "learning objective" in title_lower:
            return SectionType.LEARNING_OBJECTIVES
        elif "problem" in title_lower or "the problem" in title_lower:
            return SectionType.PROBLEM
        elif "concept" in title_lower:
            return SectionType.CONCEPT
        elif "exercise" in title_lower:
            return SectionType.EXERCISE
        elif "ship it" in title_lower:
            return SectionType.SHIP_IT
        elif "table" in title_lower or "comparison" in title_lower:
            return SectionType.TABLE
        else:
            return SectionType.BODY

    def _extract_claims(self, sections: Dict, content: str) -> List[Claim]:
        claims = []
        claim_id = 0

        for section_type, section_list in sections.items():
            for section in section_list:
                section_claims = self._extract_claims_from_section(
                    section, section_type, claim_id
                )
                claims.extend(section_claims)
                claim_id += len(section_claims)

        return claims

    def _extract_claims_from_section(
        self, section: Dict, section_type: SectionType, base_id: int
    ) -> List[Claim]:
        claims = []
        content = section["content"]
        lines = content.split("\n")

        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if self._is_factual_claim(line):
                claims.append(Claim(
                    id=f"{section_type.value}-{base_id + len(claims)}",
                    section_type=section_type,
                    text=line,
                    line_start=section["line_start"] + i,
                    line_end=section["line_start"] + i,
                    metadata={"section_title": section["title"]},
                ))

            # Also extract claims from sentences containing number words with domain keywords
            if re.search(r"\b(one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b", line.lower()):
                if any(kw in line.lower() for kw in ["task", "action", "item", "step", "pattern", "example", "model", "layer", "parameter", "audit", "frequency", "quarter", "annual", "per"]):
                    claims.append(Claim(
                        id=f"{section_type.value}-{base_id + len(claims)}",
                        section_type=section_type,
                        text=line,
                        line_start=section["line_start"] + i,
                        line_end=section["line_start"] + i,
                        metadata={"section_title": section["title"]},
                    ))

            # Also extract claims with frequency/time keywords even without explicit numbers
            if any(kw in line.lower() for kw in ["quarter", "annual", "per quarter", "per year", "monthly", "weekly"]):
                claims.append(Claim(
                    id=f"{section_type.value}-{base_id + len(claims)}",
                    section_type=section_type,
                    text=line,
                    line_start=section["line_start"] + i,
                    line_end=section["line_start"] + i,
                    metadata={"section_title": section["title"]},
                ))

        table_claims = self._extract_table_claims(section, section_type, base_id + len(claims))
        claims.extend(table_claims)

        return claims
    def _is_factual_claim(self, line: str) -> bool:
        line_lower = line.lower()
        factual_patterns = [
            r"\d+(\.\d+)?\s*(billion|million|thousand|k|m|b|gpu|hours?|years?|params?|tokens?)",
            r"\d+(\.\d+)?\s*[×x]\s*\d+",
            r"\d+(\.\d+)?%\s*(reduction|increase|compression|accuracy)",
            r"(is|are|was|were|has|have|claims?|states?|reports?|specifies?)\s+",
            r"(vs|versus|compared to|conflicts with|contradicts)",
            r"(sum to|total|maximum|minimum|exceeds|fills|reaches)",
        ]
        return any(re.search(p, line_lower) for p in factual_patterns)

    def _extract_table_claims(self, section: Dict, section_type: SectionType, base_id: int) -> List[Claim]:
        claims = []
        content = section["content"]
        if "|" not in content:
            return claims

        lines = content.split("\n")
        in_table = False
        header = None

        for i, line in enumerate(lines):
            if line.strip().startswith("|"):
                in_table = True
                if header is None and not re.match(r"^\|?\s*-+\s*\|", line):
                    header = [c.strip() for c in line.split("|") if c.strip()]
                elif header and not re.match(r"^\|?\s*-+\s*\|", line):
                    cells = [c.strip() for c in line.split("|") if c.strip()]
                    if len(cells) == len(header):
                        row_data = dict(zip(header, cells))
                        claims.append(Claim(
                            id=f"{section_type.value}-table-{base_id + len(claims)}",
                            section_type=SectionType.TABLE,
                            text=f"Table row: {row_data}",
                            line_start=section["line_start"] + i,
                            line_end=section["line_start"] + i,
                            metadata={"table_header": header, "row_data": row_data},
                        ))
            elif in_table:
                in_table = False
                header = None

        return claims

    def _extract_title(self, tokens, content: str) -> Optional[str]:
        for token in tokens:
            if token.type == "heading_open" and token.tag == "h1":
                return content.split("\n")[token.map[0]] if token.map else None
        return None


def parse_document(content: str, phase: str, lesson_id: str) -> DocumentParseResult:
    parser = DocumentParser()
    return parser.parse(content, phase, lesson_id)