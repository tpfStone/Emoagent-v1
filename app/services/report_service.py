from datetime import UTC, datetime, timedelta

from app.dao.rating_dao import RatingDAO
from app.dao.turn_dao import TurnDAO
from app.schemas.report import TimeRange, WeeklyReportResponse


class ReportService:
    def __init__(self, turn_dao: TurnDAO, rating_dao: RatingDAO):
        self.turn_dao = turn_dao
        self.rating_dao = rating_dao

    async def get_weekly_report(self, session_id: str) -> WeeklyReportResponse:
        end = datetime.now(UTC)
        start = end - timedelta(days=7)

        turns = await self.turn_dao.get_turns_in_range(session_id, start, end)
        emotion_dist = await self.turn_dao.get_emotion_distribution(
            session_id, start, end
        )
        crisis_count = await self.turn_dao.count_crisis_turns(session_id, start, end)
        avg_latencies = await self.turn_dao.get_avg_latencies(session_id, start, end)
        rating_scores = await self.rating_dao.get_avg_scores(session_id, start, end)
        missing_rate = await self.rating_dao.get_missing_rate(session_id, start, end)

        total_turns = len(turns)

        return WeeklyReportResponse(
            session_id=session_id,
            time_range=TimeRange(
                start=start.isoformat() + "Z", end=end.isoformat() + "Z"
            ),
            session_count=1,
            total_turns=total_turns,
            avg_turns_per_session=float(total_turns),
            emotion_distribution=emotion_dist,
            crisis_count=crisis_count,
            rating_before_avg=rating_scores.get("before", 0.0),
            rating_after_avg=rating_scores.get("after", 0.0),
            rating_missing_rate=missing_rate,
            bert_avg_latency_ms=avg_latencies.get("bert", 0),
            llm_avg_latency_ms=avg_latencies.get("llm", 0),
        )
