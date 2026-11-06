# document_processor.py
# Tanggung jawab tunggal: Memuat dokumen PDF dan memperkaya metadata hukum.

import re
from typing import List
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document


class MetadataEnricher:
    """Mengekstrak dan memperkaya metadata struktur hukum (BAB, Bagian, Pasal) dari teks dokumen."""

    def __init__(self, doc_title: str):
        self.doc_title = doc_title

    def _is_true_article_header(self, text_before: str, text_after: str) -> bool:
        """
        Mengecek apakah 'Pasal X' benar-benar kepala pasal atau hanya penyebutan dalam teks.
        """
        # 1. Cek teks SETELAH "Pasal X" pada baris yang sama
        first_line_after = text_after.strip().split('\n')[0].lower()
        inline_body_keywords = ['ayat', 'huruf', 'angka']
        for kw in inline_body_keywords:
            if first_line_after.startswith(kw) or f" {kw} " in f" {first_line_after} ":
                return False

        # 2. Cek HANYA KATA TEPAT SEBELUM "Pasal X"
        words = text_before.strip().split()
        if words:
            last_word = words[-1].lower()
            clean_last_word = re.sub(r'[^\w]', '', last_word)
            reference_prepositions = {
                'dalam', 'pada', 'menurut', 'sebagaimana',
                'ketentuan', 'pasal', 'ayat'
            }
            if clean_last_word in reference_prepositions:
                return False
        return True

    def process_and_enrich(self, chunks: List[str]) -> List[Document]:
        """Memproses halaman-halaman PDF menjadi Document yang diperkaya metadata."""
        doc_title_string_match = re.search(
            r'(\w+\s[\w\d\s]*)(Nomor)\s(\d+)\s(\w+)\s(\d{4})',
            self.doc_title, re.IGNORECASE
        )

        legal_level = "Dokumen Hukum"
        current_number = "-"
        current_year = "2024"
        if doc_title_string_match:
            legal_level, _, current_number, _, current_year = doc_title_string_match.groups()

        documents = []
        current_bab = "Bab Umum"
        current_bagian = "Bagian Umum"
        current_paragraf = "-"
        current_pasal = "Pasal Umum"

        for page_idx, page_text in enumerate(chunks):
            current_page = page_idx + 1

            # Level 1: BAB
            bab_sections = re.split(r'(?=BAB\s+[IVXLCDM]+)', page_text, flags=re.IGNORECASE)
            for bab_sec in bab_sections:
                if not bab_sec.strip():
                    continue
                bab_match = re.search(r'(BAB\s+[IVXLCDM]+[^\n]*)', bab_sec, flags=re.IGNORECASE)
                if bab_match:
                    current_bab = bab_match.group(1).strip()

                # Level 2: Bagian
                bagian_sections = re.split(r'(?=Bagian\s+[A-Za-z]+)', bab_sec, flags=re.IGNORECASE)
                for bag_sec in bagian_sections:
                    if not bag_sec.strip():
                        continue
                    bag_match = re.search(r'(Bagian\s+ke[A-Za-z]+[^\n]*)', bag_sec, flags=re.IGNORECASE)
                    if bag_match:
                        current_bagian = bag_match.group(1).strip()
                    current_paragraf = "-"

                    # Level 3: Paragraf
                    paragraf_sections = re.split(
                        r'(?=Paragraf\s+\d+|Paragraf\s+[IVXLCDM]+)', bag_sec, flags=re.IGNORECASE
                    )
                    for para_sec in paragraf_sections:
                        if not para_sec.strip():
                            continue
                        para_match = re.search(
                            r'(Paragraf\s+\d+|Paragraf\s+[IVXLCDM]+[^\n]*)',
                            para_sec, flags=re.IGNORECASE
                        )
                        if para_match:
                            current_paragraf = para_match.group(1).strip()

                        # Level 4: Pasal
                        pattern = re.compile(r'(?:^|\n)\s*(Pasal\s+\d+)', re.IGNORECASE)
                        matches = list(pattern.finditer(para_sec))
                        if not matches:
                            continue

                        valid_splits = []
                        for i, m in enumerate(matches):
                            start_pos = m.start()
                            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(para_sec)
                            text_before = para_sec[:start_pos]
                            text_after = para_sec[m.end():end_pos]
                            if self._is_true_article_header(text_before, text_after):
                                valid_splits.append(m)

                        if not valid_splits:
                            valid_splits = [matches[0]]

                        for idx, m in enumerate(valid_splits):
                            start_pos = m.start()
                            end_pos = (
                                valid_splits[idx + 1].start()
                                if idx + 1 < len(valid_splits)
                                else len(para_sec)
                            )
                            p_sec = para_sec[start_pos:end_pos]
                            pasal_match = re.search(
                                r'(Pasal\s+\d+[^:\n]*)', p_sec, flags=re.IGNORECASE
                            )
                            if pasal_match:
                                current_pasal = pasal_match.group(1).strip()

                            content = p_sec.strip()
                            if content:
                                context_prefix = (
                                    f"[{self.doc_title} | {current_bab} | "
                                    f"{current_bagian} | {current_paragraf} | {current_pasal}]"
                                )
                                enriched_text = f"{context_prefix}\n{content}"
                                documents.append(
                                    Document(
                                        metadata={
                                            "halaman": current_page,
                                            "dokumen": self.doc_title,
                                            "tingkat_hukum": legal_level,
                                            "nomor": current_number,
                                            "tahun": current_year,
                                            "bab": current_bab,
                                            "bagian": current_bagian,
                                            "paragraf": current_paragraf,
                                            "pasal": current_pasal,
                                        },
                                        page_content=enriched_text,
                                    )
                                )
        return documents


def load_and_enrich_documents(file_paths: List[str]) -> List[Document]:
    """Memuat semua PDF dan memprosesnya menjadi dokumen yang diperkaya metadata."""
    enrichment_documents = []
    total_pages = 0

    for file_path in file_paths:
        loader = PyMuPDFLoader(file_path)
        raw_documents = loader.load()
        total_pages += len(raw_documents)
        print(f"  ✓ Memuat {len(raw_documents)} halaman dari: {file_path}")

        raw_chunks = [doc.page_content for doc in raw_documents]
        metadata_enricher = MetadataEnricher(file_path)
        enriched_chunks = metadata_enricher.process_and_enrich(raw_chunks)

        for item in enriched_chunks:
            enrichment_documents.append(
                Document(metadata=item.metadata, page_content=item.page_content)
            )

    print(f"  ✓ Total: {total_pages} halaman → {len(enrichment_documents)} chunk diperkaya")
    return enrichment_documents
