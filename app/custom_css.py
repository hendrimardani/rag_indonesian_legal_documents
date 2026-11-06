CUSTOM_CSS = """
/* ---- Base Reset & Font ---- */
* { box-sizing: border-box; }

.gradio-container {
    max-width: 960px !important;
    margin: 0 auto !important;
    font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif !important;
}

/* ---- Hero Header ---- */
.hero-header {
    text-align: center;
    padding: 2rem 1rem 1.5rem;
    background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%);
    border-radius: 1rem;
    margin-bottom: 1.5rem;
    border: 1px solid #1e40af;
    position: relative;
    overflow: hidden;
}
.hero-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(59,130,246,0.08) 0%, transparent 70%);
    animation: pulse-glow 4s ease-in-out infinite;
}
@keyframes pulse-glow {
    0%, 100% { opacity: 0.5; transform: scale(1); }
    50% { opacity: 1; transform: scale(1.05); }
}
.hero-header h1 {
    font-size: 1.75rem;
    font-weight: 800;
    color: #f8fafc;
    margin: 0 0 0.5rem;
    position: relative;
    letter-spacing: -0.025em;
}
.hero-subtitle {
    color: #94a3b8;
    font-size: 0.9rem;
    margin: 0;
    position: relative;
}

/* ---- Card Panels ---- */
.card-panel {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 0.75rem;
    padding: 1.25rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    transition: box-shadow 0.2s ease;
}
.card-panel:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

/* ---- Section Label ---- */
.section-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.85rem;
    font-weight: 700;
    color: #334155;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #e2e8f0;
}

/* ---- Think Box (Collapsible) ---- */
.think-box {
    background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
    border: 1px solid #fbbf24;
    border-left: 4px solid #f59e0b;
    border-radius: 0.5rem;
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
    font-size: 0.9rem;
    color: #78350f;
    line-height: 1.7;
    white-space: pre-wrap;
    word-wrap: break-word;
}
.think-box summary {
    cursor: pointer;
    font-weight: 700;
    font-size: 0.9rem;
    color: #92400e;
    padding: 0.25rem 0;
    user-select: none;
}
.think-box summary:hover {
    color: #78350f;
}

/* ---- Answer Box ---- */
.answer-box {
    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
    border: 1px solid #86efac;
    border-left: 4px solid #22c55e;
    border-radius: 0.5rem;
    padding: 1.25rem;
    font-size: 0.95rem;
    color: #14532d;
    line-height: 1.8;
    white-space: pre-wrap;
    word-wrap: break-word;
}

/* ---- Status / Timer Badge ---- */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    background: #eff6ff;
    color: #1d4ed8;
    font-size: 0.8rem;
    font-weight: 600;
    padding: 0.35rem 0.75rem;
    border-radius: 9999px;
    border: 1px solid #bfdbfe;
    margin-top: 0.75rem;
}

/* ---- Gradio Component Overrides ---- */
.gr-button-primary {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    border-radius: 0.5rem !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 1px 3px rgba(37,99,235,0.3) !important;
}
.gr-button-primary:hover {
    background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%) !important;
    box-shadow: 0 4px 12px rgba(37,99,235,0.4) !important;
    transform: translateY(-1px) !important;
}
.gr-button-secondary {
    background: #f8fafc !important;
    border: 1px solid #cbd5e1 !important;
    color: #475569 !important;
    font-weight: 500 !important;
    border-radius: 0.5rem !important;
}

/* ---- Document Info Pills ---- */
.doc-info {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 1rem;
}
.doc-pill {
    background: #f1f5f9;
    color: #475569;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 500;
    border: 1px solid #e2e8f0;
}

/* ---- Footer ---- */
.app-footer {
    text-align: center;
    padding: 1rem;
    color: #94a3b8;
    font-size: 0.75rem;
    border-top: 1px solid #e2e8f0;
    margin-top: 1.5rem;
}

/* ---- Responsive ---- */
@media (max-width: 640px) {
    .hero-header h1 { font-size: 1.35rem; }
    .gradio-container { padding: 0.5rem !important; }
}

/* ---- Animations ---- */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}
.fade-in {
    animation: fadeIn 0.3s ease-out;
}

/* ---- Loading Skeleton ---- */
.skeleton-line {
    height: 0.75rem;
    background: linear-gradient(90deg, #e2e8f0 25%, #f1f5f9 50%, #e2e8f0 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 0.25rem;
    margin-bottom: 0.5rem;
}
@keyframes shimmer {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

/* ---- Example Chips ---- */
.example-chip {
    cursor: pointer;
    transition: all 0.15s ease;
}
.example-chip:hover {
    background: #dbeafe !important;
    border-color: #93c5fd !important;
}

/* Dark mode support */
.dark .card-panel {
    background: #1e293b;
    border-color: #334155;
}
.dark .think-box {
    background: linear-gradient(135deg, #422006 0%, #451a03 100%);
    border-color: #b45309;
    color: #fef3c7;
}
.dark .answer-box {
    background: linear-gradient(135deg, #052e16 0%, #064e3b 100%);
    border-color: #16a34a;
    color: #dcfce7;
}
"""