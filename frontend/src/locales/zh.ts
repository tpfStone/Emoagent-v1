import type { Locale } from './en';

const zh: Locale = {
  emotions: {
    joy: '喜悦',
    sadness: '悲伤',
    fear: '恐惧',
    anger: '愤怒',
    love: '爱',
    surprise: '惊讶',
  },
  chat: {
    title: 'EmoAgent 情绪对话',
    initializing: '正在初始化会话...',
    thinking: '思考中...',
    placeholder: '输入消息... (Enter 发送, Shift+Enter 换行)',
    send: '发送',
    greeting: '你好，我是你的情绪支持助手',
    greetingSub: '有什么想聊的，随时告诉我',
  },
  rating: {
    title: '情绪自评',
    submit: '提交',
    cancel: '取消',
    promptBefore: '请为会话开始前的情绪状态打分（1-10）',
    promptAfter: '请为会话结束后的情绪状态打分（1-10）',
  },
  crisis: {
    title: '安全提示',
  },
  report: {
    title: '周统计报告',
    button: '周报',
    loading: '加载周报中...',
    totalTurns: '总对话轮数',
    crisisTriggers: '危机触发',
    ratingBefore: '会话前自评',
    ratingAfter: '会话后自评',
    emotionDist: '情绪分布',
    performance: '性能指标',
    bertLatency: 'BERT 平均延迟',
    llmLatency: 'LLM 平均延迟',
    missingRate: '自评缺失率',
    improvement: '情绪改善',
    noData: '暂无数据',
    noReport: '暂无周报数据，请先进行对话',
  },
  notFound: {
    subtitle: '页面不存在',
    backHome: '返回首页',
  },
  error: {
    requestFailed: '请求失败',
  },
};

export default zh;
