import React, { useEffect, useRef } from 'react';
import { Spin } from 'antd';
import t from '../../locales';
import MessageItem from './MessageItem';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  emotion?: string | null;
  isCrisis?: boolean;
  turnIndex: number;
}

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
}

const MessageList: React.FC<MessageListProps> = ({ messages, isLoading }) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div
      style={{
        flex: 1,
        overflowY: 'auto',
        padding: '16px 24px',
      }}
    >
      {messages.length === 0 && (
        <div style={{ textAlign: 'center', color: '#999', marginTop: 80 }}>
          <p style={{ fontSize: 18 }}>👋 {t.chat.greeting}</p>
          <p>{t.chat.greetingSub}</p>
        </div>
      )}
      {messages.map((msg, idx) => (
        <MessageItem
          key={idx}
          role={msg.role}
          content={msg.content}
          emotion={msg.emotion}
          isCrisis={msg.isCrisis}
        />
      ))}
      {isLoading && (
        <div style={{ textAlign: 'center', padding: 16 }}>
          <Spin tip={t.chat.thinking} />
        </div>
      )}
      <div ref={bottomRef} />
    </div>
  );
};

export default MessageList;
