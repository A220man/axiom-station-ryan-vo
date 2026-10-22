import React from 'react';

interface FilterBarProps {
  phases: string[];
  severities: string[];
  sections: string[];
  filters: { phase: string; severity: string; section: string };
  onPhaseChange: (value: string) => void;
  onSeverityChange: (value: string) => void;
  onSectionChange: (value: string) => void;
}

export const FilterBar: React.FC<FilterBarProps> = ({
  phases,
  severities,
  sections,
  filters,
  onPhaseChange,
  onSeverityChange,
  onSectionChange,
}) => {
  return (
    <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
      <div>
        <label htmlFor="phase-filter" className="block text-sm font-medium mb-0.5">Phase</label>
        <select
          id="phase-filter"
          className="input"
          value={filters.phase}
          onChange={(e) => onPhaseChange(e.target.value)}
        >
          {phases.map((p) => (
            <option key={p} value={p}>{p === 'all' ? 'All Phases' : p}</option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="severity-filter" className="block text-sm font-medium mb-0.5">Severity</label>
        <select
          id="severity-filter"
          className="input"
          value={filters.severity}
          onChange={(e) => onSeverityChange(e.target.value)}
        >
          {severities.map((s) => (
            <option key={s} value={s}>{s === 'all' ? 'All Severities' : s.charAt(0).toUpperCase() + s.slice(1)}</option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="section-filter" className="block text-sm font-medium mb-0.5">Section</label>
        <select
          id="section-filter"
          className="input"
          value={filters.section}
          onChange={(e) => onSectionChange(e.target.value)}
        >
          {sections.map((s) => (
            <option key={s} value={s}>{s === 'all' ? 'All Sections' : s.replace('_', ' ')}</option>
          ))}
        </select>
      </div>
    </div>
  );
};