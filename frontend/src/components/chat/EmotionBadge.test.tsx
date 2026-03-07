import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import EmotionBadge from './EmotionBadge';

describe('EmotionBadge', () => {
  it('renders english label for known emotion', () => {
    render(<EmotionBadge emotion="fear" />);
    expect(screen.getByText('Fear')).toBeInTheDocument();
  });

  it('returns null when emotion is null', () => {
    const { container } = render(<EmotionBadge emotion={null} />);
    expect(container.firstChild).toBeNull();
  });

  it('renders raw emotion string for unknown emotion', () => {
    render(<EmotionBadge emotion="unknown_emotion" />);
    expect(screen.getByText('unknown_emotion')).toBeInTheDocument();
  });

  it('renders different labels for each emotion', () => {
    const cases = [
      { emotion: 'joy', label: 'Joy' },
      { emotion: 'sadness', label: 'Sadness' },
      { emotion: 'anger', label: 'Anger' },
      { emotion: 'love', label: 'Love' },
      { emotion: 'surprise', label: 'Surprise' },
    ];

    for (const { emotion, label } of cases) {
      const { unmount } = render(<EmotionBadge emotion={emotion} />);
      expect(screen.getByText(label)).toBeInTheDocument();
      unmount();
    }
  });
});
