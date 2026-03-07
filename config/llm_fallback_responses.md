# LLM Emotion Fallback Responses

**Description:** This document contains the static fallback response templates used when the primary LLM service is unavailable (e.g., API timeout, server error, rate limit exceeded). 

**Trigger Logic:**
These responses are mapped to the primary emotion label detected by the `nateraw/bert-base-uncased-emotion` model. They are designed to validate the user's current emotional state while gracefully explaining the technical issue.

---

## 1. Sadness
> "I can sense that you are going through a tough time right now, and I really want to be here for you. Unfortunately, my system is experiencing a temporary glitch, and I can't process my full response. Please know that your feelings are valid, and I'll be back online to listen to you properly very soon."

## 2. Joy
> "It sounds like you're experiencing some really positive moments, and I'd love to share in that joy with you! My system is taking a little unexpected break right now, so I can't reply fully. Hold onto that good energy, and let's chat more about it as soon as I'm reconnected."

## 3. Love
> "I can hear a lot of warmth and connection in your words, which is wonderful to see. I'm currently having a slight technical hiccup and can't give you the thoughtful reply you deserve right now. Please keep that positive feeling close, and I'll be back with you shortly."

## 4. Anger
> "I can hear how frustrated and upset you are, and it's completely understandable that you need to express that. I'm so sorry, but my system is temporarily down, which I know might be adding to the frustration. I want to give your thoughts the attention they need, so please give me a moment to get back online."

## 5. Fear
> "It sounds like you're feeling quite anxious or overwhelmed right now. Please take a deep breath—you are in a safe space. My processing system is currently experiencing a delay, so I can't respond fully at this exact moment. Try to ground yourself, and I will be right here for you as soon as my connection is restored."

## 6. Surprise
> "It sounds like something really caught you off guard! I'm eager to hear more about it, but my system is currently experiencing a brief pause. Give me just a little time to get my circuits back in order, and we can pick up right where we left off."
