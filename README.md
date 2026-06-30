# Citizen Services Assistant

A complete, runnable web application — a government services dashboard with an embedded AI chatbot for each service category. 

## Tech Stack
- **LangChain + Ollama** — local LLM pipeline (`llama3`, `nomic-embed-text`)
- **FAISS** — vector database for government scheme documents, partitioned per service category
- **spaCy** — intent detection and slot filling (`en_core_web_sm`)
- **Flask** — REST API backend serving the chatbot logic
- **Streamlit** — citizen-facing UI

## Prerequisites
- Python 3.9+
- [Ollama](https://ollama.ai/) installed locally

## Setup Instructions

1. **Install Ollama & Pull Models**
   Ensure Ollama is running, then pull the required models:
   ```bash
   ollama pull llama3
   ollama pull nomic-embed-text
   ```

2. **Setup Python Environment**
   Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Download spaCy Model**
   ```bash
   python -m spacy download en_core_web_sm
   ```

4. **Build FAISS Indexes**
   Process the placeholder scheme documents into vector embeddings:
   ```bash
   python scripts/build_all_indexes.py
   ```

5. **Run the Application**
   You'll need two terminals for this.
   
   **Terminal 1 (Backend):**
   ```bash
   python -m app.main
   ```
   *Runs on http://localhost:5000*
   
   **Terminal 2 (Frontend):**
   ```bash
   streamlit run ui/streamlit_app.py
   ```
   *Runs on http://localhost:8501*

## Project Structure
- `data/schemes/`: Category folders containing realistic `.txt` files describing schemes.
- `faiss_indexes/`: Generated vector databases per category.
- `app/`: Flask backend containing `catalog.py`, NLP logic (`intent.py`, `slots.py`), RAG logic (`retriever.py`, `eligibility.py`), and LLM pipeline.
- `ui/`: Streamlit frontend with extensive custom CSS for an accessible, beautiful user interface.
- `scripts/`: Index building script.
