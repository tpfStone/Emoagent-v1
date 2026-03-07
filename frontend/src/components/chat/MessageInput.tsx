import React, { useState } from 'react';
import { Input, Button } from 'antd';
import { SendOutlined } from '@ant-design/icons';
import t from '../../locales';

const { TextArea } = Input;

interface MessageInputProps {
  onSend: (text: string) => void;
  disabled: boolean;
}

const MessageInput: React.FC<MessageInputProps> = ({ onSend, disabled }) => {
  const [text, setText] = useState('');

  const handleSend = () => {
    const trimmed = text.trim();
    if (!trimmed) return;
    onSend(trimmed);
    setText('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        gap: 12,
        padding: '12px 24px',
        borderTop: '1px solid #f0f0f0',
        background: '#fff',
      }}
    >
      <TextArea
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={t.chat.placeholder}
        autoSize={{ minRows: 1, maxRows: 4 }}
        disabled={disabled}
        style={{ borderRadius: 12 }}
      />
      <Button
        type="primary"
        icon={<SendOutlined />}
        onClick={handleSend}
        disabled={disabled || !text.trim()}
        style={{ borderRadius: 12, height: 'auto', minHeight: 40 }}
      >
        {t.chat.send}
      </Button>
    </div>
  );
};

export default MessageInput;
