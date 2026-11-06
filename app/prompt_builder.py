# prompt_builder.py
# Tanggung jawab tunggal: Membangun prompt sistem dan memformat
# template chat Llama 3 untuk generasi teks RAG.

SYSTEM_PROMPT = """
Anda adalah asisten hukum AI yang fokus pada pemecahan masalah (Problem Solver).

ATURAN WAJIB GENERASI:
1. Di dalam tag <think>...</think>: 
   - POLA PENALARAN: (1) Identifikasi poin pertanyaan user -> (2) Cocokkan dengan pasal/aturan yang relevan dari dokumen -> (3) Buat kesimpulan logis.
   - DILARANG MERANGKUM isi bab/pasal dari dokumen secara berurutan.
2. Di dalam tag <answer>...</answer>: 
   - Berikan jawaban langsung, jelas, dan solutif untuk user berdasarkan hasil analisis di <think>.
3. DILARANG MENULIS KATA DUPLIKAT Antara tag <think> dan <answer>.
"""

FEW_SHOT_USER = (
    "PERTANYAAN USER:\n"
    "Saya staf admin kerja lembur 3 jam, apakah berhak dapat uang lembur?\n\n"
    "DOKUMEN KONTEKS:\n"
    "PP No. 35 Tahun 2021 Pasal 27: Pengusaha wajib membayar upah lembur "
    "kepada pekerja/buruh yang dipekerjakan melebihi waktu kerja normal."
)

FEW_SHOT_ASSISTANT = (
    "<think>\n"
    "User menanyakan hak upah lembur untuk posisi staf admin (3 jam lembur). "
    "Berdasarkan PP No. 35 Tahun 2021 Pasal 27, kerja melebihi waktu normal "
    "wajib diberi upah lembur. Maka staf admin berhak atas upah 3 jam tersebut.\n"
    "</think>\n"
    "<answer>\n"
    "Ya, Anda berhak mendapatkan upah lembur. Berdasarkan PP No. 35 Tahun 2021 "
    "Pasal 27, pengusaha wajib membayar upah lembur untuk pekerja yang bekerja "
    "melebihi waktu kerja normal (8 jam sehari).\n"
    "</answer>"
)


def generate_with_llama3_template(inputs, tokenizer):
    """
    Memformat prompt menggunakan chat template Llama 3
    dengan few-shot example dan assistant prefill <think>.
    """
    context = inputs["context"]
    question = inputs["question"]

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        # Few-shot example
        {"role": "user", "content": FEW_SHOT_USER},
        {"role": "assistant", "content": FEW_SHOT_ASSISTANT},
        # Real user query
        {
            "role": "user",
            "content": (
                f"PERTANYAAN USER:\n{question}\n\n"
                f"DOKUMEN KONTEKS:\n{context}"
            ),
        },
    ]

    formatted_prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )

    # Assistant Prefill — memaksa model mulai dengan <think>
    formatted_prompt += "<think>\n"
    return formatted_prompt
