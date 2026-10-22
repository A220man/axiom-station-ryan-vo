import React, { useState } from 'react';
import { useAnalysis } from '../hooks/useAnalysis';
import { ContradictionTable } from './ContradictionTable';
import { FilterBar } from './FilterBar';
import type { AnalysisRequest } from '../types/api';

const SAMPLE_CONTENT = `# Phase 12 - Multimodal AI

## Hook
BLIP-2 uses an 11B LLM backbone for vision-language tasks.

## Body
The Q-Former bridges the vision encoder to an OPT-6.7B language model.
The model has 6.7B parameters total.

## Comparison Table
| Model | Params | Data |
|-------|--------|------|
| BLIP-2 | 11B | 129M images |
| LLaVA | 6.7B | 558K conversations |

## Learning Objectives
This lesson covers three tasks: understanding Q-Former, comparing with Flamingo, implementing BLIP-2.

## Exercise 1
The four tasks are: task 1, task 2, task 3, task 4.`;

export const Analyzer: React.FC = () => {
  const [content, setContent] = useState(SAMPLE_CONTENT);
  const [phase, setPhase] = useState('phase-12');
  const [lessonId, setLessonId] = useState('03-blip2-qformer-bridge');
  const { response, loading, error, analyze, analyzeFileUpload, clear } = useAnalysis();

  const handleAnalyze = () => {
    const request: AnalysisRequest = { content, phase, lesson_id: lessonId };
    analyze(request);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      analyzeFileUpload(file, phase, lessonId);
    }
  };

  const filteredContradictions = response?.contradictions || [];
  const phases = ['all', ...new Set(filteredContradictions.map((c) => c.phase))];
  const severities = ['all', 'error', 'warning', 'info', 'critical'];
  const sections = ['all', ...new Set(filteredContradictions.map((c) => c.claim_a.section_type))];

  return (
    <div className="container" style={{ paddingTop: '2rem', paddingBottom: '2rem' }}>
      <header className="section-header">
        <h1 className="section-title">Axiom Station - Contradiction Analyzer</h1>
      </header>

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h2 className="section-title" style={{ fontSize: '1rem', marginBottom: '1rem' }}>Document Input</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
          <div>
            <label htmlFor="phase" className="block text-sm font-medium mb-0.5">Phase</label>
            <input
              id="phase"
              type="text"
              className="input"
              value={phase}
              onChange={(e) => setPhase(e.target.value)}
              placeholder="phase-12"
            />
          </div>
          <div>
            <label htmlFor="lessonId" className="block text-sm font-medium mb-0.5">Lesson ID</label>
            <input
              id="lessonId"
              type="text"
              className="input"
              value={lessonId}
              onChange={(e) => setLessonId(e.target.value)}
              placeholder="03-blip2-qformer-bridge"
            />
          </div>
        </div>
        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor="content" className="block text-sm font-medium mb-0.5">Markdown Content</label>
          <textarea
            id="content"
            className="input"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Paste markdown content here..."
          />
        </div>
        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          <button className="btn-primary" onClick={handleAnalyze} disabled={loading || !content.trim()}>
            {loading ? 'Analyzing...' : 'Analyze Document'}
          </button>
          <button className="btn-secondary" onClick={clear} disabled={loading}>
            Clear
          </button>
        </div>
        <div style={{ marginTop: '1rem' }}>
          <label htmlFor="file-upload" className="block text-sm font-medium mb-0.5">Or upload a .md file</label>
          <input
            id="file-upload"
            type="file"
            accept=".md,.markdown,.txt"
            onChange={handleFileUpload}
            className="input"
            style={{ padding: '0.5rem' }}
          />
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      {response && (
        <>
          <div className="card" style={{ marginBottom: '1.5rem' }}>
            <div className="section-header">
              <h2 className="section-title">Analysis Summary</h2>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <div className="badge badge-info">Claims: {response.summary.total_claims}</div>
                <div className="badge badge-error">Contradictions: {response.summary.total_contradictions}</div>
              </div>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem' }}>
              {Object.entries(response.summary.by_severity).map(([severity, count]) => (
                <div key={severity} className={`badge badge-${severity}`}>
                  {severity.charAt(0).toUpperCase() + severity.slice(1)}: {count}
                </div>
              ))}
            </div>
          </div>

          <div className="card">
            <div className="section-header">
              <h2 className="section-title">Detected Contradictions</h2>
            </div>
            <FilterBar
              phases={phases}
              severities={severities}
              sections={sections}
              filters={{ phase: 'all', severity: 'all', section: 'all' }}
              onPhaseChange={() => {}}
              onSeverityChange={() => {}}
              onSectionChange={() => {}}
            />
            <ContradictionTable contradictions={filteredContradictions} />
          </div>
        </>
      )}
    </div>
  );
};