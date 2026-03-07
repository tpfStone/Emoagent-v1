from pydantic import BaseModel


class TimeRange(BaseModel):
    start: str
    end: str


class WeeklyReportResponse(BaseModel):
    session_id: str
    time_range: TimeRange
    session_count: int
    total_turns: int
    avg_turns_per_session: float
    emotion_distribution: dict[str, int]
    crisis_count: int
    rating_before_avg: float
    rating_after_avg: float
    rating_missing_rate: float
    bert_avg_latency_ms: int
    llm_avg_latency_ms: int
