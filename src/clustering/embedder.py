import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

class MessageEmbedder:
    _model = None

    def __init__(self):
        if MessageEmbedder._model is None:
            print(f"Loading embedding model ...")
            MessageEmbedder._model = SentenceTransformer(MODEL_NAME)
            print("Model loaded.")
        self.model = MessageEmbedder._model

    def embed(self, messages: list[dict]):
        texts = [msg["content"] for msg in messages]
        print(f"Embedding {len(texts)} messages ...")
        embeddings = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        print(f"Embedding done.")
        return messages, embeddings