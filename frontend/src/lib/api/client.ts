import { env } from '$env/dynamic/public';

import type {
  AnalyzeAcceptedResponse,
  AnalyzeRequest,
  DatasetOption,
  DatasetsResponse,
  ChangePreset,
  JobResponse,
  PresetsResponse
} from '$lib/types/contracts';

const API_BASE_URL = env.PUBLIC_API_BASE_URL || 'http://localhost:8000';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers || {})
    },
    ...init
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const payload = await response.json();
      if (typeof payload?.detail === 'string') {
        message = payload.detail;
      }
    } catch {
      // Ignore parse errors and keep default message.
    }
    throw new Error(message);
  }

  return (await response.json()) as T;
}

export function submitAnalyze(body: AnalyzeRequest): Promise<AnalyzeAcceptedResponse> {
  return request<AnalyzeAcceptedResponse>('/analyze', {
    method: 'POST',
    body: JSON.stringify(body)
  });
}

export function getJob(jobId: string): Promise<JobResponse> {
  return request<JobResponse>(`/jobs/${jobId}`);
}

export async function getDatasets(): Promise<DatasetOption[]> {
  const response = await request<DatasetsResponse>('/datasets');
  return response.datasets;
}

export async function getPresets(): Promise<ChangePreset[]> {
  const response = await request<PresetsResponse>('/presets');
  return response.presets;
}
