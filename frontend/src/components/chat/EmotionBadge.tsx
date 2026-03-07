import React from 'react';
import { Tag } from 'antd';
import { EMOTION_COLORS, EMOTION_LABELS } from '../../utils/constants';

interface EmotionBadgeProps {
  emotion: string | null;
}

const EmotionBadge: React.FC<EmotionBadgeProps> = ({ emotion }) => {
  if (!emotion) return null;
  return (
    <Tag color={EMOTION_COLORS[emotion] || 'default'}>
      {EMOTION_LABELS[emotion] || emotion}
    </Tag>
  );
};

export default EmotionBadge;
