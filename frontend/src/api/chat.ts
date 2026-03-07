import apiClient from './client';
import type { ChatRequest, ChatResponse } from './types';

export const chatAPI = {
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    const { data } = await apiClient.post<ChatResponse>('/api/chat/message', request);
    return data;
  },
};
