# 📑 Technical Report: AI-Powered Study Pack Generator
**Course:** SCSE4041 — Natural Language Processing & Prompt Engineering  
**Project Milestone:** Milestone 2 Technical Supporting Document  
**Team Name:** Visionaries (Team ID: PE-B25-45) | **Batch:** B25 - B36 / Batch 36 Group 9  
**Faculty Mentor:** Saurabh R Srivastava | **Date:** November 22, 2026  

---

## 1. Executive Summary & Architectural Overview

The **AI-Powered Study Pack Generator** is an automated educational pipeline designed to transform unstructured lecture materials (textbook excerpts, lecture notes, or syllabus PDFs) into strictly-grounded, multi-part study packs comprising an executive summary, domain terminology definitions, and exam practice questions with answer keys. 

In Milestone 1, a single monolithic prompt was employed, resulting in severe output dilution, frequent hallucinations of unmentioned textbook facts, and brittle formatting. In Milestone 2, we refactored the system into a **3-stage sequential Prompt Engineering Chain (`P1` → `P2` → `P3`)** hosted within a lightweight, responsive **Streamlit** web application and backed by **Google Gemini 2.5 Flash** via the `google-genai` SDK. By decomposing the cognitive load across dedicated prompt stages and enforcing strict negative grounding constraints at temperature `0.2`, the system achieves zero ungrounded extrapolations on standard academic benchmark texts.

```
[Raw Notes / PDF Upload] 
         │
         ▼
[Heuristic Validation Gate] ──(Fails: <30 chars/noise)──► [Warning Alert (No LLM Call)]
         │ (Passes)
         ▼
[P1: Summary Generator] ──► {summary}
         │
         ▼
[P2: Key Terms Extractor] (conditioned on {notes} + {summary}) ──► {key_terms}
         │
         ▼
[P3: Practice Q&A Generator] (conditioned on {notes} + {key_terms}) ──► {practice_qa}
         │
         ▼
[Markdown Compiler] ──► [3-Tab UI Display] + [Exportable study_pack.md]
```

---

## 2. Tools, Frameworks & Foundation Model Selection

- **Foundation Model (`gemini-2.5-flash`)**: Selected for its exceptional reasoning-to-latency ratio, high instruction-following adherence, and native support for structured markdown. Operating at a deterministic temperature of `0.2`, it prioritizes factual fidelity and eliminates creative hallucination.
- **Client SDK (`google-genai` v3.6.1)**: Utilizes Google's modern GenAI Python SDK (`genai.Client`) with explicit `GenerateContentConfig(temperature=0.2)`.
- **Application Framework (`Streamlit` v1.67)**: Provides a clean, modern single-page application (SPA) featuring password-masked API key handling, dynamic model switching, real-time step execution status (`st.status`), tabbed outputs, and client-side markdown export (`st.download_button`).
- **Document Processing (`pypdf` v7.1.1)**: Performs client-side PDF parsing across all document pages, extracting pure text buffers prior to validation and inference.
- **Environment Management (`python-dotenv`)**: Securely loads local credentials from `.env` without exposing keys to version control.

---

## 3. Prompt Chaining Design (`P1` → `P2` → `P3`)

Rather than forcing the LLM to simultaneously summarize, extract terms, and author exam questions in a single context window, our design partitions the task into three interdependent stages:

1. **`P1_summary` (Executive Summary Generator)**:
   - *Input:* `{lecture_notes}`
   - *Objective:* Ingests raw text, identifies thematic core topics, and constructs a structured executive summary using Markdown headers (`##`, `###`) and concise bullet points.
   - *Constraint:* Strict textual grounding; zero external extrapolation.
2. **`P2_key_terms` (Key Terms & Definitions Extractor)**:
   - *Input:* `{lecture_notes}`, `{summary}`
   - *Objective:* Scans the notes guided by the P1 summary to identify technical keywords, acronyms, and formulas, generating a bolded markdown glossary (`- **[Term]**: [Definition]`).
   - *Constraint:* Terms not explicitly defined in the text are defined strictly within their recorded context rather than from external training memory.
3. **`P3_practice_qa` (Exam Practice Q&A Generator)**:
   - *Input:* `{lecture_notes}`, `{key_terms}`
   - *Objective:* Generates exactly 5 exam-style questions (2 Conceptual, 2 Applied/Analytical, 1 Synthesis) with model answers and grounding citations.
   - *Constraint:* If an exam question asks about a topic missing from the notes, the model is strictly mandated to answer: *"Not provided in notes."*

---

## 4. Quantitative Evaluation & Prompt Evolution Summary

We evaluated 10 standard university lecture excerpts across the 3 prompt iterations (`v1` Milestone 1 Baseline, `v2` Grounded Monolith, and `v3` Final Sequential Chain):

| Evaluation Metric | v1 (M1 Baseline) | v2 (Grounded Monolith) | v3 (Final 3-Step Chain) |
| :--- | :---: | :---: | :---: |
| **Prompt Architecture** | Single Monolithic Prompt | Single Constrained Prompt | 3-Step Sequential Chain |
| **Operating Temperature** | `0.7` (Creative) | `0.3` (Constrained) | `0.2` (Deterministic) |
| **Hallucination Rate (Out of 10 runs)** | 60% (6/10 runs added external facts) | 20% (2/10 runs had minor bleed) | **0% (0/10 runs had ungrounded facts)** |
| **Schema & Markdown Compliance** | 40% (Erratic formatting) | 80% (Occasional missed headers) | **100% (Strict markdown adhered)** |
| **Questions Generated Count** | Fluctuated (2 to 4 questions) | 5 questions (often superficial) | **Exactly 5 with citations & keys** |
| **Key Term Depth** | 2-3 generic words | 4-5 terms | **6-10 domain-specific terms** |
| **Pre-LLM Guardrail Filter** | ❌ None (processed noise/spam) | ❌ None | **✅ Heuristic Gate (catches empty/noise)** |
| **Average End-to-End Latency** | ~3.8 seconds | ~4.2 seconds | **~6.5 seconds (total across 3 steps)** |

---

## 5. Current Limitations & Failure Modes

1. **Scanned Image-Only PDFs**: Text extraction relies on `pypdf`, which extracts native digital text layers. Scanned bitmap PDFs lacking embedded OCR text layers return empty buffers, which trigger the validation guardrail rather than OCR processing.
2. **Heavy Colloquial/Bilingual (Hinglish) Notes**: While `gemini-2.5-flash` successfully comprehends mixed Hindi-English academic notes, definition formatting occasionally mixes syntax styles when phonetic Romanized Hindi is blended with English technical jargon.
3. **Complex Embedded Equations**: Multi-line mathematical equations represented with non-standard ASCII shorthand in raw lecture notes may suffer minor formatting distortion during PDF text extraction before reaching the prompt chain.
4. **Context Dilution on Full-Length Books (>50 pages)**: While Gemini Flash has a large context window, single-pass chaining on an entire textbook chapter without chunking or retrieval (RAG) can lead to attention compression in the middle sections of P1 summaries.
