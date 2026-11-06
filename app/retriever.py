# retriever.py
# Tanggung jawab tunggal: Membangun dan mengelola komponen retrieval
# (vector store, BM25, hybrid retriever, cross-encoder reranker).

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_community.vectorstores import Chroma
from langchain_classic.retrievers import (
    ParentDocumentRetriever,
    EnsembleRetriever,
    ContextualCompressionRetriever,
)
from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
from langchain_classic.chains import HypotheticalDocumentEmbedder
from langchain_community.retrievers import BM25Retriever
from langchain_core.stores import InMemoryByteStore
from langchain_core.documents import Document

from config import (
    CHUNK_SIZE_PARENT,
    CHUNK_SIZE_CHILD,
    EMBEDDING_MODEL,
    CROSS_ENCODER_MODEL,
    CHROMA_COLLECTION_NAME,
    CHROMA_PERSIST_DIR,
    RETRIEVER_TOP_K,
    BM25_TOP_K,
    ENSEMBLE_WEIGHTS,
    RERANKER_TOP_N,
)


def build_retrieval_system(enrichment_documents, hyde_llm):
    """
    Membangun seluruh sistem retrieval:
    - Embedding + HyDE
    - VectorStore (ChromaDB)
    - ParentDocumentRetriever
    - BM25 Retriever
    - EnsembleRetriever (Hybrid)
    - CrossEncoder Reranker + ContextualCompressionRetriever

    Returns:
        tuple: (parent_retriever, compression_retriever, cross_encoder_model)
    """
    print("[3/6] Membangun sistem retrieval...")

    # --- Splitters ---
    parent_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE_PARENT)
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE_CHILD)

    # --- Embeddings + HyDE ---
    print("  → Memuat embedding model...")
    base_embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    hyde_embeddings = HypotheticalDocumentEmbedder.from_llm(
        hyde_llm, base_embeddings, prompt_key="web_search"
    )
    print(f"  ✓ Embedding '{EMBEDDING_MODEL}' + HyDE siap")

    # --- VectorStore ---
    print("  → Membuat vector store ChromaDB...")
    vectorstore = Chroma.from_documents(
        documents=enrichment_documents,
        embedding=hyde_embeddings,
        collection_name=CHROMA_COLLECTION_NAME,
        persist_directory=CHROMA_PERSIST_DIR,
    )

    # --- Parent Document Retriever ---
    print("  → Membangun Parent Document Retriever...")
    docstore = InMemoryByteStore()

    parent_retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=docstore,
        child_splitter=child_splitter,
        parent_splitter=parent_splitter,
        search_type="similarity",
        search_kwargs={"k": RETRIEVER_TOP_K},
    )

    batch_size = 200
    for i in range(0, len(enrichment_documents), batch_size):
        batched = enrichment_documents[i : i + batch_size]
        parent_retriever.add_documents(batched)
    print(f"  ✓ {len(enrichment_documents)} dokumen diindeks ke parent retriever")

    # --- BM25 Retriever ---
    print("  → Membangun BM25 Retriever...")
    bm25_retriever = BM25Retriever.from_documents(enrichment_documents)
    bm25_retriever.k = BM25_TOP_K

    # --- Hybrid Retriever ---
    hybrid_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, parent_retriever],
        weights=ENSEMBLE_WEIGHTS,
    )
    print(f"  ✓ Hybrid Retriever siap (BM25={ENSEMBLE_WEIGHTS[0]}, Semantic={ENSEMBLE_WEIGHTS[1]})")

    # --- Cross-Encoder Reranker ---
    print("  → Memuat Cross-Encoder Reranker...")
    cross_encoder_model = HuggingFaceCrossEncoder(model_name=CROSS_ENCODER_MODEL)
    cross_encoder_reranker = CrossEncoderReranker(
        model=cross_encoder_model, top_n=RERANKER_TOP_N
    )

    compression_retriever = ContextualCompressionRetriever(
        base_compressor=cross_encoder_reranker,
        base_retriever=hybrid_retriever,
    )
    print(f"  ✓ Reranker '{CROSS_ENCODER_MODEL}' siap (top_n={RERANKER_TOP_N})")

    return parent_retriever, compression_retriever, cross_encoder_model
