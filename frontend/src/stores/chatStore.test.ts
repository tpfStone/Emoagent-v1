import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useChatStore } from './chatStore';
import { useSessionStore } from './sessionStore';

vi.mock('../api/chat', () => ({
  chatAPI: {
    sendMessage: vi.fn(),
  },
}));

import { chatAPI } from '../api/chat';

describe('chatStore', () => {
  beforeEach(() => {
    useChatStore.setState({ messages: [], isLoading: false, error: null });
  });

  it('has correct initial state', () => {
    const state = useChatStore.getState();
    expect(state.messages).toEqual([]);
    expect(state.isLoading).toBe(false);
    expect(state.error).toBeNull();
  });

  it('clearMessages resets messages', () => {
    useChatStore.setState({
      messages: [
        { role: 'user', content: 'hello', turnIndex: 1, timestamp: new Date() },
      ],
    });

    useChatStore.getState().clearMessages();
    expect(useChatStore.getState().messages).toEqual([]);
  });

  it('sendMessage sets error when session not initialized', async () => {
    useSessionStore.setState({ token: null, sessionId: null });

    await useChatStore.getState().sendMessage('hello');
    expect(useChatStore.getState().error).toBe('Session not initialized');
  });

  it('sendMessage adds user and assistant messages on success', async () => {
    useSessionStore.setState({
      token: 'test-token',
      sessionId: 'test-session',
      isAuthenticated: true,
      isLoading: false,
      error: null,
    });

    (chatAPI.sendMessage as ReturnType<typeof vi.fn>).mockResolvedValue({
      assistant_message: 'AI reply',
      emotion_label: 'joy',
      is_crisis: false,
      turn_index: 1,
    });

    await useChatStore.getState().sendMessage('Hello');

    const messages = useChatStore.getState().messages;
    expect(messages).toHaveLength(2);
    expect(messages[0].role).toBe('user');
    expect(messages[0].content).toBe('Hello');
    expect(messages[1].role).toBe('assistant');
    expect(messages[1].content).toBe('AI reply');
    expect(messages[1].emotion).toBe('joy');
  });

  it('sendMessage sets error on API failure', async () => {
    useSessionStore.setState({
      token: 'test-token',
      sessionId: 'test-session',
      isAuthenticated: true,
      isLoading: false,
      error: null,
    });

    (chatAPI.sendMessage as ReturnType<typeof vi.fn>).mockRejectedValue(
      new Error('Network error')
    );

    await useChatStore.getState().sendMessage('Hello');

    expect(useChatStore.getState().error).toBe('Failed to send message');
    expect(useChatStore.getState().isLoading).toBe(false);
  });
});
