import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authAPI } from '../api/auth';

interface SessionState {
  token: string | null;
  sessionId: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  initSession: () => Promise<void>;
  clearSession: () => void;
}

export const useSessionStore = create<SessionState>()(
  persist(
    (set, get) => ({
      token: null,
      sessionId: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      initSession: async () => {
        if (get().isAuthenticated) return;
        set({ isLoading: true, error: null });
        try {
          const { token, session_id } = await authAPI.getAnonymousToken();
          set({
            token,
            sessionId: session_id,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch {
          set({ error: 'Failed to get session', isLoading: false });
        }
      },

      clearSession: () => {
        set({
          token: null,
          sessionId: null,
          isAuthenticated: false,
        });
      },
    }),
    { name: 'session-storage' }
  )
);
