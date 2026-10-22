import axios from 'axios';
import type { AnalysisRequest, AnalysisResponse } from '../types/api';

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const analyzeDocument = async (request: AnalysisRequest): Promise<AnalysisResponse> => {
  const response = await api.post<AnalysisResponse>('/documents/analyze', request);
  return response.data;
};

export const analyzeFile = async (file: File, phase: string, lessonId: string): Promise<AnalysisResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('phase', phase);
  formData.append('lesson_id', lessonId);

  const response = await api.post<AnalysisResponse>('/documents/analyze/file', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const getContradictions = async (params?: { phase?: string; lesson_id?: string; severity?: string }) => {
  const response = await api.get('/contradictions/', { params });
  return response.data;
};

export const getStats = async () => {
  const response = await api.get('/contradictions/stats');
  return response.data;
};

export default api;