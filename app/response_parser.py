# response_parser.py
# Tanggung jawab tunggal: Membersihkan dan memformat output LLM —
# ekstraksi tag <think>/<answer>, deduplikasi, dan formatting final.

import re


def clean_legal_response(raw_output: str) -> str:
    """Membersihkan output mentah LLM dari artefak template dan token sampah."""
    if not raw_output:
        return ""

    # Sisipkan tag <think> jika terpotong akibat prefill
    if not raw_output.startswith("<think>") and "</think>" in raw_output:
        raw_output = "<think>\n" + raw_output

    # Bersihkan token khusus Llama 3
    stop_tokens = [
        "<|start_header_id|>", "<|end_header_id|>",
        "<|eot_id|>", "<|end_of_text|>",
    ]
    for token in stop_tokens:
        if token in raw_output:
            raw_output = raw_output.split(token)[0]

    # Ekstrak tag <think> dan <answer>
    think_match = re.search(r"<think>(.*?)</think>", raw_output, re.DOTALL)
    answer_match = re.search(r"<answer>(.*?)</answer>", raw_output, re.DOTALL)

    think_text = think_match.group(1).strip() if think_match else ""
    answer_text = answer_match.group(1).strip() if answer_match else ""

    # Jika tag <answer> tidak ada tapi ada teks setelah </think>
    if not answer_text and "</think>" in raw_output:
        answer_text = (
            raw_output.split("</think>")[-1]
            .replace("<answer>", "")
            .replace("</answer>", "")
            .strip()
        )

    if think_text and answer_text:
        return f"<think>\n{think_text}\n</think>\n<answer>\n{answer_text}\n</answer>"
    elif answer_text:
        return f"<answer>\n{answer_text}\n</answer>"

    return raw_output.strip()


def remove_duplicate_paragraphs(text: str) -> str:
    """Menghapus paragraf atau kalimat yang diulang secara persis."""
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    seen = []
    for line in lines:
        if line not in seen:
            seen.append(line)
    return "\n".join(seen)


def parse_think_answer(response: str) -> dict:
    """
    Memparse response menjadi dict dengan key 'think' dan 'answer',
    dengan deduplikasi paragraf.
    """
    think_match = re.search(r"<think>(.*?)</think>", response, re.DOTALL)
    answer_match = re.search(r"<answer>(.*?)</answer>", response, re.DOTALL)

    think_text = think_match.group(1).strip() if think_match else ""
    answer_text = answer_match.group(1).strip() if answer_match else response.strip()

    # Bersihkan sisa tag
    answer_text = re.sub(r"</?answer>", "", answer_text).strip()

    # Deduplikasi
    think_clean = remove_duplicate_paragraphs(think_text)
    answer_clean = remove_duplicate_paragraphs(answer_text)

    return {
        "think": think_clean,
        "answer": answer_clean,
    }
