export interface Claim {
  id: string;
  section_type: 'hook' | 'body' | 'table' | 'exercise' | 'learning_objectives' | 'problem' | 'concept' | 'ship_it';
  text: string;
  line_start: number;
  line_end: number;
  metadata: Record<string, unknown>;
}

export interface Contradiction {
  id: string;
  lesson_id: string;
  phase: string;
  claim_a: Claim;
  claim_b: Claim;
  severity: 'info' | 'warning' | 'error' | 'critical';
  description: string;
  suggestion?: string;
}

export interface DocumentParseResult {
  phase: string;
  lesson_id: string;
  title: string;
  claims: Claim[];
  raw_sections: Record<string, unknown>;
}

export interface AnalysisResponse {
  document: DocumentParseResult;
  contradictions: Contradiction[];
  summary: {
    total_claims: number;
    total_contradictions: number;
    by_severity: Record<string, number>;
    by_section: Record<string, number>;
  };
}

export interface AnalysisRequest {
  content: string;
  phase: string;
  lesson_id: string;
}