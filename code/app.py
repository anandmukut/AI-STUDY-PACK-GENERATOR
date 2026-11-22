"""
AI-Powered Study Pack Generator Using Prompt Engineering
=======================================================
A Streamlit web application that converts lecture notes or uploaded PDF documents
into structured study packs (Summary, Key Terms & Definitions, Practice Q&A)
using a sequential 3-step prompt chain powered by Google Gemini.
"""

import os
import re
from datetime import datetime
from io import BytesIO
from typing import Tuple

import streamlit as st
from dotenv import load_dotenv
import pypdf
from google import genai
from google.genai import types

# Load environment variables (e.g., from .env if present)
load_dotenv()

# --- Prompt Chain Definitions & System Prompts ---

PROMPT_1_SUMMARY = """
You are an expert academic tutor and concise summarizer specializing in higher education materials.

INPUT LECTURE NOTES:
\"\"\"
{lecture_notes}
\"\"\"

TASK:
Generate a comprehensive, clear, and bulleted executive summary of these lecture notes.

STRICT GROUNDING RULES:
1. Base your summary STRICTLY and EXCLUSIVELY on the provided lecture notes.
2. Do NOT extrapolate, hallucinate, or incorporate outside knowledge not present in the text.
3. Organize the summary logically with thematic section headings (using Markdown ## and ###) followed by concise, impactful bullet points.
4. Highlight central concepts, methodologies, core arguments, and experimental or theoretical conclusions explicitly described.
"""

PROMPT_2_KEY_TERMS = """
You are an expert academic curriculum designer and terminology specialist.

INPUT LECTURE NOTES:
\"\"\"
{lecture_notes}
\"\"\"

GENERATED SUMMARY:
\"\"\"
{summary}
\"\"\"

TASK:
Extract all crucial domain-specific terms, technical definitions, formulas, acronyms, and foundational principles from the lecture notes.

STRICT GROUNDING RULES:
1. Ground every term and definition STRICTLY in the provided lecture notes and summary.
2. If a term is mentioned in the notes but its full definition is not elaborated, define it strictly within the scope given in the notes. Do NOT invent external definitions.
3. Format as a clean, structured Markdown list with bolded terms followed by clear definitions:
   - **[Term/Concept Name]**: [Definition and context grounded in notes]
4. Order the terms logically from fundamental concepts to advanced or specialized topics.
"""

PROMPT_3_PRACTICE_QA = """
You are an expert university examiner creating rigorous assessment materials.

INPUT LECTURE NOTES:
\"\"\"
{lecture_notes}
\"\"\"

KEY TERMS & DEFINITIONS:
\"\"\"
{key_terms}
\"\"\"

TASK:
Generate exactly 5 exam-style practice questions with complete, detailed answer keys grounded in the provided notes.

STRICT GROUNDING RULES:
1. Every question and answer must be directly answerable from the provided lecture notes and key terms.
2. Include a balanced mix:
   - 2 Conceptual/Definition questions
   - 2 Applied scenario or analytical questions
   - 1 Synthesis or evaluation question
3. SPECIAL REQUIREMENT: If any concept or detail in the question is not explicitly provided in the notes, state explicitly: "Not provided in notes."
4. Structure each question cleanly in the following Markdown format:

### Question 1: [Question text]
- **Question Type**: [Conceptual / Applied / Analytical / Synthesis]
- **Model Answer**: [Comprehensive answer directly from the notes]
- **Grounding & Explanation**: [Reference to where in the lecture notes or key terms this is derived]

(Repeat format for Questions 2 through 5)
"""


# --- Helper Functions ---

def extract_text_from_pdf(uploaded_file) -> str:
    """Extract clean text content across all pages from an uploaded PDF."""
    try:
        reader = pypdf.PdfReader(uploaded_file)
        pages_text = []
        for idx, page in enumerate(reader.pages):
            page_content = page.extract_text()
            if page_content and page_content.strip():
                pages_text.append(f"--- Page {idx + 1} ---\n{page_content.strip()}")
        return "\n\n".join(pages_text)
    except Exception as exc:
        st.error(f"Failed to parse PDF document: {exc}")
        return ""


def validate_academic_notes(text: str) -> Tuple[bool, str]:
    """
    Validates that the provided notes are:
    1. Not empty or purely whitespace.
    2. At least 30 characters long.
    3. Not gibberish, keyboard spam, or non-academic noise.
    """
    if not text:
        return False, "Input is empty. Please upload a PDF with readable text or paste your lecture notes."

    cleaned = text.strip()
    if len(cleaned) < 30:
        return False, f"The input is too short ({len(cleaned)} characters). Minimum 30 characters required."

    # Extract alphanumeric words
    words = re.findall(r"\b[A-Za-z0-9'-]+\b", cleaned)
    if len(words) < 5:
        return False, f"The input contains only {len(words)} word(s). Please provide complete notes or sentences."

    # Check ratio of alphabetic characters to detect symbol floods or unreadable binary/OCR junk
    alpha_chars = sum(1 for c in cleaned if c.isalpha())
    alpha_ratio = alpha_chars / len(cleaned)
    if alpha_ratio < 0.40:
        return (
            False,
            "The input has an abnormally low ratio of text/letters (contains mostly symbols, digits, or noise)."
        )

    # Check for repetitive single-character or low-entropy spam (e.g. 'aaaaaaaaaa' or 'asdfasdf')
    unique_chars = len(set(cleaned.lower()))
    if unique_chars < 6:
        return False, "The input appears to be repetitive keystrokes or noise rather than academic lecture material."

    # Check average word length to detect unspaced character walls (e.g. 'abcdefghijklmnopqrstuvwxyz...')
    avg_word_length = sum(len(w) for w in words) / max(len(words), 1)
    if avg_word_length > 25:
        return False, "The input contains unnaturally long tokens without spaces, indicating random noise or raw data."
    if avg_word_length < 1.8:
        return False, "The input consists mostly of disjointed 1- or 2-letter fragments."

    return True, ""


def execute_prompt_chain(
    api_key: str,
    model_name: str,
    temperature: float,
    lecture_notes: str,
    status_callback=None
) -> Tuple[str, str, str]:
    """
    Executes the 3-step sequential Prompt Chain using Google GenAI SDK:
      P1: Summary Generator
      P2: Key Terms & Definitions Extractor (conditioned on notes + P1 output)
      P3: Practice Q&A Generator (conditioned on notes + P2 output)
    """
    client = genai.Client(api_key=api_key)
    gen_config = types.GenerateContentConfig(
        temperature=temperature,
    )

    # Step 1: Summary Generator (P1)
    if status_callback:
        status_callback("P1", "Generating concise, strictly-grounded executive summary...")
    prompt_1 = PROMPT_1_SUMMARY.format(lecture_notes=lecture_notes)
    response_1 = client.models.generate_content(
        model=model_name,
        contents=prompt_1,
        config=gen_config
    )
    summary_output = response_1.text or ""

    # Step 2: Key Terms & Definitions Extractor (P2 conditioned on notes + P1 output)
    if status_callback:
        status_callback("P2", "Extracting domain-specific key terms & definitions...")
    prompt_2 = PROMPT_2_KEY_TERMS.format(
        lecture_notes=lecture_notes,
        summary=summary_output
    )
    response_2 = client.models.generate_content(
        model=model_name,
        contents=prompt_2,
        config=gen_config
    )
    key_terms_output = response_2.text or ""

    # Step 3: Practice Q&A Generator (P3 conditioned on notes + P2 output)
    if status_callback:
        status_callback("P3", "Generating 5 exam-style practice questions with answer key...")
    prompt_3 = PROMPT_3_PRACTICE_QA.format(
        lecture_notes=lecture_notes,
        key_terms=key_terms_output
    )
    response_3 = client.models.generate_content(
        model=model_name,
        contents=prompt_3,
        config=gen_config
    )
    practice_qa_output = response_3.text or ""

    return summary_output, key_terms_output, practice_qa_output


def compile_study_pack_markdown(
    summary: str,
    key_terms: str,
    practice_qa: str,
    model_name: str
) -> str:
    """Compiles all 3 chain outputs into a polished Markdown document."""
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""# 📚 AI-Generated Study Pack
*Generated via 3-Stage Prompt Engineering Chain using `{model_name}`*  
*Date: {timestamp_str}*

---

## 📝 1. Grounded Executive Summary
{summary}

---

## 🔑 2. Key Terms & Definitions
{key_terms}

---

## ❓ 3. Exam Practice Questions & Solutions
{practice_qa}

---
*Generated by AI Study Pack Generator | Powered by Google GenAI*
"""


# --- Main Streamlit Application UI ---

def main():
    # Page Configuration
    st.set_page_config(
        page_title="AI-Powered Study Pack Generator",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Modern Custom Styling
    st.markdown(
        """
        <style>
        .main .block-container {
            padding-top: 1.8rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }
        .hero-header {
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #06b6d4 100%);
            padding: 1.8rem 2rem;
            border-radius: 14px;
            color: white;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08);
        }
        .hero-title {
            font-size: 2.1rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            margin: 0;
            color: #ffffff;
        }
        .hero-subtitle {
            font-size: 1.05rem;
            font-weight: 400;
            color: #e0f2fe;
            margin-top: 0.4rem;
            margin-bottom: 0.8rem;
        }
        .badge-tag {
            display: inline-block;
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(4px);
            color: #ffffff;
            font-size: 0.78rem;
            font-weight: 600;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            margin-right: 0.5rem;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Session State Initialization
    if "study_pack" not in st.session_state:
        st.session_state["study_pack"] = {
            "summary": None,
            "key_terms": None,
            "practice_qa": None,
            "timestamp": None,
            "model_used": None,
        }

    # ==========================================
    # --- SIDEBAR: Controls & Settings ---
    # ==========================================
    with st.sidebar:
        st.image(
            "https://api.iconify.design/fluent-emoji:books.svg",
            width=54
        )
        st.title("Study Pack Settings")
        st.markdown("Configure your Gemini model credentials and inference parameters.")

        # API Key Input
        env_api_key = os.getenv("GEMINI_API_KEY", "")
        api_key = st.text_input(
            "Gemini API Key",
            value=env_api_key,
            type="password",
            help="Enter your Google Gemini API key. Get one from https://aistudio.google.com/"
        )

        if not api_key:
            st.warning("⚠️ **API Key Required**: Please enter your Gemini API Key above to run the generator.")
            st.caption("You can get a free key at [Google AI Studio](https://aistudio.google.com/).")

        st.markdown("---")
        st.subheader("🤖 Model Configuration")

        model_options = [
            "gemini-2.5-flash",
            "gemini-2.5-pro",
            "gemini-2.0-flash",
            "gemini-1.5-flash",
            "gemini-1.5-pro"
        ]
        selected_model = st.selectbox(
            "Model Selector",
            options=model_options,
            index=0,  # Default: gemini-2.5-flash
            help="Select the Gemini model variant for study pack generation."
        )

        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.2,  # Default: 0.2
            step=0.05,
            help="Lower values (0.1 - 0.3) ensure grounded, deterministic, strictly factual academic outputs."
        )

        st.markdown("---")
        st.markdown(
            """
            <div style="font-size: 0.8rem; color: gray;">
            <b>Prompt Chain Architecture:</b><br/>
            • <b>P1</b>: Grounded Summary<br/>
            • <b>P2</b>: Terms & Definitions (conditioned on P1)<br/>
            • <b>P3</b>: 5 Exam Q&As (conditioned on P2)
            </div>
            """,
            unsafe_allow_html=True
        )

    # ==========================================
    # --- MAIN CONTENT AREA ---
    # ==========================================

    # Hero Banner
    st.markdown(
        """
        <div class="hero-header">
            <h1 class="hero-title">AI-Powered Study Pack Generator</h1>
            <p class="hero-subtitle">Transform unstructured lecture notes and textbooks into comprehensive, grounded study packs using Prompt Chaining.</p>
            <div>
                <span class="badge-tag">🔗 3-Step Prompt Chain</span>
                <span class="badge-tag">🎯 Strict Grounding</span>
                <span class="badge-tag">⚡ Gemini 2.5 Flash</span>
                <span class="badge-tag">📑 PDF / Text Support</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # API Key Instruction Banner if missing
    if not api_key:
        st.info(
            "👋 **Welcome!** To get started, please provide your **Gemini API Key** in the sidebar on the left. "
            "Once entered, you can upload a PDF or paste lecture notes below to generate your study pack."
        )

    # Input Section: PDF or Paste Notes
    st.subheader("📥 Input Material")

    input_tab = st.radio(
        "Select Input Method:",
        options=["📄 Upload PDF File", "✍️ Paste Raw Lecture Notes"],
        horizontal=True
    )

    lecture_notes_text = ""

    if input_tab == "📄 Upload PDF File":
        uploaded_pdf = st.file_uploader(
            "Upload your lecture notes or slides (PDF format)",
            type=["pdf"],
            help="Upload an academic PDF file. Text will be automatically extracted across all pages."
        )
        if uploaded_pdf is not None:
            with st.spinner("Extracting text from PDF pages..."):
                lecture_notes_text = extract_text_from_pdf(uploaded_pdf)
                if lecture_notes_text:
                    st.success(f"Successfully extracted text ({len(lecture_notes_text):,} characters) from `{uploaded_pdf.name}`.")
                    with st.expander("👁️ Preview Extracted PDF Text", expanded=False):
                        st.text_area("Extracted Text", value=lecture_notes_text, height=180, disabled=True)
                else:
                    st.warning("⚠️ Could not extract readable text from the uploaded PDF. It may be an image-only scan.")
    else:
        lecture_notes_text = st.text_area(
            "Paste your lecture notes, transcript, or textbook content:",
            height=220,
            placeholder="e.g., Photosynthesis is the biological process by which autotrophic organisms convert light energy into chemical energy..."
        )

    # Generate Action Controls
    col_btn, col_stats = st.columns([1, 3])

    with col_btn:
        generate_clicked = st.button("🚀 Generate Study Pack", type="primary", use_container_width=True)

    with col_stats:
        if lecture_notes_text:
            char_count = len(lecture_notes_text)
            word_count = len(lecture_notes_text.split())
            st.caption(f"📊 Current Input: **{char_count:,}** characters | **{word_count:,}** words")

    # Execution of 3-Step Prompt Chain
    if generate_clicked:
        if not api_key:
            st.error("❌ **Missing API Key**: Please enter your Gemini API Key in the sidebar before generating.")
        else:
            # Input Validation (Edge/Invalid Handling)
            is_valid, validation_msg = validate_academic_notes(lecture_notes_text)
            if not is_valid:
                st.warning(f"⚠️ **Invalid Notes Input**: {validation_msg}")
            else:
                try:
                    with st.status("🧠 Executing 3-Step Prompt Engineering Chain...", expanded=True) as status_box:
                        def update_status(step_id, message):
                            st.write(f"🔹 **{step_id}**: {message}")

                        summary_res, key_terms_res, qa_res = execute_prompt_chain(
                            api_key=api_key,
                            model_name=selected_model,
                            temperature=temperature,
                            lecture_notes=lecture_notes_text,
                            status_callback=update_status
                        )

                        status_box.update(
                            label="✅ **Study Pack Generated Successfully!**",
                            state="complete",
                            expanded=False
                        )

                    # Save in session state
                    st.session_state["study_pack"] = {
                        "summary": summary_res,
                        "key_terms": key_terms_res,
                        "practice_qa": qa_res,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "model_used": selected_model,
                    }
                    st.toast("🎉 Study Pack generated successfully!", icon="📚")

                except Exception as exc:
                    st.error(f"❌ **Error executing prompt chain**: {exc}")
                    st.info("Tip: Verify your API key and ensure the selected model is available for your account.")

    # ==========================================
    # --- OUTPUT SECTION: Tabs & Markdown Download ---
    # ==========================================
    st.markdown("---")
    st.subheader("📚 Generated Study Pack")

    stored_pack = st.session_state["study_pack"]

    if stored_pack["summary"] is not None:
        header_col1, header_col2 = st.columns([3, 1])
        with header_col1:
            st.caption(f"Generated at: **{stored_pack['timestamp']}** | Model: `{stored_pack['model_used']}`")
        with header_col2:
            markdown_download = compile_study_pack_markdown(
                summary=stored_pack["summary"],
                key_terms=stored_pack["key_terms"],
                practice_qa=stored_pack["practice_qa"],
                model_name=stored_pack["model_used"] or selected_model
            )
            st.download_button(
                label="📥 Download Full Study Pack (.md)",
                data=markdown_download,
                file_name=f"study_pack_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            )

        # 3 Neat Tabs
        tab_summary, tab_terms, tab_qa = st.tabs([
            "📝 Summary",
            "🔑 Key Terms & Definitions",
            "❓ Practice Q&A"
        ])

        with tab_summary:
            st.markdown(stored_pack["summary"])

        with tab_terms:
            st.markdown(stored_pack["key_terms"])

        with tab_qa:
            st.markdown(stored_pack["practice_qa"])

    else:
        st.info("💡 Your generated study pack will appear here in 3 tabs once generated.")


if __name__ == "__main__":
    main()
