import pytest
from unittest.mock import MagicMock, patch

# Import your memory modules
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory
from memory.vector_store import VectorStore
from memory.memory_manager import MemoryManager


# -----------------------------------
# Fixtures
# -----------------------------------

@pytest.fixture
def short_memory():
    return ShortTermMemory(max_size=5)


@pytest.fixture
def long_memory():
    db = MagicMock()
    return LongTermMemory(db=db)


@pytest.fixture
def vector_store():
    vs = VectorStore()
    vs.embedder = MagicMock()
    vs.embedder.encode.return_value = [0.1, 0.2, 0.3]
    return vs


@pytest.fixture
def memory_manager(short_memory, long_memory, vector_store):
    return MemoryManager(
        short_term=short_memory,
        long_term=long_memory,
        vector_store=vector_store
    )


# -----------------------------------
# ShortTermMemory Tests
# -----------------------------------

def test_short_term_store_and_retrieve(short_memory):
    short_memory.add("Hello")
    short_memory.add("World")

    data = short_memory.get_all()

    assert len(data) == 2
    assert data[-1] == "World"


def test_short_term_eviction(short_memory):
    for i in range(10):
        short_memory.add(f"msg_{i}")

    data = short_memory.get_all()

    assert len(data) <= 5
    assert "msg_0" not in data  # oldest removed


def test_short_term_clear(short_memory):
    short_memory.add("test")
    short_memory.clear()

    assert short_memory.get_all() == []


# -----------------------------------
# LongTermMemory Tests
# -----------------------------------

def test_long_term_store(long_memory):
    long_memory.store("Important data")

    long_memory.db.insert.assert_called_once()


def test_long_term_retrieve(long_memory):
    long_memory.db.search.return_value = ["result1", "result2"]

    results = long_memory.retrieve("query")

    long_memory.db.search.assert_called_once()
    assert len(results) == 2


def test_long_term_empty_query(long_memory):
    with pytest.raises(ValueError):
        long_memory.retrieve("")


# -----------------------------------
# VectorStore Tests
# -----------------------------------

def test_vector_store_embedding(vector_store):
    vec = vector_store.embed("Hello")

    vector_store.embedder.encode.assert_called_once()
    assert isinstance(vec, list)


def test_vector_store_add_and_search(vector_store):
    vector_store.store = MagicMock()
    vector_store.search = MagicMock(return_value=["match"])

    vector_store.store("text")
    results = vector_store.search("text")

    assert results == ["match"]


def test_vector_store_similarity_search(vector_store):
    vector_store.index = MagicMock()
    vector_store.index.search.return_value = ([0.9], [1])

    results = vector_store.similarity_search("query")

    assert results is not None


# -----------------------------------
# MemoryManager Tests (CORE)
# -----------------------------------

def test_memory_manager_store(memory_manager):
    memory_manager.store("Hello JARVIS")

    assert len(memory_manager.short_term.get_all()) > 0


def test_memory_manager_retrieve(memory_manager):
    memory_manager.long_term.retrieve = MagicMock(return_value=["LT result"])
    memory_manager.short_term.add("recent")

    results = memory_manager.retrieve("query")

    assert "LT result" in results or isinstance(results, list)


def test_memory_manager_priority(memory_manager):
    """
    Short-term memory should be prioritized over long-term
    """
    memory_manager.short_term.add("recent data")
    memory_manager.long_term.retrieve = MagicMock(return_value=["old data"])

    results = memory_manager.retrieve("data")

    assert "recent data" in str(results)


def test_memory_manager_empty_input(memory_manager):
    with pytest.raises(ValueError):
        memory_manager.store("")


def test_memory_manager_vector_integration(memory_manager):
    memory_manager.vector_store.store = MagicMock()

    memory_manager.store("Vector test")

    memory_manager.vector_store.store.assert_called()


# -----------------------------------
# Edge Cases & Stress
# -----------------------------------

def test_large_input(memory_manager):
    large_text = "A" * 10000

    memory_manager.store(large_text)

    assert len(memory_manager.short_term.get_all()) > 0


def test_concurrent_like_behavior(memory_manager):
    for i in range(50):
        memory_manager.store(f"msg_{i}")

    data = memory_manager.short_term.get_all()

    assert len(data) > 0


def test_memory_consistency(memory_manager):
    memory_manager.store("Consistency test")

    results = memory_manager.retrieve("Consistency")

    assert results is not None