const en = {
  emotions: {
    joy: 'Joy',
    sadness: 'Sadness',
    fear: 'Fear',
    anger: 'Anger',
    love: 'Love',
    surprise: 'Surprise',
  },
  chat: {
    title: 'EmoAgent',
    initializing: 'Initializing session...',
    thinking: 'Thinking...',
    placeholder: 'Type a message... (Enter to send, Shift+Enter for new line)',
    send: 'Send',
    greeting: "Hi, I'm your emotional support assistant",
    greetingSub: 'Feel free to share anything on your mind',
  },
  rating: {
    title: 'Self-Assessment',
    submit: 'Submit',
    cancel: 'Cancel',
    promptBefore: 'Rate your emotional state before the session (1-10)',
    promptAfter: 'Rate your emotional state after the session (1-10)',
  },
  crisis: {
    title: 'Safety Alert',
  },
  report: {
    title: 'Weekly Report',
    button: 'Report',
    loading: 'Loading report...',
    totalTurns: 'Total Turns',
    crisisTriggers: 'Crisis Triggers',
    ratingBefore: 'Pre-Session Rating',
    ratingAfter: 'Post-Session Rating',
    emotionDist: 'Emotion Distribution',
    performance: 'Performance Metrics',
    bertLatency: 'BERT Avg Latency',
    llmLatency: 'LLM Avg Latency',
    missingRate: 'Rating Missing Rate',
    improvement: 'Mood Improvement',
    noData: 'No data available',
    noReport: 'No report data yet. Start a conversation first.',
  },
  notFound: {
    subtitle: 'Page not found',
    backHome: 'Back to Home',
  },
  error: {
    requestFailed: 'Request failed',
  },
};

export type Locale = typeof en;
export default en;
