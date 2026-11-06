# app.py
# Tanggung jawab tunggal: Entry point aplikasi —
# menginisialisasi semua modul dan meluncurkan server Gradio.

import sys
import os
import warnings

# Suppress warnings
warnings.simplefilter("ignore", category=DeprecationWarning)
warnings.simplefilter("ignore", category=RuntimeWarning)

# Pastikan direktori app ada di path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import DOCUMENT_FILES
from model_loader import (
    load_model_and_tokenizer,
    create_text_generation_pipeline,
    create_hyde_pipeline,
)
from document_processor import load_and_enrich_documents
from retriever import build_retrieval_system
from rag_pipeline import RAGPipeline
from ui import build_ui


def initialize_system():
    """Menginisialisasi seluruh sistem RAG secara berurutan."""
    print("=" * 60)
    print("   ASISTEN HUKUM AI INDONESIA — Inisialisasi Sistem")
    print("=" * 60)

    # 1. Load model & tokenizer
    model, tokenizer = load_model_and_tokenizer()

    # 2. Create pipelines
    llm = create_text_generation_pipeline(model, tokenizer)
    hyde_llm = create_hyde_pipeline(model, tokenizer)

    # 3. Load & enrich documents
    print("[4/6] Memuat dan memperkaya dokumen PDF...")
    enrichment_documents = load_and_enrich_documents(DOCUMENT_FILES)

    # 4. Build retrieval system
    parent_retriever, compression_retriever, cross_encoder_model = (
        build_retrieval_system(enrichment_documents, hyde_llm)
    )

    # 5. Build RAG pipeline
    print("[5/6] Membangun RAG pipeline...")
    pipeline = RAGPipeline(
        llm=llm,
        tokenizer=tokenizer,
        parent_retriever=parent_retriever,
        compression_retriever=compression_retriever,
        cross_encoder_model=cross_encoder_model,
    )
    print("  ✓ RAG pipeline siap")

    # 6. Build UI
    print("[6/6] Membangun antarmuka Gradio...")
    app = build_ui(pipeline)
    print("  ✓ UI siap\n")
    print("=" * 60)
    print("   SISTEM SIAP — Meluncurkan server...")
    print("=" * 60)

    return app


if __name__ == "__main__":
    app = initialize_system()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
    )
