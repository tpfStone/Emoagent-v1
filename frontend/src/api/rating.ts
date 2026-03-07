import apiClient from './client';
import type { RatingRequest, RatingResponse } from './types';

export const ratingAPI = {
  submitRating: async (request: RatingRequest): Promise<RatingResponse> => {
    const { data } = await apiClient.post<RatingResponse>('/api/ratings', request);
    return data;
  },
};
