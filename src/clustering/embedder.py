# """
# embedder.py
# -----------
# Converts cleaned message text into dense semantic vectors using
# a sentence-transformers model.

# Model choice:
#   - "paraphrase-multilingual-MiniLM-L12-v2"
#     → Supports 50+ languages including Arabic & English
#     → Small (120MB), fast, good quality
#     → Perfect for WhatsApp messages which mix Arabic/English

# The model is loaded ONCE and reused across calls (lazy singleton).
# """

# import numpy as np
# from sentence_transformers import SentenceTransformer


# # ── Config ────────────────────────────────────────────────────────────────────
# MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
# BATCH_SIZE = 64     # How many sentences to embed at once


# class MessageEmbedder:
#     """
#     Encodes a list of message dicts into a numpy matrix of embeddings.
#     """

#     _model = None  # Class-level singleton — loaded once

#     def __init__(self):
#         if MessageEmbedder._model is None:
#             print(f"📦 Loading embedding model: {MODEL_NAME} ...")
#             MessageEmbedder._model = SentenceTransformer(MODEL_NAME)
#             print("✅ Model loaded.")
#         self.model = MessageEmbedder._model

#     def embed(self, messages: list[dict]) -> tuple[list[dict], np.ndarray]:
#         """
#         Embed a list of message dicts.

#         Args:
#             messages: List of dicts with at least 'content' key.

#         Returns:
#             (messages, embeddings)
#             - messages:   Same input list (unchanged)
#             - embeddings: np.ndarray of shape (N, embedding_dim)
#         """
#         texts = [msg["content"] for msg in messages]

#         print(f"🔢 Embedding {len(texts)} messages ...")
#         embeddings = self.model.encode(
#             texts,
#             batch_size=BATCH_SIZE,
#             show_progress_bar=len(texts) > 100,
#             convert_to_numpy=True,
#             normalize_embeddings=True,   # L2-normalize → cosine similarity = dot product
#         )
#         print(f"✅ Embedding done. Shape: {embeddings.shape}")
#         return messages, embeddings
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

class MessageEmbedder:
    _model = None

    def __init__(self):
        if MessageEmbedder._model is None:
            print(f"📦 Loading embedding model ...")
            MessageEmbedder._model = SentenceTransformer(MODEL_NAME)
            print("✅ Model loaded.")
        self.model = MessageEmbedder._model

    def embed(self, messages: list[dict]):
        texts = [msg["content"] for msg in messages]
        print(f"🔢 Embedding {len(texts)} messages ...")
        embeddings = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        print(f"✅ Embedding done.")
        return messages, embeddings