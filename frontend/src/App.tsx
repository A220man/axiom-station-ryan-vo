import React from 'react';
import { Analyzer } from './components/Analyzer';

export const App: React.FC = () => {
  return (
    <div style={{ minHeight: '100vh' }}>
      <nav style={{ background: 'white', borderBottom: '1px solid var(--color-border)', padding: '1rem 1.5rem' }}>
        <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <h1 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Axiom Station</h1>
          <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>AI Engineering Documentation Contradiction Detector</p>
        </div>
      </nav>
      <main>
        <Analyzer />
      </main>
      <footer style={{ background: 'white', borderTop: '1px solid var(--color-border)', padding: '1.5rem', marginTop: '2rem' }}>
        <div className="container" style={{ textAlign: 'center', color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>
          MIT \u00A9 Ryan Vo ryandtvo@gmail.com | AI & Machine Learning
        </div>
      </footer>
    </div>
  );
};