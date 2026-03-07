import React, { useEffect } from 'react';
import { Spin, Alert } from 'antd';
import { useChatStore } from '../../stores/chatStore';
import { useSessionStore } from '../../stores/sessionStore';
import t from '../../locales';
import MessageList from './MessageList';
import MessageInput from './MessageInput';

const ChatWindow: React.FC = () => {
  const { messages, isLoading, error, sendMessage } = useChatStore();
  const { initSession, isAuthenticated } = useSessionStore();

  useEffect(() => {
    initSession();
  }, [initSession]);

  if (!isAuthenticated) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <Spin tip={t.chat.initializing} size="large" />
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {error && (
        <Alert
          message={error}
          type="error"
          closable
          onClose={() => useChatStore.setState({ error: null })}
          style={{ margin: '8px 24px 0' }}
        />
      )}
      <MessageList messages={messages} isLoading={isLoading} />
      <MessageInput onSend={sendMessage} disabled={isLoading} />
    </div>
  );
};

export default ChatWindow;
