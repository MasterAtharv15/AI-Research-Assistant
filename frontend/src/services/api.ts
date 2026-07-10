import axios from 'axios';
import type { AxiosInstance } from 'axios';

import type { QueryRequest, QueryResponse, UploadResponse } from '../types/api';

/** Shared Axios client for the FastAPI backend. */
const api: AxiosInstance = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 1800000,
});

function toReadableError(error: unknown): Error {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === 'string' && detail.trim()) {
      return new Error(detail);
    }

    if (typeof error.message === 'string' && error.message.trim()) {
      return new Error(error.message);
    }
  }

  if (error instanceof Error) {
    return new Error(error.message);
  }

  return new Error('An unexpected error occurred while contacting the API.');
}

/** Upload a PDF document to the backend and return the extraction result. */
export async function uploadPdf(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await api.post<UploadResponse>('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    return response.data;
  } catch (error) {
    throw toReadableError(error);
  }
}

/** Send a user question to the backend and return the answer and matching chunks. */
export async function askQuestion(request: QueryRequest): Promise<QueryResponse> {
  try {
    const response = await api.post<QueryResponse>('/query', request);
    return response.data;
  } catch (error) {
    throw toReadableError(error);
  }
}
