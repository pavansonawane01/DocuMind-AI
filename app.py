import streamlit as st
import fitz
import os
import json
import hashlib
import sqlite3
import pandas as pd
import pytesseract

from pathlib import Path
from datetime import datetime
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
from google import genai


# =====================================================
# CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="DocuMind AI | Neural Workspace",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "documind.db"

load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

try:
    client = genai.Client(api_key=API_KEY) if API_KEY else None
except Exception:
    client = None

# Update this path if Tesseract is installed somewhere else.
TESSERACT_EXE = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if Path(TESSERACT_EXE).exists():
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_EXE


# =====================================================
# FUTURISTIC UI
# =====================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --bg: #070910;
    --panel: #111524;
    --panel-2: #171a2c;
    --text: #f4f5ff;
    --muted: #929ab6;
    --purple: #a78bfa;
    --cyan: #22d3ee;
    --border: rgba(139, 92, 246, .23);
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 85% 5%, rgba(104,48,190,.16), transparent 28%),
        radial-gradient(circle at 10% 45%, rgba(0,190,220,.08), transparent 25%),
        var(--bg);
    color: var(--text);
}

header[data-testid="stHeader"] { background: transparent; }
.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #101323, #090b14);
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * { color: #d9ddf0; }

.neural-logo {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 25px;
    font-weight: 700;
    letter-spacing: -1px;
    background: linear-gradient(90deg, #a78bfa, #22d3ee);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.neural-tag {
    color: #8189a8;
    font-size: 10px;
    letter-spacing: 3px;
    margin-top: 4px;
}

.hero {
    position: relative;
    overflow: hidden;
    padding: 48px 42px;
    min-height: 300px;
    border: 1px solid rgba(139,92,246,.34);
    border-radius: 25px;
    background: linear-gradient(115deg, rgba(24,20,48,.98), rgba(10,19,35,.96));
    box-shadow: 0 0 55px rgba(109,40,217,.13);
}
.hero-content { position: relative; z-index: 2; max-width: 680px; }
.eyebrow {
    color: #67e8f9;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 3px;
    margin-bottom: 22px;
}
.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(38px, 5vw, 65px);
    line-height: 1.08;
    font-weight: 700;
    letter-spacing: -3px;
    color: white;
}
.hero-gradient {
    background: linear-gradient(90deg, #a78bfa, #22d3ee, #e879f9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-description {
    color: #a6adc5;
    font-size: 15px;
    line-height: 1.8;
    max-width: 560px;
    margin-top: 18px;
}
.hero-status {
    display: inline-block;
    margin-top: 22px;
    padding: 9px 15px;
    border: 1px solid rgba(34,211,238,.35);
    border-radius: 30px;
    background: rgba(34,211,238,.07);
    color: #67e8f9;
    font-size: 11px;
    letter-spacing: 1px;
    font-weight: 700;
}
.hero-orb {
    position: absolute;
    width: 230px;
    height: 230px;
    right: 9%;
    top: 35px;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 35%, #a78bfa 0%, #6d28d9 22%, #164e91 55%, transparent 72%);
    filter: blur(9px);
    opacity: .8;
    box-shadow: 0 0 90px rgba(124,58,237,.45);
    animation: floatOrb 5s ease-in-out infinite;
}
@keyframes floatOrb {
    0%, 100% { transform: translateY(0) scale(1); }
    50% { transform: translateY(-16px) scale(1.05); }
}

.metric-card {
    background: linear-gradient(145deg, #171a2c, #101321);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 20px;
    min-height: 115px;
}
.metric-label { color: #929ab6; font-size: 11px; letter-spacing: 1px; }
.metric-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 30px;
    font-weight: 700;
    color: #f8faff;
    margin-top: 8px;
}
.section-heading {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: #f4f5ff;
    margin: 10px 0 6px;
}
.section-sub { color: #8992ae; font-size: 13px; margin-bottom: 18px; }
.section-card {
    background: #111524;
    border: 1px solid rgba(139,92,246,.18);
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 18px;
}
.feature-card {
    background: linear-gradient(145deg, rgba(23,26,44,.96), rgba(14,18,32,.96));
    border: 1px solid rgba(139,92,246,.22);
    border-radius: 18px;
    padding: 22px;
    min-height: 160px;
}
.feature-icon { font-size: 24px; margin-bottom: 12px; }
.feature-title { font-weight: 700; font-size: 16px; color: #f4f5ff; margin-bottom: 8px; }
.feature-copy { color: #929ab6; font-size: 13px; line-height: 1.65; }

div[data-testid="stFileUploader"] {
    background: rgba(19,24,43,.8);
    border: 1px dashed rgba(34,211,238,.42);
    border-radius: 16px;
    padding: 15px;
}
.stButton > button, .stDownloadButton > button {
    border: 1px solid rgba(139,92,246,.45);
    border-radius: 10px;
    background: linear-gradient(100deg, #652cc5, #164c83);
    color: white;
    font-weight: 700;
    transition: .2s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    border-color: #22d3ee;
    box-shadow: 0 0 22px rgba(34,211,238,.25);
    transform: translateY(-1px);
    color: white;
}
.stTextInput input, .stTextArea textarea {
    background: #101525 !important;
    color: #f4f5ff !important;
    border: 1px solid rgba(139,92,246,.30) !important;
    border-radius: 10px !important;
}
.stSelectbox div[data-baseweb="select"] { background: #101525; }
.stTabs [data-baseweb="tab-list"] {
    gap: 12px;
    border-bottom: 1px solid rgba(139,92,246,.2);
}
.stTabs [data-baseweb="tab"] { color: #a5acc4; font-weight: 600; }
.stTabs [aria-selected="true"] {
    color: #67e8f9 !important;
    border-bottom-color: #22d3ee !important;
}
div[data-testid="stExpander"] {
    background: #111524;
    border: 1px solid rgba(139,92,246,.2);
    border-radius: 12px;
}
hr { border-color: rgba(139,92,246,.18); }
small, .muted { color: #8992ae; }

@media (max-width: 800px) {
    .hero { padding: 32px 24px; }
    .hero-orb { right: -70px; opacity: .35; }
    .hero-title { letter-spacing: -1.5px; }
}
</style>
""", unsafe_allow_html=True)


# =====================================================
# DATABASE
# =====================================================

def get_connection():
    return sqlite3.connect(DB_PATH, timeout=30)


def init_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                file_type TEXT,
                upload_date TEXT,
                page_count INTEGER,
                ocr_pages INTEGER,
                summary TEXT,
                important_info TEXT,
                doc_hash TEXT UNIQUE
            )
        """)


def save_document(record):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO documents
            (filename, file_type, upload_date, page_count, ocr_pages,
             summary, important_info, doc_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(doc_hash) DO UPDATE SET
                filename=excluded.filename,
                file_type=excluded.file_type,
                page_count=excluded.page_count,
                ocr_pages=excluded.ocr_pages,
                summary=CASE
                    WHEN excluded.summary != '' THEN excluded.summary
                    ELSE documents.summary
                END,
                important_info=CASE
                    WHEN excluded.important_info != '' THEN excluded.important_info
                    ELSE documents.important_info
                END
        """, (
            record["filename"], record["file_type"], record["upload_date"],
            record["page_count"], record["ocr_pages"], record["summary"],
            record["important_info"], record["doc_hash"]
        ))


def get_all_documents():
    with get_connection() as conn:
        return pd.read_sql_query(
            "SELECT * FROM documents ORDER BY id DESC", conn
        )


init_database()


# =====================================================
# DOCUMENT EXTRACTION
# =====================================================

def calculate_hash(data):
    return hashlib.sha256(data).hexdigest()


def run_ocr(image):
    """Try English + Hindi OCR, then fall back to English."""
    try:
        return pytesseract.image_to_string(image, lang="eng+hin")
    except Exception:
        return pytesseract.image_to_string(image, lang="eng")


def extract_pdf(file_bytes):
    pdf = fitz.open(stream=file_bytes, filetype="pdf")
    extracted_text = []
    ocr_pages = 0

    try:
        for page_number, page in enumerate(pdf, start=1):
            text = page.get_text("text").strip()

            if len(text) < 20:
                try:
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                    image = Image.frombytes(
                        "RGB", [pix.width, pix.height], pix.samples
                    )
                    text = run_ocr(image).strip()
                    ocr_pages += 1
                except Exception as error:
                    text = f"[OCR could not process page {page_number}: {error}]"

            extracted_text.append(text)
    finally:
        page_count = len(pdf)
        pdf.close()

    return "\n\n".join(extracted_text), page_count, ocr_pages


def extract_image(file_bytes):
    image = Image.open(BytesIO(file_bytes)).convert("RGB")
    text = run_ocr(image)
    return text, 1, 1


# =====================================================
# GEMINI AI
# =====================================================

def ask_gemini(prompt):
    if client is None:
        return (
            "Gemini API is not connected. Check that GEMINI_API_KEY is set "
            "correctly in your .env file, then restart the app."
        )

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        return response.text or "AI did not return a response."
    except Exception as error:
        return f"AI Error: {error}"


def generate_summary(document_text):
    prompt = f"""
You are DocuMind AI, an expert document intelligence assistant.
Analyze the document and create a clear, accurate summary.

Use these sections:
1. Document Overview
2. Main Points
3. Important Details
4. Key Conclusions
5. Actionable Insights

Do not invent information. Clearly state when information is absent.

DOCUMENT:
{document_text[:25000]}
"""
    return ask_gemini(prompt)


def extract_important_info(document_text):
    prompt = f"""
You are DocuMind AI. Extract information actually present in the document.
Do not guess or invent anything.

Organize the result under:
- Important Names
- Dates and Deadlines
- Amounts and Numbers
- Important Terms
- Key Requirements
- Important Contact Details
- Critical Notes

DOCUMENT:
{document_text[:25000]}
"""
    return ask_gemini(prompt)


def chat_with_document(document_text, question):
    prompt = f"""
You are DocuMind AI. Answer using ONLY the document below.

Rules:
- Be accurate and specific.
- If the answer is not present, say so clearly.
- Do not invent facts.
- Keep the answer easy to understand.

DOCUMENT:
{document_text[:25000]}

USER QUESTION:
{question}
"""
    return ask_gemini(prompt)


# =====================================================
# SESSION STATE
# =====================================================

DEFAULT_STATE = {
    "document_text": "",
    "document_name": "",
    "file_type": "",
    "summary": "",
    "important_info": "",
    "chat_history": [],
    "page_count": 0,
    "ocr_pages": 0,
    "doc_hash": ""
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =====================================================
# REUSABLE UI HELPERS
# =====================================================

def show_hero():
    hero_html = """
    <div class="hero">
        <div class="hero-content">
            <div class="eyebrow">◈ NEXT GENERATION DOCUMENT INTELLIGENCE</div>
            <div class="hero-title">
                Think beyond<br>
                <span class="hero-gradient">the document.</span>
            </div>
            <div class="hero-description">
                An intelligent workspace that transforms complex
                documents into knowledge, insights and decisions.
            </div>
            <div class="hero-status">✦ INTELLIGENCE ENGINE ONLINE</div>
        </div>
        <div class="hero-orb"></div>
    </div>
    """
    # Keep the HTML in one string and explicitly enable HTML rendering.
    st.markdown(hero_html, unsafe_allow_html=True)


def metric_card(label, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def section_heading(title, subtitle=None):
    st.markdown(
        f'<div class="section-heading">{title}</div>',
        unsafe_allow_html=True
    )
    if subtitle:
        st.markdown(
            f'<div class="section-sub">{subtitle}</div>',
            unsafe_allow_html=True
        )


def make_record():
    return {
        "filename": st.session_state.document_name,
        "file_type": st.session_state.file_type,
        "upload_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "page_count": st.session_state.page_count,
        "ocr_pages": st.session_state.ocr_pages,
        "summary": st.session_state.summary,
        "important_info": st.session_state.important_info,
        "doc_hash": st.session_state.doc_hash
    }


# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:
    st.markdown("""
    <div style="padding:10px 5px 25px 5px;">
        <div class="neural-logo">◈ DocuMind AI</div>
        <div class="neural-tag">NEURAL WORKSPACE</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    page = st.radio(
        "NAVIGATION",
        [
            "Dashboard",
            "Document Analyzer",
            "Chat with Document",
            "History & Analytics",
            "About"
        ],
        label_visibility="visible"
    )

    st.markdown("---")
    st.markdown("<div class='muted'>✦ AI ENGINE STATUS</div>",
                unsafe_allow_html=True)

    if client:
        st.success("AI Engine Connected")
    else:
        st.error("API Key Missing")

    st.markdown("""
    <div class="muted">
        Powered by Gemini AI<br>
        OCR: Tesseract<br>
        Storage: SQLite
    </div>
    """, unsafe_allow_html=True)


# =====================================================
# DASHBOARD
# =====================================================

if page == "Dashboard":
    show_hero()
    st.write("")
    section_heading("Your Intelligence Overview")

    df = get_all_documents()
    total_docs = len(df)
    total_pages = int(df["page_count"].fillna(0).sum()) if not df.empty else 0
    total_ocr = int(df["ocr_pages"].fillna(0).sum()) if not df.empty else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("DOCUMENTS ANALYZED", total_docs)
    with col2:
        metric_card("TOTAL PAGES PROCESSED", total_pages)
    with col3:
        metric_card("OCR PAGES PROCESSED", total_ocr)

    st.write("")
    section_heading("Workspace Tools", "Everything you need to turn documents into useful intelligence.")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">◈</div>
            <div class="feature-title">Document Intelligence</div>
            <div class="feature-copy">
                Upload PDFs and images, extract text, generate AI summaries
                and identify important information.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">✦</div>
            <div class="feature-title">Neural Document Chat</div>
            <div class="feature-copy">
                Ask questions about your uploaded document and receive
                context-aware answers powered by Gemini AI.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    if not df.empty:
        section_heading("Recent Documents")
        st.dataframe(
            df[["filename", "file_type", "upload_date", "page_count"]].head(5),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No documents analyzed yet. Open Document Analyzer to begin.")


# =====================================================
# DOCUMENT ANALYZER
# =====================================================

elif page == "Document Analyzer":
    show_hero()
    st.write("")
    section_heading(
        "Document Intelligence Lab",
        "Upload a document and let AI turn it into structured knowledge."
    )

    uploaded_file = st.file_uploader(
        "Upload your document",
        type=["pdf", "png", "jpg", "jpeg"],
        help="Supported formats: PDF, PNG, JPG, JPEG",
        key="document_uploader"
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        file_hash = calculate_hash(file_bytes)

        if st.session_state.doc_hash != file_hash:
            with st.spinner("Extracting document content..."):
                try:
                    extension = Path(uploaded_file.name).suffix.lower()

                    if extension == ".pdf":
                        extracted, pages, ocr_count = extract_pdf(file_bytes)
                        detected_type = "PDF"
                    else:
                        extracted, pages, ocr_count = extract_image(file_bytes)
                        detected_type = "Image"

                    st.session_state.document_text = extracted
                    st.session_state.document_name = uploaded_file.name
                    st.session_state.file_type = detected_type
                    st.session_state.page_count = pages
                    st.session_state.ocr_pages = ocr_count
                    st.session_state.doc_hash = file_hash
                    st.session_state.summary = ""
                    st.session_state.important_info = ""
                    st.session_state.chat_history = []

                except Exception as error:
                    st.error(f"Document extraction failed: {error}")

        if st.session_state.document_text:
            st.success(f"Document ready: {st.session_state.document_name}")

            a, b, c = st.columns(3)
            with a:
                metric_card("PAGES", st.session_state.page_count)
            with b:
                metric_card("OCR PAGES", st.session_state.ocr_pages)
            with c:
                metric_card("CHARACTERS", f"{len(st.session_state.document_text):,}")

            st.write("")
            tab1, tab2, tab3 = st.tabs([
                "✦ AI Summary",
                "◈ Important Information",
                "▤ Extracted Text"
            ])

            with tab1:
                st.markdown("### AI Document Summary")
                if st.button("Generate AI Summary", key="summary_btn",
                             use_container_width=False):
                    with st.spinner("AI is analyzing your document..."):
                        st.session_state.summary = generate_summary(
                            st.session_state.document_text
                        )
                        save_document(make_record())

                if st.session_state.summary:
                    st.markdown('<div class="section-card">', unsafe_allow_html=True)
                    st.markdown(st.session_state.summary)
                    st.markdown("</div>", unsafe_allow_html=True)
                    st.download_button(
                        "Download Summary",
                        data=st.session_state.summary,
                        file_name="documind_summary.txt",
                        mime="text/plain"
                    )

            with tab2:
                st.markdown("### Important Information Extraction")
                if st.button("Extract Important Information", key="important_btn"):
                    with st.spinner("Identifying important information..."):
                        st.session_state.important_info = extract_important_info(
                            st.session_state.document_text
                        )
                        save_document(make_record())

                if st.session_state.important_info:
                    st.markdown('<div class="section-card">', unsafe_allow_html=True)
                    st.markdown(st.session_state.important_info)
                    st.markdown("</div>", unsafe_allow_html=True)
                    st.download_button(
                        "Download Important Information",
                        data=st.session_state.important_info,
                        file_name="important_information.txt",
                        mime="text/plain"
                    )

            with tab3:
                st.markdown("### Extracted Document Text")
                st.text_area(
                    "Extracted content",
                    value=st.session_state.document_text,
                    height=350,
                    key="extracted_text_view"
                )
                st.download_button(
                    "Download Extracted Text",
                    data=st.session_state.document_text,
                    file_name="extracted_text.txt",
                    mime="text/plain"
                )
                json_data = json.dumps(
                    {
                        "filename": st.session_state.document_name,
                        "text": st.session_state.document_text
                    },
                    ensure_ascii=False,
                    indent=4
                )
                st.download_button(
                    "Download Extracted Text as JSON",
                    data=json_data,
                    file_name="extracted_document.json",
                    mime="application/json"
                )
    else:
        st.info("Upload a PDF or image to start document analysis.")


# =====================================================
# CHAT WITH DOCUMENT
# =====================================================

elif page == "Chat with Document":
    show_hero()
    st.write("")
    section_heading("Neural Document Chat")

    if not st.session_state.document_text:
        st.warning("First upload a document in Document Analyzer.")
    else:
        st.success(f"Active document: {st.session_state.document_name}")
        st.markdown("""
        <div class="section-card">
            <div class="section-heading">Ask your document anything</div>
            <div class="section-sub">
                Your AI assistant answers using the uploaded document.
            </div>
        </div>
        """, unsafe_allow_html=True)

        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        question = st.chat_input("Ask a question about your document...")
        if question:
            st.session_state.chat_history.append({
                "role": "user", "content": question
            })
            with st.chat_message("user"):
                st.markdown(question)

            with st.chat_message("assistant"):
                with st.spinner("Analyzing your document..."):
                    answer = chat_with_document(
                        st.session_state.document_text, question
                    )
                st.markdown(answer)

            st.session_state.chat_history.append({
                "role": "assistant", "content": answer
            })

        if st.button("Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()


# =====================================================
# HISTORY & ANALYTICS
# =====================================================

elif page == "History & Analytics":
    show_hero()
    st.write("")
    section_heading("Document History & Analytics")

    df = get_all_documents()
    if df.empty:
        st.info("No document history available yet.")
    else:
        total_docs = len(df)
        total_pages = int(df["page_count"].fillna(0).sum())
        total_ocr = int(df["ocr_pages"].fillna(0).sum())

        c1, c2, c3 = st.columns(3)
        with c1:
            metric_card("TOTAL DOCUMENTS", total_docs)
        with c2:
            metric_card("PAGES PROCESSED", total_pages)
        with c3:
            metric_card("OCR PAGES", total_ocr)

        st.write("")
        section_heading("Document Processing Overview")
        chart_data = pd.DataFrame({
            "Metric": ["Documents", "Pages", "OCR Pages"],
            "Count": [total_docs, total_pages, total_ocr]
        })
        st.bar_chart(chart_data.set_index("Metric"), use_container_width=True)

        section_heading("Complete Document History")
        st.dataframe(
            df[["filename", "file_type", "upload_date", "page_count", "ocr_pages"]],
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Export History as CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="documind_history.csv",
            mime="text/csv"
        )
        st.download_button(
            "Export History as JSON",
            data=df.to_json(orient="records", indent=4, force_ascii=False),
            file_name="documind_history.json",
            mime="application/json"
        )

        with st.expander("View Saved Document Details"):
            for _, row in df.iterrows():
                st.markdown(f"**{row['filename']}**")
                st.caption(f"Uploaded: {row['upload_date']}")
                if row["summary"]:
                    st.markdown("**Summary**")
                    st.write(row["summary"])
                if row["important_info"]:
                    st.markdown("**Important Information**")
                    st.write(row["important_info"])
                st.divider()


# =====================================================
# ABOUT
# =====================================================

elif page == "About":
    show_hero()
    st.write("")
    section_heading("About DocuMind AI")

    st.markdown("""
    <div class="section-card">
        <div class="section-heading">◈ What is DocuMind AI?</div>
        <div class="section-sub" style="line-height:1.8">
            DocuMind AI is an intelligent document analysis platform designed
            to transform static documents into useful knowledge. It combines
            artificial intelligence, OCR technology and persistent document
            storage in one workspace.
        </div>
    </div>
    """, unsafe_allow_html=True)

    section_heading("Technology Stack")
    tech = [
        ("Python", "Core application language"),
        ("Streamlit", "Interactive user interface"),
        ("Gemini AI", "AI-powered document intelligence"),
        ("PyMuPDF", "PDF text extraction"),
        ("Tesseract OCR", "Image and scanned PDF recognition"),
        ("SQLite", "Persistent document history")
    ]

    for start in (0, 3):
        cols = st.columns(3)
        for col, item in zip(cols, tech[start:start + 3]):
            with col:
                st.markdown(
                    f"""
                    <div class="feature-card">
                        <div class="feature-title">{item[0]}</div>
                        <div class="feature-copy">{item[1]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    st.write("")
    st.markdown("""
    <div class="section-card">
        <div class="section-heading">Built for intelligent work.</div>
        <div class="section-sub">DocuMind AI — Neural Workspace</div>
    </div>
    """, unsafe_allow_html=True)


# =====================================================
# FOOTER
# =====================================================

st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#707993;font-size:12px;padding:12px;">
    ◈ DOCUMIND AI &nbsp; | &nbsp; NEURAL WORKSPACE
    <br><br>
    Transforming documents into intelligence.
</div>
""", unsafe_allow_html=True)



