import React from 'react';
import type { Contradiction } from '../types/api';

interface ContradictionRowProps {
  contradiction: Contradiction;
  index: number;
}

export const ContradictionRow: React.FC<ContradictionRowProps> = ({ contradiction, index }) => {
  const severityClass = `badge badge-${contradiction.severity}`;
  const sectionA = contradiction.claim_a.section_type.replace('_', ' ');
  const sectionB = contradiction.claim_b.section_type.replace('_', ' ');

  return (
    <tr>
      <td>{index + 1}</td>
      <td><span className={severityClass}>{contradiction.severity.toUpperCase()}</span></td>
      <td>{contradiction.phase}</td>
      <td>{contradiction.lesson_id}</td>
      <td>
        <div className="text-sm text-muted">Section A: {sectionA}</div>
        <div className="text-sm">{contradiction.claim_a.text.slice(0, 100)}...</div>
      </td>
      <td>
        <div className="text-sm text-muted">Section B: {sectionB}</div>
        <div className="text-sm">{contradiction.claim_b.text.slice(0, 100)}...</div>
      </td>
      <td>{contradiction.description}</td>
      <td>{contradiction.suggestion || '-'}</td>
    </tr>
  );
};

interface ContradictionTableProps {
  contradictions: Contradiction[];
}

export const ContradictionTable: React.FC<ContradictionTableProps> = ({ contradictions }) => {
  if (contradictions.length === 0) {
    return (
      <div className="empty-state">
        <p>No contradictions found.</p>
      </div>
    );
  }

  return (
    <div className="table-container">
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Severity</th>
            <th>Phase</th>
            <th>Lesson</th>
            <th>Claim A</th>
            <th>Claim B</th>
            <th>Description</th>
            <th>Suggestion</th>
          </tr>
        </thead>
        <tbody>
          {contradictions.map((c, i) => (
            <ContradictionRow key={c.id} contradiction={c} index={i} />
          ))}
        </tbody>
      </table>
    </div>
  );
};