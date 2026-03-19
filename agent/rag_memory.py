import json
import os
from typing import Dict, List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class RAGMemory:
    def __init__(self, memory_path: str = "agent_memory.json"):
        self.memory_path = memory_path
        self.entries: List[Dict] = []
        self.vectorizer = TfidfVectorizer(stop_words="english", max_features=500)
        self.tfidf_matrix = None
        self._load()

    def _load(self):
        if not os.path.exists(self.memory_path):
            self.entries = []
            self.tfidf_matrix = None
            return

        try:
            with open(self.memory_path, "r", encoding="utf-8") as f:
                self.entries = json.load(f)
        except Exception:
            self.entries = []

        self._build_index()

    def _save(self):
        try:
            with open(self.memory_path, "w", encoding="utf-8") as f:
                json.dump(self.entries, f, indent=2)
        except Exception:
            pass

    def _build_index(self):
        docs = []
        for e in self.entries:
            docs.append((e.get("query", "") + " " + e.get("response", "")).strip())

        if not docs:
            self.tfidf_matrix = None
            return

        self.tfidf_matrix = self.vectorizer.fit_transform(docs)

    def add_interaction(self, query: str, response: str):
        self.entries.append({"query": query, "response": response})
        self._build_index()
        self._save()

    def get_relevant(self, query: str, top_k: int = 3) -> List[Dict]:
        if not self.tfidf_matrix or not self.entries:
            return []

        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        ranked_idx = scores.argsort()[::-1]
        top_idx = [i for i in ranked_idx if scores[i] > 0][:top_k]

        return [self.entries[i] for i in top_idx]
