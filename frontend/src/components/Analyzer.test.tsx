import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Analyzer } from './Analyzer';
import { analyzeDocument } from '../api/client';

vi.mock('../api/client', () => ({
  analyzeDocument: vi.fn(),
  analyzeFile: vi.fn(),
  getContradictions: vi.fn(),
  getStats: vi.fn(),
}));

const mockAnalyzeDocument = analyzeDocument as unknown as ReturnType<typeof vi.fn>;

describe('Analyzer', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the analyzer form', () => {
    render(<Analyzer />);
    expect(screen.getByText('Axiom Station - Contradiction Analyzer')).toBeInTheDocument();
    expect(screen.getByLabelText('Phase')).toBeInTheDocument();
    expect(screen.getByLabelText('Lesson ID')).toBeInTheDocument();
    expect(screen.getByText('Analyze Document')).toBeInTheDocument();
  });

  it('shows sample content by default', () => {
    render(<Analyzer />);
    const textarea = screen.getByLabelText('Markdown Content') as HTMLTextAreaElement;
    expect(textarea.value).toContain('Phase 12 - Multimodal AI');
  });

  it('calls analyzeDocument on submit', async () => {
    const mockResponse = {
      document: {
        phase: 'phase-12',
        lesson_id: 'test-01',
        title: '# Test',
        claims: [],
        raw_sections: {},
      },
      contradictions: [],
      summary: {
        total_claims: 0,
        total_contradictions: 0,
        by_severity: {},
        by_section: {},
      },
    };
    mockAnalyzeDocument.mockResolvedValue(mockResponse);

    render(<Analyzer />);
    fireEvent.click(screen.getByText('Analyze Document'));

    await waitFor(() => {
      expect(mockAnalyzeDocument).toHaveBeenCalledWith(
        expect.objectContaining({
          phase: 'phase-12',
          lesson_id: '03-blip2-qformer-bridge',
        })
      );
    });
  });

  it('displays error message on analysis failure', async () => {
    mockAnalyzeDocument.mockRejectedValue(new Error('API Error'));

    render(<Analyzer />);
    fireEvent.click(screen.getByText('Analyze Document'));

    await waitFor(() => {
      expect(screen.getByText('API Error')).toBeInTheDocument();
    });
  });
});
