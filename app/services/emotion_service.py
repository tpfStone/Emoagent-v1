import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from app.config import Settings
from app.utils.metrics import bert_latency, emotion_distribution

logger = logging.getLogger("emoagent")

EMOTION_LABELS = ["sadness", "joy", "love", "anger", "fear", "surprise"]

_executor = ThreadPoolExecutor(max_workers=1)


class EmotionService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._model = None
        self._tokenizer = None
        self._device = settings.BERT_DEVICE
        self._load_failed = False

    def _load_model(self):
        if self._model is not None:
            return
        if self._load_failed:
            raise RuntimeError("BERT model previously failed to load; skipping retry this session")
        logger.info(f"Loading BERT model: {self.settings.BERT_MODEL_NAME}")
        try:
            self._tokenizer = AutoTokenizer.from_pretrained(
                self.settings.BERT_MODEL_NAME,
                cache_dir=self.settings.BERT_MODEL_PATH,
            )
            self._model = AutoModelForSequenceClassification.from_pretrained(
                self.settings.BERT_MODEL_NAME,
                cache_dir=self.settings.BERT_MODEL_PATH,
            )
            self._model.to(self._device)
            self._model.eval()
            logger.info("BERT model loaded successfully")
        except Exception as e:
            self._load_failed = True
            raise RuntimeError(f"BERT model failed to load: {e}") from e

    def _classify_sync(self, text: str) -> tuple[str, int]:
        self._load_model()
        start = time.perf_counter()

        inputs = self._tokenizer(
            text, return_tensors="pt", truncation=True, max_length=512, padding=True
        )
        inputs = {k: v.to(self._device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self._model(**inputs)

        predicted_idx = torch.argmax(outputs.logits, dim=-1).item()
        emotion = EMOTION_LABELS[predicted_idx]
        latency_ms = int((time.perf_counter() - start) * 1000)
        
        bert_latency.observe((time.perf_counter() - start))
        emotion_distribution.labels(emotion=emotion).inc()

        logger.debug(f"Emotion classified: {emotion} ({latency_ms}ms)")
        return emotion, latency_ms

    async def classify_emotion(self, text: str, timeout: float = 45.0) -> tuple[str, int]:
        """
        对文本进行情绪分类（在线程池中执行，不阻塞事件循环）。
        首次加载模型时允许较长超时，后续推理毫秒级完成。
        Returns: (emotion_label, latency_ms)
        """
        loop = asyncio.get_running_loop()
        try:
            return await asyncio.wait_for(
                loop.run_in_executor(_executor, self._classify_sync, text),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            self._load_failed = True
            raise RuntimeError(f"BERT model loading timed out after {timeout}s")
