"""
FAISS-based RAG retriever for the Citizen Services Assistant.
Lazily loads per-category FAISS indexes and performs similarity search.
"""

import os
import warnings
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings

# Module-level cache for loaded FAISS indexes
_index_cache: dict[str, FAISS] = {}

# Base directory for FAISS indexes (relative to project root)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_INDEX_BASE_DIR = _PROJECT_ROOT / "faiss_indexes"


def _get_embeddings() -> OllamaEmbeddings:
    """Create the embedding model instance."""
    return OllamaEmbeddings(model="nomic-embed-text")


def _load_index(category: str) -> FAISS | None:
    """
    Load a FAISS index for the given category from disk.

    Args:
        category: The category name (matches subfolder name).

    Returns:
        A FAISS vector store instance, or None if not found.
    """
    index_path = _INDEX_BASE_DIR / category
    if not index_path.exists():
        warnings.warn(
            f"FAISS index not found for category '{category}' "
            f"at {index_path}. Run scripts/build_all_indexes.py to build indexes."
        )
        return None

    try:
        embeddings = _get_embeddings()
        index = FAISS.load_local(
            str(index_path),
            embeddings,
            allow_dangerous_deserialization=True,
        )
        return index
    except Exception as e:
        warnings.warn(f"Failed to load FAISS index for '{category}': {e}")
        return None


def retrieve(category: str, query: str, k: int = 3) -> str:
    """
    Retrieve relevant document chunks for a query within a category.

    Args:
        category: The service category to search within.
        query: The user's question or query text.
        k: Number of top results to return (default 3).

    Returns:
        Concatenated page_content of the top-k matching documents.
        Returns empty string if no index is available.
    """
    if not category:
        return ""

    # Lazy-load and cache the index
    if category not in _index_cache:
        index = _load_index(category)
        if index is None:
            return ""
        _index_cache[category] = index

    index = _index_cache[category]

    try:
        results = index.similarity_search(query, k=k)
        if not results:
            return ""
        return "\n\n---\n\n".join(doc.page_content for doc in results)
    except Exception as e:
        warnings.warn(f"FAISS similarity search failed for '{category}': {e}")
        return ""
