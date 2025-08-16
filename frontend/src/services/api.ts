import axios from 'axios';

const API_BASE_URL = '/api';

export interface UploadResponse {
  session_id: string;
  filename: string;
  chunks_processed: number;
  message: string;
}

export interface ChatResponse {
  response: string;
  session_id: string;
}

class ApiService {
  private client = axios.create({
    baseURL: API_BASE_URL,
    timeout: 120000, // 2 minutes for document processing
  });

  async uploadFile(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post<UploadResponse>('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  async chat(sessionId: string, message: string): Promise<ChatResponse> {
    const response = await this.client.post<ChatResponse>('/chat', {
      session_id: sessionId,
      message,
    });

    return response.data;
  }

  async deleteSession(sessionId: string): Promise<void> {
    await this.client.delete(`/session/${sessionId}`);
  }

  async healthCheck(): Promise<{ status: string; active_sessions: number }> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

export const apiService = new ApiService();