import { describe, it, expect } from 'vitest';
import { EMOTION_COLORS, EMOTION_LABELS } from './constants';

describe('constants', () => {
  it('EMOTION_LABELS contains all 6 emotions', () => {
    const emotions = ['joy', 'sadness', 'fear', 'anger', 'love', 'surprise'];
    for (const emotion of emotions) {
      expect(EMOTION_LABELS[emotion]).toBeDefined();
    }
  });

  it('EMOTION_COLORS contains all 6 emotions', () => {
    const emotions = ['joy', 'sadness', 'fear', 'anger', 'love', 'surprise'];
    for (const emotion of emotions) {
      expect(EMOTION_COLORS[emotion]).toBeDefined();
      expect(EMOTION_COLORS[emotion]).toMatch(/^#[0-9a-f]{6}$/);
    }
  });

  it('EMOTION_LABELS and EMOTION_COLORS have same keys', () => {
    expect(Object.keys(EMOTION_LABELS).sort()).toEqual(
      Object.keys(EMOTION_COLORS).sort()
    );
  });
});
