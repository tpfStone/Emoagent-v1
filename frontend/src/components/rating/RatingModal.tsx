import React, { useState } from 'react';
import { Modal, Slider, Typography } from 'antd';
import { ratingAPI } from '../../api/rating';
import { useSessionStore } from '../../stores/sessionStore';
import t from '../../locales';

const { Text, Title } = Typography;

interface RatingModalProps {
  type: 'before' | 'after';
  open: boolean;
  onClose: () => void;
}

const sliderMarks: Record<number, string> = {
  1: '1',
  5: '5',
  10: '10',
};

const RatingModal: React.FC<RatingModalProps> = ({ type, open, onClose }) => {
  const [score, setScore] = useState(5);
  const [loading, setLoading] = useState(false);
  const { token, sessionId } = useSessionStore();

  const handleSubmit = async () => {
    if (!token || !sessionId) return;
    setLoading(true);
    try {
      await ratingAPI.submitRating({
        session_id: sessionId,
        rating_type: type,
        score,
        token,
      });
      onClose();
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      title={t.rating.title}
      open={open}
      onOk={handleSubmit}
      onCancel={onClose}
      okText={t.rating.submit}
      cancelText={t.rating.cancel}
      confirmLoading={loading}
      maskClosable={false}
    >
      <Text>
        {type === 'before' ? t.rating.promptBefore : t.rating.promptAfter}
      </Text>
      <Slider
        min={1}
        max={10}
        value={score}
        onChange={setScore}
        marks={sliderMarks}
        style={{ marginTop: 24 }}
      />
      <div style={{ textAlign: 'center', marginTop: 8 }}>
        <Title level={3}>{score} / 10</Title>
      </div>
    </Modal>
  );
};

export default RatingModal;
