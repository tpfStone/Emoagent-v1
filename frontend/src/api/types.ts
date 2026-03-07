export interface AuthResponse {
  token: string;
  session_id: string;
}

export interface ChatRequest {
  session_id: string;
  user_message: string;
  token: string;
}

export interface ChatResponse {
  assistant_message: string;
  emotion_label: string | null;
  is_crisis: boolean;
  turn_index: number;
}

export interface RatingRequest {
  session_id: string;
  rating_type: 'before' | 'after';
  score: number;
  token: string;
}

export interface RatingResponse {
  id: number;
  session_id: string;
  rating_type: 'before' | 'after';
  score: number;
  created_at: string;
}

export interface WeeklyReportResponse {
  session_id: string;
  time_range: {
    start: string;
    end: string;
  };
  session_count: number;
  total_turns: number;
  avg_turns_per_session: number;
  emotion_distribution: Record<string, number>;
  crisis_count: number;
  rating_before_avg: number;
  rating_after_avg: number;
  rating_missing_rate: number;
  bert_avg_latency_ms: number;
  llm_avg_latency_ms: number;
}
