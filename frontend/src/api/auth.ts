import apiClient from './client';
import type { AuthResponse } from './types';

export const authAPI = {
  getAnonymousToken: async (): Promise<AuthResponse> => {
    const { data } = await apiClient.post<AuthResponse>('/api/auth/anonymous');
    return data;
  },
};
