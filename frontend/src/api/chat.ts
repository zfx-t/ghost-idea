import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export interface ChatRequest {
  message: string;
  conversationId?: string;
}

export interface ChatResponse {
  response: string;
  conversationId: string;
}

export const chatAPI = {
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await axios.post(`${API_BASE_URL}/chat`, request);
    return response.data;
  },
};
