"""
Build FAISS indexes for all categories from text files in data/schemes/.

Usage:
    python scripts/build_all_indexes.py

Expects:
    data/schemes/<category>/*.txt  — text files containing scheme information
Produces:
    faiss_indexes/<category>/      — FAISS index files for each category
"""

import os
import sys
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "schemes"
INDEX_DIR = PROJECT_ROOT / "faiss_indexes"


def build_index_for_category(category_path: Path, output_path: Path) -> bool:
    """
    Build a FAISS index from all .txt files in a category directory.

    Args:
        category_path: Path to the category folder containing .txt files.
        output_path: Path where the FAISS index will be saved.

    Returns:
        True if index was built successfully, False otherwise.
    """
    category_name = category_path.name

    # Check if there are any .txt files
    txt_files = list(category_path.glob("*.txt"))
    if not txt_files:
        print(f"  ⚠️  No .txt files found in {category_path}. Skipping.")
        return False

    print(f"  📄 Found {len(txt_files)} text file(s)")

    # Load documents
    try:
        loader = DirectoryLoader(
            str(category_path),
            glob="*.txt",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
        )
        documents = loader.load()
    except Exception as e:
        print(f"  ❌ Error loading documents: {e}")
        return False

    if not documents:
        print(f"  ⚠️  No documents loaded from {category_path}. Skipping.")
        return False

    print(f"  📑 Loaded {len(documents)} document(s)")

    # Split documents into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    print(f"  ✂️  Split into {len(chunks)} chunk(s)")

    if not chunks:
        print(f"  ⚠️  No chunks after splitting. Skipping.")
        return False

    # Create embeddings and FAISS index
    try:
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        index = FAISS.from_documents(chunks, embeddings)
    except Exception as e:
        print(f"  ❌ Error creating embeddings/index: {e}")
        print(f"     Make sure Ollama is running and 'nomic-embed-text' model is pulled.")
        return False

    # Save the index
    output_path.mkdir(parents=True, exist_ok=True)
    try:
        index.save_local(str(output_path))
        print(f"  ✅ Index saved to {output_path}")
        return True
    except Exception as e:
        print(f"  ❌ Error saving index: {e}")
        return False


def main():
    """Build FAISS indexes for all category subdirectories in data/schemes/."""
    print("=" * 60)
    print("🔨 FAISS Index Builder for Citizen Services Assistant")
    print("=" * 60)

    if not DATA_DIR.exists():
        print(f"\n❌ Data directory not found: {DATA_DIR}")
        print(f"   Please create the directory and add .txt files for each category.")
        print(f"   Expected structure:")
        print(f"     data/schemes/agriculture/*.txt")
        print(f"     data/schemes/health/*.txt")
        print(f"     data/schemes/education/*.txt")
        print(f"     ... etc.")
        sys.exit(1)

    # Find all subdirectories
    categories = sorted([
        d for d in DATA_DIR.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    ])

    if not categories:
        print(f"\n⚠️  No category subdirectories found in {DATA_DIR}")
        print(f"   Please add subdirectories with .txt files.")
        sys.exit(1)

    print(f"\n📂 Data directory: {DATA_DIR}")
    print(f"📂 Index output:   {INDEX_DIR}")
    print(f"📋 Found {len(categories)} category folder(s)\n")

    success_count = 0
    fail_count = 0

    for category_path in categories:
        category_name = category_path.name
        output_path = INDEX_DIR / category_name
        print(f"🔄 Processing: {category_name}")

        if build_index_for_category(category_path, output_path):
            success_count += 1
        else:
            fail_count += 1

        print()

    # Summary
    print("=" * 60)
    print(f"📊 Build Summary:")
    print(f"   ✅ Successful: {success_count}")
    print(f"   ❌ Failed/Skipped: {fail_count}")
    print(f"   📁 Total categories: {len(categories)}")
    print("=" * 60)

    if success_count > 0:
        print(f"\n🎉 Indexes are ready at: {INDEX_DIR}")
    else:
        print(f"\n⚠️  No indexes were built. Check your data directory and Ollama setup.")


if __name__ == "__main__":
    main()
