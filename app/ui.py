# ui.py
# Tanggung jawab tunggal: Membangun antarmuka pengguna (UI) Gradio
# dengan tema modern Tailwind CSS.

import gradio as gr
from custom_css import CUSTOM_CSS

# ============================================================
# HTML FRAGMENTS
# ============================================================
def hero_html():
    return """
    <div class="hero-header">
        <h1>⚖️ Asisten Hukum AI Indonesia</h1>
        <p class="hero-subtitle">
            RAG Pipeline — Retrieval-Augmented Generation untuk dokumen hukum Indonesia<br/>
            <span style="font-size:0.8rem; color:#64748b;">
                PP No. 35/2021 · PP No. 5/2021 · PP No. 51/2023 · UU No. 6/2023
            </span>
        </p>
    </div>
    """


def loading_html():
    return """
    <div class="card-panel fade-in" style="text-align:center; padding:2rem;">
        <div style="font-size:1.5rem; margin-bottom:0.75rem;">⚡</div>
        <div style="font-weight:600; color:#1e40af; margin-bottom:1rem;">
            Sedang menganalisis dokumen & menyusun penalaran...
        </div>
        <div style="max-width:300px; margin:0 auto;">
            <div class="skeleton-line" style="width:100%;"></div>
            <div class="skeleton-line" style="width:85%;"></div>
            <div class="skeleton-line" style="width:92%;"></div>
        </div>
    </div>
    """


def format_result_html(think_text: str, answer_text: str, elapsed: float) -> str:
    """Memformat hasil RAG menjadi HTML bergaya Tailwind."""

    think_section = ""
    if think_text:
        # Escape HTML characters in think text
        think_escaped = (
            think_text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        think_section = f"""
        <details class="think-box fade-in" open>
            <summary>🧠 Proses Penalaran (Chain-of-Thought)</summary>
            <div style="margin-top:0.75rem;">{think_escaped}</div>
        </details>
        """

    answer_escaped = (
        answer_text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

    answer_section = f"""
    <div class="answer-box fade-in">
        <div class="section-label">💬 Jawaban Akhir</div>
        <div>{answer_escaped}</div>
    </div>
    """

    timer_badge = f"""
    <div style="text-align:right;">
        <span class="status-badge">
            ⏱️ Selesai dalam {elapsed:.2f} detik
        </span>
    </div>
    """

    return f"""
    <div class="card-panel fade-in">
        {think_section}
        {answer_section}
        {timer_badge}
    </div>
    """


def empty_state_html():
    return """
    <div class="card-panel" style="text-align:center; padding:3rem 1.5rem; color:#94a3b8;">
        <div style="font-size:2.5rem; margin-bottom:0.75rem;">📜</div>
        <div style="font-weight:600; color:#64748b; margin-bottom:0.5rem;">
            Siap Membantu Anda
        </div>
        <div style="font-size:0.85rem;">
            Ketik pertanyaan tentang hukum ketenagakerjaan Indonesia<br/>
            atau pilih salah satu contoh di bawah.
        </div>
    </div>
    """


# ============================================================
# GRADIO INTERFACE BUILDER
# ============================================================
EXAMPLE_QUERIES = [
    "Apakah karyawan kontrak (PKWT) berhak mendapatkan uang kompensasi jika kontraknya berakhir?",
    "Apa isi bab 2 pasal 2 tahun 2023?",
    "Berapa lama waktu kerja lembur maksimal per hari?",
    "Bagaimana aturan cuti tahunan bagi pekerja?",
    "Apa saja hak pekerja yang di-PHK?",
]


def build_ui(rag_pipeline):
    """
    Membangun antarmuka Gradio yang terhubung ke RAGPipeline.

    Args:
        rag_pipeline: Instance dari RAGPipeline.

    Returns:
        gr.Blocks: Aplikasi Gradio.
    """

    def on_submit(query):
        """Handler saat user submit pertanyaan."""
        if not query or not query.strip():
            return empty_state_html()

        # Tampilkan loading (akan digantikan oleh result)
        yield loading_html()

        # Jalankan pipeline
        result = rag_pipeline.generate(query.strip())

        # Tampilkan hasil
        yield format_result_html(
            think_text=result["think"],
            answer_text=result["answer"],
            elapsed=result["elapsed_seconds"],
        )

    def on_example_click(example_text):
        """Handler saat user klik contoh pertanyaan."""
        return example_text

    # ---- Build the App ----
    with gr.Blocks(
        css=CUSTOM_CSS,
        title="Asisten Hukum AI Indonesia",
        theme=gr.themes.Soft(
            primary_hue=gr.themes.colors.blue,
            secondary_hue=gr.themes.colors.slate,
            neutral_hue=gr.themes.colors.slate,
            font=gr.themes.GoogleFont("Inter"),
        ),
    ) as app:

        # ---- Header ----
        gr.HTML(hero_html())

        # ---- Input Section ----
        with gr.Group(elem_classes=["card-panel"]):
            gr.HTML('<div class="section-label">📝 Pertanyaan Anda</div>')

            with gr.Row():
                query_input = gr.Textbox(
                    placeholder="Contoh: Apakah karyawan kontrak berhak dapat uang kompensasi?",
                    label="",
                    show_label=False,
                    lines=2,
                    max_lines=5,
                    scale=5,
                    container=False,
                )
                submit_btn = gr.Button(
                    "🔍 Tanya AI",
                    variant="primary",
                    scale=1,
                    min_width=120,
                )

            # ---- Example Queries ----
            gr.HTML('<div style="font-size:0.8rem; color:#64748b; font-weight:600; margin-top:0.75rem;">💡 Contoh pertanyaan:</div>')
            with gr.Row():
                example_btns = []
                for ex in EXAMPLE_QUERIES[:3]:
                    btn = gr.Button(
                        ex[:60] + ("..." if len(ex) > 60 else ""),
                        variant="secondary",
                        size="sm",
                        elem_classes=["example-chip"],
                    )
                    example_btns.append((btn, ex))
            with gr.Row():
                for ex in EXAMPLE_QUERIES[3:]:
                    btn = gr.Button(
                        ex[:60] + ("..." if len(ex) > 60 else ""),
                        variant="secondary",
                        size="sm",
                        elem_classes=["example-chip"],
                    )
                    example_btns.append((btn, ex))

        # ---- Output Section ----
        result_output = gr.HTML(value=empty_state_html())

        # ---- Footer ----
        gr.HTML("""
        <div class="app-footer">
            Dibuat dengan 🤖 LLM Fine-tuned + GRPO · Powered by LangChain RAG Pipeline<br/>
            Model: <code>hendrimardani/fine-tuned-model-indonesian-GRPO</code>
        </div>
        """)

        # ---- Event Bindings ----
        submit_btn.click(
            fn=on_submit,
            inputs=[query_input],
            outputs=[result_output],
        )

        query_input.submit(
            fn=on_submit,
            inputs=[query_input],
            outputs=[result_output],
        )

        for btn, full_text in example_btns:
            btn.click(
                fn=on_example_click,
                inputs=[gr.State(full_text)],
                outputs=[query_input],
            )

    return app
