"""
Prometheus metrics for EmoAgent system

This module defines custom business and performance metrics for monitoring
the emotion chat system. LLMOps metrics will be added after real LLM integration.
"""

from prometheus_client import Counter, Histogram, Gauge


# ========== 业务指标 (Business Metrics) ==========

sessions_total = Counter(
    'emoagent_sessions_total',
    'Total number of sessions created'
)

messages_total = Counter(
    'emoagent_messages_total',
    'Total number of messages processed'
)

crisis_triggered = Counter(
    'emoagent_crisis_total',
    'Total number of crisis detections',
    ['category']
)


# ========== 性能指标 (Performance Metrics) ==========

bert_latency = Histogram(
    'emoagent_bert_latency_seconds',
    'BERT inference latency in seconds',
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

api_latency = Histogram(
    'emoagent_api_latency_seconds',
    'API endpoint latency in seconds',
    ['endpoint'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)


# ========== 情绪分布 (Emotion Distribution) ==========

emotion_distribution = Gauge(
    'emoagent_emotion_distribution',
    'Current emotion distribution',
    ['emotion']
)

active_sessions = Gauge(
    'emoagent_active_sessions',
    'Number of currently active sessions'
)


# ========== 自评指标 (Rating Metrics) ==========

rating_submissions = Counter(
    'emoagent_rating_submissions_total',
    'Total number of rating submissions',
    ['type']
)

rating_score_distribution = Histogram(
    'emoagent_rating_score',
    'Distribution of rating scores',
    ['type'],
    buckets=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
)


# ========== LLMOps 指标 (延后至真实LLM上线后) ==========
# 
# llm_tokens_total = Counter(
#     'emoagent_llm_tokens_total',
#     'Total LLM tokens consumed',
#     ['type', 'provider']
# )
# 
# llm_cost_usd = Counter(
#     'emoagent_llm_cost_usd',
#     'Estimated LLM cost in USD',
#     ['provider']
# )
# 
# llm_calls_total = Counter(
#     'emoagent_llm_calls_total',
#     'Total LLM API calls',
#     ['provider', 'status']
# )
# 
# llm_retry_total = Counter(
#     'emoagent_llm_retry_total',
#     'Total LLM retry attempts',
#     ['provider']
# )
# 
# llm_latency = Histogram(
#     'emoagent_llm_latency_seconds',
#     'LLM API call latency in seconds',
#     ['provider', 'status'],
#     buckets=[0.5, 1.0, 2.5, 5.0, 10.0, 15.0, 30.0]
# )
# 
# llm_response_length = Histogram(
#     'emoagent_llm_response_length',
#     'LLM response length in characters',
#     ['provider'],
#     buckets=[50, 100, 200, 500, 1000, 2000]
# )
