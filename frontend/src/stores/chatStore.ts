import { AxiosError } from 'axios';
import { create } from 'zustand';
import { chatAPI } from '../api/chat';
import { useSessionStore } from './sessionStore';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  emotion?: string | null;
  isCrisis?: boolean;
  turnIndex: number;
  timestamp: Date;
}

interface ChatState {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (text: string) => Promise<void>;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isLoading: false,
  error: null,

  sendMessage: async (text: string) => {
    const { token, sessionId } = useSessionStore.getState();
    if (!token || !sessionId) {
      set({ error: 'Session not initialized' });
      return;
    }

    const userMessage: Message = {
      role: 'user',
      content: text,
      turnIndex: get().messages.length + 1,
      timestamp: new Date(),
    };
    set({ messages: [...get().messages, userMessage], isLoading: true, error: null });

    try {
      const response = await chatAPI.sendMessage({
        session_id: sessionId,
        user_message: text,
        token,
      });

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.assistant_message,
        emotion: response.emotion_label,
        isCrisis: response.is_crisis,
        turnIndex: response.turn_index,
        timestamp: new Date(),
      };

      set({
        messages: [...get().messages, assistantMessage],
        isLoading: false,
      });
    } catch (err) {
      const detail = (err instanceof AxiosError)
        ? (err.response?.data as Record<string, string>)?.detail ?? err.message
        : 'Failed to send message';
      set({ error: detail, isLoading: false });
    }
  },

  clearMessages: () => {
    set({ messages: [] });
  },
}));
