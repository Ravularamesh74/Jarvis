"""
JARVIS Vector Store (Semantic Memory)
------------------------------------
Capabilities:
- Store embeddings + text
- Perform similarity search
- Plug into memory_manager

Default:
- Uses numpy cosine similarity

Upgrade Path:
- FAISS / ChromaDB
"""

import numpy as np
import logging
from typing import List, Dict, Optional

logger = logging.getLogger("JARVIS.Memory.VectorStore")
logger.setLevel(logging.INFO)


class VectorStore:
    def __init__(self, embedding_model=None):
        """
        embedding_model -> function(text) -> List[float]
        """
        self.embedding_model = embedding_model or self._default_embed

        self.vectors: List[np.ndarray] = []
        self.texts: List[str] = []
        self.metadata: List[dict] = []

    # =========================================================
    # DEFAULT EMBEDDING (PLACEHOLDER)
    # =========================================================
    def _default_embed(self, text: str) -> np.ndarray:
        """
        VERY BASIC embedding (replace with real model)
        """
        return np.array([hash(word) % 1000 for word in text.split()][:50])

    # =========================================================
    # ADD MEMORY
    # =========================================================
    def add(self, text: str, metadata: dict = None):
        try:
            vector = np.array(self.embedding_model(text))

            self.vectors.append(vector)
            self.texts.append(text)
            self.metadata.append(metadata or {})

            logger.info(f"[VECTOR STORE] Added: {text[:50]}")

        except Exception as e:
            logger.error(f"[ERROR] Add failed: {e}")

    # =========================================================
    # COSINE SIMILARITY
    # =========================================================
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
            return 0.0
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    # =========================================================
    # SEARCH (CORE FUNCTION)
    # =========================================================
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        query_vector = np.array(self.embedding_model(query))

        scores = []

        for i, vector in enumerate(self.vectors):
            sim = self._cosine_similarity(query_vector, vector)

            scores.append({
                "text": self.texts[i],
                "score": sim,
                "metadata": self.metadata[i]
            })

        # Sort by similarity
        scores.sort(key=lambda x: x["score"], reverse=True)

        return scores[:top_k]

    # =========================================================
    # DELETE ENTRY
    # =========================================================
    def delete(self, index: int):
        if index < len(self.vectors):
            self.vectors.pop(index)
            self.texts.pop(index)
            self.metadata.pop(index)
            logger.info(f"[VECTOR STORE] Deleted index {index}")

    # =========================================================
    # CLEAR STORE
    # =========================================================
    def clear(self):
        self.vectors.clear()
        self.texts.clear()
        self.metadata.clear()
        logger.info("[VECTOR STORE] Cleared")

    # =========================================================
    # SIZE
    # =========================================================
    def size(self) -> int:
        return len(self.vectors)


# =========================================================
# SINGLETON
# =========================================================
_vector_store_instance: Optional[VectorStore] = None


def get_vector_store(embedding_model=None) -> VectorStore:
    global _vector_store_instance

    if _vector_store_instance is None:
        _vector_store_instance = VectorStore(embedding_model)

    return _vector_store_instance


# =========================================================
# TEST MODE
# =========================================================
if __name__ == "__main__":
    store = VectorStore()

    store.add("User likes Python and AI")
    store.add("JARVIS is an AI assistant")
    store.add("Weather is sunny today")

    results = store.search("AI system")

    for r in results:
        print(r)