import apiClient from './client';
import type { WeeklyReportResponse } from './types';

export const reportAPI = {
  getWeeklyReport: async (sessionId: string, token: string): Promise<WeeklyReportResponse> => {
    const { data } = await apiClient.get<WeeklyReportResponse>(
      `/api/reports/weekly?session_id=${sessionId}&token=${token}`
    );
    return data;
  },
};
