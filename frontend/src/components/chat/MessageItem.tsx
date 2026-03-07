import React from 'react';
import { Typography } from 'antd';
import { RobotOutlined, UserOutlined } from '@ant-design/icons';
import EmotionBadge from './EmotionBadge';

const { Text } = Typography;

interface MessageItemProps {
  role: 'user' | 'assistant';
  content: string;
  emotion?: string | null;
  isCrisis?: boolean;
}

const MessageItem: React.FC<MessageItemProps> = ({ role, content, emotion, isCrisis }) => {
  const isUser = role === 'user';

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        marginBottom: 16,
        gap: 8,
      }}
    >
      {!isUser && (
        <div
          style={{
            width: 36,
            height: 36,
            borderRadius: '50%',
            background: '#5B8FB9',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}
        >
          <RobotOutlined style={{ color: '#fff', fontSize: 18 }} />
        </div>
      )}
      <div
        style={{
          maxWidth: '70%',
          padding: '12px 16px',
          borderRadius: isUser ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
          background: isUser ? '#5B8FB9' : isCrisis ? '#fff1f0' : '#f5f5f5',
          color: isUser ? '#fff' : '#333',
          border: isCrisis ? '1px solid #ff4d4f' : 'none',
          lineHeight: 1.6,
        }}
      >
        <Text style={{ color: isUser ? '#fff' : '#333', whiteSpace: 'pre-wrap' }}>
          {content}
        </Text>
        {!isUser && emotion && (
          <div style={{ marginTop: 8 }}>
            <EmotionBadge emotion={emotion} />
          </div>
        )}
      </div>
      {isUser && (
        <div
          style={{
            width: 36,
            height: 36,
            borderRadius: '50%',
            background: '#e8e8e8',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}
        >
          <UserOutlined style={{ color: '#666', fontSize: 18 }} />
        </div>
      )}
    </div>
  );
};

export default MessageItem;
