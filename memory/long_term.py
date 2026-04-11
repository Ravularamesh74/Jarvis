"""
JARVIS Long-Term Memory System
-----------------------------
Capabilities:
- Persistent storage (SQLite)
- Semantic memory (embedding-ready)
- Context retrieval
- Knowledge storage
- Conversation history

Future Upgrade:
- Vector DB (FAISS / Chroma)
- LLM embedding integration
"""

import sqlite3
import datetime
import json
import logging
from typing import List, Optional

logger = logging.getLogger("JARVIS.Memory.LongTerm")
logger.setLevel(logging.INFO)


class LongTermMemory:
    def __init__(self, db_path: str = "data/memory/long_term.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._create_tables()

    # =========================================================
    # DATABASE SETUP
    # =========================================================
    def _create_tables(self):
        cursor = self.conn.cursor()

        # General memory storage
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            content TEXT,
            metadata TEXT,
            created_at TEXT
        )
        """)

        # Conversation history
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            message TEXT,
            response TEXT,
            timestamp TEXT
        )
        """)

        # Knowledge base
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE,
            value TEXT,
            updated_at TEXT
        )
        """)

        self.conn.commit()

    # =========================================================
    # STORE GENERIC MEMORY
    # =========================================================
    def store(self, content: str, mem_type: str = "general", metadata: dict = None):
        cursor = self.conn.cursor()

        cursor.execute("""
        INSERT INTO memories (type, content, metadata, created_at)
        VALUES (?, ?, ?, ?)
        """, (
            mem_type,
            content,
            json.dumps(metadata or {}),
            datetime.datetime.utcnow().isoformat()
        ))

        self.conn.commit()
        logger.info(f"[MEMORY STORED] {content}")

    # =========================================================
    # STORE CONVERSATION
    # =========================================================
    def store_conversation(self, user: str, message: str, response: str):
        cursor = self.conn.cursor()

        cursor.execute("""
        INSERT INTO conversations (user, message, response, timestamp)
        VALUES (?, ?, ?, ?)
        """, (
            user,
            message,
            response,
            datetime.datetime.utcnow().isoformat()
        ))

        self.conn.commit()

    # =========================================================
    # SAVE KNOWLEDGE (KEY-VALUE)
    # =========================================================
    def remember(self, key: str, value: str):
        cursor = self.conn.cursor()

        cursor.execute("""
        INSERT INTO knowledge (key, value, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(key) DO UPDATE SET
            value=excluded.value,
            updated_at=excluded.updated_at
        """, (
            key,
            value,
            datetime.datetime.utcnow().isoformat()
        ))

        self.conn.commit()
        logger.info(f"[KNOWLEDGE SAVED] {key} -> {value}")

    def recall(self, key: str) -> Optional[str]:
        cursor = self.conn.cursor()

        cursor.execute("SELECT value FROM knowledge WHERE key=?", (key,))
        row = cursor.fetchone()

        return row[0] if row else None

    # =========================================================
    # RETRIEVE RECENT MEMORY
    # =========================================================
    def get_recent(self, limit: int = 10) -> List[str]:
        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT content FROM memories
        ORDER BY created_at DESC
        LIMIT ?
        """, (limit,))

        return [row[0] for row in cursor.fetchall()]

    # =========================================================
    # SEARCH MEMORY (BASIC)
    # =========================================================
    def search(self, query: str, limit: int = 5) -> List[str]:
        """
        Basic LIKE search (replace with embeddings later)
        """
        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT content FROM memories
        WHERE content LIKE ?
        ORDER BY created_at DESC
        LIMIT ?
        """, (f"%{query}%", limit))

        return [row[0] for row in cursor.fetchall()]

    # =========================================================
    # GET CONVERSATION HISTORY
    # =========================================================
    def get_conversation(self, user: str, limit: int = 10):
        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT message, response FROM conversations
        WHERE user=?
        ORDER BY timestamp DESC
        LIMIT ?
        """, (user, limit))

        return cursor.fetchall()

    # =========================================================
    # DELETE MEMORY
    # =========================================================
    def delete(self, memory_id: int):
        cursor = self.conn.cursor()

        cursor.execute("DELETE FROM memories WHERE id=?", (memory_id,))
        self.conn.commit()

    # =========================================================
    # CLOSE CONNECTION
    # =========================================================
    def close(self):
        self.conn.close()


# =========================================================
# SINGLETON (OPTIONAL)
# =========================================================
_memory_instance: Optional[LongTermMemory] = None


def get_long_term_memory(db_path="data/memory/long_term.db"):
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = LongTermMemory(db_path)
    return _memory_instance


# =========================================================
# TEST MODE
# =========================================================
if __name__ == "__main__":
    mem = LongTermMemory()

    mem.store("User likes Python and AI")
    mem.remember("favorite_language", "Python")

    print(mem.recall("favorite_language"))
    print(mem.get_recent())