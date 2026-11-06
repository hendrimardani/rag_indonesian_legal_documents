# model_loader.py
# Tanggung jawab tunggal: Memuat model LLM, tokenizer, dan pipeline generasi teks.

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, BitsAndBytesConfig
from langchain_huggingface import HuggingFacePipeline

from config import MODEL_NAME, MAX_NEW_TOKENS, DO_SAMPLE


def load_model_and_tokenizer():
    """Memuat model LLM dengan kuantisasi 4-bit dan tokenizernya."""
    print("[1/6] Memuat model & tokenizer...")

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    )

    model = AutoModelForCausalLM.from_pretrained(
        pretrained_model_name_or_path=MODEL_NAME,
        quantization_config=bnb_config,
        device_map="auto",
    )

    tokenizer = AutoTokenizer.from_pretrained(
        pretrained_model_name_or_path=MODEL_NAME
    )

    print(f"  ✓ Model '{MODEL_NAME}' berhasil dimuat (4-bit quantized)")
    return model, tokenizer


def create_text_generation_pipeline(model, tokenizer):
    """Membuat pipeline generasi teks untuk RAG."""
    print("[2/6] Membuat pipeline generasi teks...")

    text_gen_pipeline = pipeline(
        model=model,
        tokenizer=tokenizer,
        task="text-generation",
        do_sample=DO_SAMPLE,
        max_new_tokens=MAX_NEW_TOKENS,
        return_full_text=False,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=(
            tokenizer.pad_token_id
            if tokenizer.pad_token_id is not None
            else tokenizer.eos_token_id
        ),
    )

    llm = HuggingFacePipeline(pipeline=text_gen_pipeline)
    print(f"  ✓ Pipeline teks siap (max_new_tokens={MAX_NEW_TOKENS})")
    return llm


def create_hyde_pipeline(model, tokenizer):
    """Membuat pipeline HyDE (Hypothetical Document Embedder) untuk retrieval."""
    print("  → Membuat HyDE pipeline...")

    hyde_pipeline = pipeline(
        model=model,
        tokenizer=tokenizer,
        task="text-generation",
        temperature=0.7,
        num_return_sequences=2,
        do_sample=True,
        repetition_penalty=1.15,
        max_new_tokens=128,
        return_full_text=False,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=(
            tokenizer.pad_token_id
            if tokenizer.pad_token_id is not None
            else tokenizer.eos_token_id
        ),
    )

    hyde_llm = HuggingFacePipeline(pipeline=hyde_pipeline)
    print("  ✓ HyDE pipeline siap")
    return hyde_llm
