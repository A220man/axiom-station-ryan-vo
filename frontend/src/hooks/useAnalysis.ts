import { useState, useCallback } from 'react';
import { analyzeDocument, analyzeFile } from '../api/client';
import type { AnalysisRequest, AnalysisResponse, Contradiction } from '../types/api';

export function useAnalysis() {
  const [response, setResponse] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyze = useCallback(async (request: AnalysisRequest) => {
    setLoading(true);
    setError(null);
    try {
      const result = await analyzeDocument(request);
      setResponse(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
      setResponse(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const analyzeFileUpload = useCallback(async (file: File, phase: string, lessonId: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await analyzeFile(file, phase, lessonId);
      setResponse(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'File analysis failed');
      setResponse(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const clear = useCallback(() => {
    setResponse(null);
    setError(null);
  }, []);

  return { response, loading, error, analyze, analyzeFileUpload, clear };
}

export function useContradictionFilters(contradictions: Contradiction[]) {
  const [phaseFilter, setPhaseFilter] = useState<string>('all');
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [sectionFilter, setSectionFilter] = useState<string>('all');

  const filtered = contradictions.filter((c) => {
    if (phaseFilter !== 'all' && c.phase !== phaseFilter) return false;
    if (severityFilter !== 'all' && c.severity !== severityFilter) return false;
    if (sectionFilter !== 'all' && c.claim_a.section_type !== sectionFilter) return false;
    return true;
  });

  const phases = ['all', ...new Set(contradictions.map((c) => c.phase))];
  const severities = ['all', 'error', 'warning', 'info', 'critical'];
  const sections = ['all', ...new Set(contradictions.map((c) => c.claim_a.section_type))];

  return {
    filtered,
    filters: { phase: phaseFilter, severity: severityFilter, section: sectionFilter },
    setPhaseFilter,
    setSeverityFilter,
    setSectionFilter,
    options: { phases, severities, sections },
  };
}