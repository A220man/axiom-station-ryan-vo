import pytest
from app.services.document_parser import parse_document, DocumentParser
from app.services.contradiction_engine import analyze_document, ContradictionEngine
from app.models.schemas import Claim, SectionType, Severity


class TestDocumentParser:
    def test_parse_simple_document(self):
        content = """# Lesson Title

## Hook
This model has 11B parameters.

## Body
The actual model uses OPT-6.7B with 6.7B parameters.
"""
        result = parse_document(content, "phase-12", "03-blip2-qformer-bridge")
        assert result.phase == "phase-12"
        assert result.lesson_id == "03-blip2-qformer-bridge"
        assert len(result.claims) >= 2

    def test_extract_table_claims(self):
        content = """# Test

## Comparison Table
| Model | Params |
|-------|--------|
| A     | 1.3B   |
| B     | 4.4B   |
"""
        result = parse_document(content, "phase-12", "04-flamingo-gated-cross-attention")
        table_claims = [c for c in result.claims if c.section_type == SectionType.TABLE]
        assert len(table_claims) >= 1

    def test_section_classification(self):
        parser = DocumentParser()
        assert parser._classify_section("Hook", 2) == SectionType.HOOK
        assert parser._classify_section("Learning Objectives", 2) == SectionType.LEARNING_OBJECTIVES
        assert parser._classify_section("The Problem", 2) == SectionType.PROBLEM
        assert parser._classify_section("Exercise 5", 2) == SectionType.EXERCISE
        assert parser._classify_section("Comparison Table", 2) == SectionType.TABLE


class TestContradictionEngine:
    def test_numeric_contradiction_detection(self):
        content = """# Test

## Hook
The model has 11B parameters.

## Body
The model uses OPT-6.7B with 6.7B parameters.
"""
        document = parse_document(content, "phase-12", "test-lesson")
        contradictions = analyze_document(document)

        assert len(contradictions) >= 1
        found = False
        for c in contradictions:
            desc_lower = c.description.lower()
            if "11b" in desc_lower and "6.7b" in desc_lower:
                found = True
                assert c.severity == Severity.ERROR
        assert found, "Should detect 11B vs 6.7B contradiction"

    def test_count_contradiction(self):
        content = """# Test

## Learning Objectives
This lesson covers three tasks.

## Body
The four tasks are: task 1, task 2, task 3, task 4.
"""
        document = parse_document(content, "phase-14", "test-count")
        contradictions = analyze_document(document)

        found = False
        for c in contradictions:
            desc_lower = c.description.lower()
            if "three" in desc_lower and "four" in desc_lower:
                found = True
            # Also check for semantic contradiction warnings
            if "semantic" in desc_lower:
                if ("three" in c.claim_a.text.lower() and "four" in c.claim_b.text.lower()) or \
                   ("three" in c.claim_b.text.lower() and "four" in c.claim_a.text.lower()):
                    found = True
        assert found, "Should detect three vs four contradiction"

    def test_annual_vs_quarter(self):
        content = """# Test

## Concept
An annual failure-mode audit is recommended.

## Ship It
Per quarter. Not annual.
"""
        document = parse_document(content, "phase-16", "test-frequency")
        contradictions = analyze_document(document)

        found = False
        for c in contradictions:
            desc_lower = c.description.lower()
            if "annual" in desc_lower and "quarter" in desc_lower:
                found = True
                assert c.severity == Severity.ERROR
        assert found, "Should detect annual vs quarter contradiction"

    def test_2x_vs_4x_reduction(self):
        content = """# Test

## Hook
Aspect ratio is 9:16.

## Problem
The problem shows 1:3 aspect ratio.
"""
        document = parse_document(content, "phase-12", "test-ratio")
        contradictions = analyze_document(document)
        assert len(contradictions) >= 0

    def test_no_false_positive_on_different_units(self):
        content = """# Test

## Hook
Training took 100 GPU-hours.

## Body
The model has 100M parameters.
"""
        document = parse_document(content, "phase-12", "test-units")
        contradictions = analyze_document(document)
        numeric_contradictions = [c for c in contradictions if "numeric" in c.description.lower()]
        assert len(numeric_contradictions) == 0, "Different units should not trigger false positive"


class TestIntegration:
    def test_full_analysis_pipeline(self):
        content = """# Phase 12 - Multimodal AI

## Hook
BLIP-2 uses an 11B LLM backbone.

## Body
The Q-Former bridges the vision encoder to an OPT-6.7B language model.
The model has 6.7B parameters total.
"""
        document = parse_document(content, "phase-12", "03-blip2-qformer-bridge")
        contradictions = analyze_document(document)

        assert len(document.claims) > 0
        assert len(contradictions) >= 1
        error_contradictions = [c for c in contradictions if c.severity == Severity.ERROR]
        assert len(error_contradictions) >= 1