# query_utils.py
# Tanggung jawab tunggal: Utilitas pemrosesan query —
# normalisasi angka romawi, filter metadata otomatis, dan web fallback.

import re
from ddgs import DDGS
from langchain_core.documents import Document

from config import RELEVANCE_THRESHOLD


def normalize_to_roman(text: str) -> str:
    """Mengubah penyebutan 'Bab [1-20]' dalam query menjadi angka romawi."""
    arabic_to_roman_map = {
        "1": "I", "2": "II", "3": "III", "4": "IV", "5": "V",
        "6": "VI", "7": "VII", "8": "VIII", "9": "IX", "10": "X",
        "11": "XI", "12": "XII", "13": "XIII", "14": "XIV",
        "15": "XV", "16": "XVI", "17": "XVII", "18": "XVIII",
        "19": "XIX", "20": "XX",
    }
    text_lower = text.lower()
    pattern = r"bab\s+(\d{1,2})\b"

    def replace_match(match):
        num_str = match.group(1)
        if num_str in arabic_to_roman_map:
            prefix = match.group(0).split()[0]
            return f"{prefix} {arabic_to_roman_map[num_str]}"
        return match.group(0)

    return re.sub(pattern, replace_match, text_lower)


def generate_dynamic_filter(query: str) -> dict:
    """
    Mengekstrak entitas hukum (BAB, Bagian, Pasal) dari query
    dan memformat filter ChromaDB.
    """
    query_lower = query.lower()
    filter_conditions = []

    # 1. Deteksi BAB
    bab_match = re.search(r'\bbab\s+([ivxlcdm]+|\d+)\b', query_lower)
    if bab_match:
        val = bab_match.group(1).upper()
        if val.isdigit():
            romans = {
                1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V',
                6: 'VI', 7: 'VII', 8: 'VIII', 9: 'IX', 10: 'X',
                11: 'XI', 12: 'XII', 13: 'XIII', 14: 'XIV', 15: 'XV',
                16: 'XVI', 17: 'XVII', 18: 'XVIII', 19: 'XIX', 20: 'XX',
            }
            val = romans.get(int(val), val)
        filter_conditions.append({"bab": {"$eq": f"BAB {val}"}})

    # 2. Deteksi BAGIAN
    bagian_match = re.search(r'\bbagian\s+([a-z]+)\b', query_lower)
    if bagian_match:
        bagian_val = bagian_match.group(1).capitalize()
        filter_conditions.append({"bagian": {"$eq": f"Bagian {bagian_val}"}})

    # 3. Deteksi PASAL
    pasal_match = re.search(r'\bpasal\s+(\d+)\b', query_lower)
    if pasal_match:
        pasal_num = pasal_match.group(1)
        filter_conditions.append({"pasal": {"$eq": f"Pasal {pasal_num}"}})

    if not filter_conditions:
        return {}
    elif len(filter_conditions) == 1:
        return filter_conditions[0]
    else:
        return {"$and": filter_conditions}


def search_duckduckgo_fallback(query: str, max_results: int = 10) -> str:
    """Fungsi cadangan pencarian web menggunakan DuckDuckGo."""
    try:
        with DDGS() as ddgs:
            raw_results = list(ddgs.text(query, max_results=max_results))
            cleaned_results = [
                r.get('body', '') for r in raw_results if r.get('body', '')
            ]
        if cleaned_results:
            return (
                "SUMBER INFORMASI DARI INTERNET (DuckDuckGo):\n"
                + "\n\n".join(cleaned_results)
            )
    except Exception as e:
        print(f"[ERROR] Gagal melakukan pencarian web: {e}")

    return "Informasi tidak ditemukan baik di dokumen lokal maupun di internet."


def invoke_hybrid_with_auto_filter(
    query, parent_retriever, compression_retriever, cross_encoder_model,
    threshold=RELEVANCE_THRESHOLD
):
    """
    Menerapkan filter metadata otomatis berdasarkan kata kunci yang terdeteksi,
    lalu memanggil hybrid retriever. Jika skor relevansi di bawah ambang batas,
    fallback ke pencarian DuckDuckGo.
    """
    cleaned_query = normalize_to_roman(query)
    auto_filter = generate_dynamic_filter(cleaned_query)

    if auto_filter:
        parent_retriever.search_kwargs["filter"] = auto_filter
        docs = compression_retriever.invoke(cleaned_query)
    else:
        if "filter" in parent_retriever.search_kwargs:
            parent_retriever.search_kwargs.pop("filter")
        docs = compression_retriever.invoke(cleaned_query)

    if docs:
        text_pairs = [(cleaned_query, doc.page_content) for doc in docs]
        scores = cross_encoder_model.score(text_pairs)
        top_score = float(max(scores))

        if top_score < threshold:
            web_result_text = search_duckduckgo_fallback(cleaned_query)
            return [
                Document(
                    page_content=web_result_text,
                    metadata={"source": "DuckDuckGo Search"},
                )
            ]
        else:
            top_docs = docs[0]
            return [
                Document(
                    page_content=top_docs.page_content,
                    metadata=top_docs.metadata,
                )
            ]
    else:
        web_result_text = search_duckduckgo_fallback(cleaned_query)
        return [
            Document(
                page_content=web_result_text,
                metadata={"source": "DuckDuckGo Search"},
            )
        ]
