# rag_pipeline.py
# Tanggung jawab tunggal: Mengorkestrasi seluruh pipeline RAG —
# dari query masuk hingga respons terstruktur (think + answer).

import time
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

from query_utils import normalize_to_roman, invoke_hybrid_with_auto_filter
from prompt_builder import generate_with_llama3_template
from response_parser import clean_legal_response, parse_think_answer


class RAGPipeline:
    """Kelas yang mengelola pipeline RAG end-to-end."""

    def __init__(self, llm, tokenizer, parent_retriever,
                 compression_retriever, cross_encoder_model):
        self.llm = llm
        self.tokenizer = tokenizer
        self.parent_retriever = parent_retriever
        self.compression_retriever = compression_retriever
        self.cross_encoder_model = cross_encoder_model
        self._chain = self._build_chain()

    def _format_docs(self, docs):
        """Menggabungkan page_content dari dokumen-dokumen yang relevan."""
        return "\n\n".join(doc.page_content for doc in docs)

    def _build_chain(self):
        """Membangun LangChain LCEL chain untuk RAG pipeline."""
        chain = (
            {
                "context": RunnableLambda(
                    lambda query: invoke_hybrid_with_auto_filter(
                        query,
                        self.parent_retriever,
                        self.compression_retriever,
                        self.cross_encoder_model,
                    )
                )
                | self._format_docs,
                "question": RunnablePassthrough(),
            }
            | RunnableLambda(
                lambda inputs: generate_with_llama3_template(inputs, self.tokenizer)
            )
            | self.llm
            | StrOutputParser()
            | RunnableLambda(clean_legal_response)
        )
        return chain

    def generate(self, query: str) -> dict:
        """
        Menjalankan pipeline RAG pada sebuah query.

        Args:
            query: Pertanyaan dari pengguna.

        Returns:
            dict dengan key:
                - 'think': Proses penalaran model
                - 'answer': Jawaban akhir
                - 'elapsed_seconds': Waktu pemrosesan
                - 'raw_response': Response mentah dari chain
        """
        cleaned_query = normalize_to_roman(query)

        start_time = time.time()
        raw_response = self._chain.invoke(cleaned_query)
        elapsed = time.time() - start_time

        parsed = parse_think_answer(raw_response)
        parsed["elapsed_seconds"] = round(elapsed, 2)
        parsed["raw_response"] = raw_response

        return parsed
