# config.py
# Tanggung jawab tunggal: Menyimpan semua konstanta konfigurasi aplikasi.

import os

# --- Konfigurasi Chunking ---
CHUNK_SIZE_PARENT = 800
CHUNK_SIZE_CHILD = 200

# --- Konfigurasi Model ---
CROSS_ENCODER_MODEL = "BAAI/bge-reranker-base"
EMBEDDING_MODEL = "BAAI/bge-m3"
MODEL_NAME = "hendrimardani/fine-tuned-model-indonesian-GRPO"

# --- Konfigurasi Generasi Teks ---
MAX_NEW_TOKENS = 1500
DO_SAMPLE = False

# --- Konfigurasi Retriever ---
RETRIEVER_TOP_K = 3
BM25_TOP_K = 3
ENSEMBLE_WEIGHTS = [0.5, 0.5]  # [BM25, Semantic]
RERANKER_TOP_N = 3
RELEVANCE_THRESHOLD = 0.0014

# --- Path Dokumen ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCUMENT_DIR = os.path.join(BASE_DIR, "Upload File Documents")

DOCUMENT_FILES = [
    os.path.join(DOCUMENT_DIR, "PP Nomor 35 Tahun 2021.pdf"),
    os.path.join(DOCUMENT_DIR, "PP Nomor 5 Tahun 2021.pdf"),
    os.path.join(DOCUMENT_DIR, "PP Nomor 51 Tahun 2023.pdf"),
    os.path.join(DOCUMENT_DIR, "UU Nomor 6 Tahun 2023.pdf"),
]

# --- Konfigurasi ChromaDB ---
CHROMA_COLLECTION_NAME = "split_parents"
CHROMA_PERSIST_DIR = os.path.join(BASE_DIR, "app", "chroma_db")
