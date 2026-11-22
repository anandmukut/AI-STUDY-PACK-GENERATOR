<<<<<<< HEAD
# AI-STUDY-PACK-GENERATOR
=======
# AI-Powered Study Pack Generator Using Prompt Engineering 🎓
**Course Code:** SCSE4041 | **Milestone 2 Submission**

---

## 👥 Team & Project Information

- **Project Title:** AI-Powered Study Pack Generator Using Prompt Engineering
- **Team ID:** PE-B25-45
- **Team Name:** Visionaries
- **Batch:** B25 - B36 / Batch 36 Group 9
- **Faculty Mentor:** Saurabh R Srivastava
- **Live Prototype URL:** [INSERT_PROTOTYPE_LINK_HERE]

### 👨‍💻 Team Members

| Enrollment No. | Member Name | Role / Contribution |
| :--- | :--- | :--- |
| **S24CSEU1599** | **Yugansh Gupta** *(Leader)* | Prompt Engineering Architecture & Pipeline Design |
| **S24CSEU1587** | **Himanshu Singh** | UI/UX Development & Streamlit Application |
| **S24CSEU1583** | **Adarsh Kumar** | PDF Text Extraction & Validation Algorithms |
| **S24CSEU1611** | **Parth Singal** | Grounding Constraints & Benchmark Test Cases |
| **S24CSEU1606** | **Mukut Anand** | System Integration, Testing & Documentation |

---

## 📖 What the Project Does

Modern university students and researchers frequently deal with dense, unstructured lecture slides, transcripts, and textbook chapters. Generic summaries produced by basic LLM prompts often introduce hallucinations, miss technical terminology, or generate superficial assessment questions.

The **AI-Powered Study Pack Generator** addresses this through an advanced, sequential **3-step prompt engineering chain** powered by **Google Gemini** (`gemini-2.5-flash`):

1. **P1 — Grounded Executive Summary Generator**:
   Ingests the raw lecture notes (`{lecture_notes}`) and produces an executive summary formatted with logical Markdown headers and high-impact bullet points, strictly grounded in the source text with zero outside extrapolation.

2. **P2 — Key Terms & Definitions Extractor**:
   Takes the original notes (`{lecture_notes}`) together with the P1 summary (`{summary}`) to extract essential domain-specific terms, acronyms, and foundational concepts, defining each strictly within the scope provided in the text.

3. **P3 — Exam Practice Q&A Generator**:
   Takes the original notes (`{lecture_notes}`) and the extracted key terms (`{key_terms}`) to formulate 5 rigorous university exam-style questions (conceptual, analytical, and applied) accompanied by a model answer key and grounding citations. If any requested fact is not in the source text, it explicitly outputs: *"Not provided in notes."*

---

## ✨ Features

- **Sequential Prompt Chaining (`P1 → P2 → P3`)**: Context is decomposed across stages rather than overloaded in a single monolithic prompt, significantly improving grounding and structural consistency.
- **Dual Input Modes**: Upload multi-page academic PDF files (`pypdf` extraction) or paste raw notes directly into the multi-line editor.
- **Heuristic Input Validation**: Blocks empty inputs, texts under 30 characters, keyboard spam, symbol floods, and non-academic noise before calling LLM APIs.
- **Interactive UI**: Password-masked API key input, dynamic Gemini model selector, temperature slider (default `0.2` for deterministic factuality), and progress tracking via `st.status`.
- **Organized Output & Export**: View generated outputs in 3 tabs (`📝 Summary`, `🔑 Key Terms & Definitions`, `❓ Practice Q&A`) and download the compiled study pack as a clean `.md` document.

---

## 🏗️ Repository Structure

```
AI-Study-Pack-Generator-M2/
├── .env.example                       # Sample environment file for API keys
├── .gitignore                         # Excludes .env, __pycache__, *.pyc
├── CHANGELOG.md                       # Progression log from Milestone 1 to Milestone 2
├── README.md                          # Project documentation and team metadata
├── requirements.txt                   # Project dependencies (streamlit, google-genai, etc.)
├── code/
│   ├── app.py                         # Streamlit application with modern UI & prompt chain
│   └── run_tests.py                   # Automated benchmark test runner for 12 test cases
├── docs/
│   └── diagrams.md                    # Mermaid.js system, workflow & architecture diagrams
├── prompts/
│   ├── v1/
│   │   └── baseline_prompt.txt        # Milestone 1 monolithic baseline prompt
│   ├── v2/
│   │   └── structured_grounded_prompt.txt # Intermediate grounded prompt with anti-hallucination
│   ├── v3/
│   │   └── chained_prompts_draft.txt  # Initial 3-step prompt chain draft
│   └── final/
│       ├── P1_summary.txt             # Final P1 executive summary prompt template
│       ├── P2_key_terms.txt           # Final P2 key terms prompt template
│       └── P3_practice_qa.txt         # Final P3 exam Q&A prompt template
├── test-data/
│   ├── test_inputs.json               # 12 diverse test cases (Normal, Edge, Invalid)
│   ├── test_outputs.json              # Real test outputs from prompt chain execution
│   └── test_results_table.md          # Formatted results and evaluation matrix
└── tests/
    └── test_app.py                    # Unit tests for validation, parsing, and templates
```

---

## 🚀 Setup & Execution Guide

### Prerequisites
- Python 3.10, 3.11, or 3.12 installed on your system.
- A Google Gemini API Key ([Get a free key at Google AI Studio](https://aistudio.google.com/)).

### Step 1: Clone the Repository & Navigate to Workspace
```bash
git clone <repository-url>
cd AI-Study-Pack-Generator-M2
```

### Step 2: Install Required Dependencies
Install the required packages listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### Step 3: (Optional) Configure Environment Variables
Copy `.env.example` to `.env` and insert your Gemini API key:
```bash
cp .env.example .env
```
Inside `.env`:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```
*(Note: You can also enter or paste your Gemini API key directly into the password-masked input in the Streamlit sidebar at runtime).*

### Step 4: Run the Streamlit Application
Launch the application:
```bash
streamlit run code/app.py
```
Open your web browser and navigate to: `http://localhost:8501`.

### Step 5: Run Automated Benchmark Tests
To execute the automated 12-test suite across Normal, Edge, and Invalid test cases:
```bash
python code/run_tests.py
```
This generates:
- `test-data/test_outputs.json`
- `test-data/test_results_table.md`

### Step 6: Run Unit Tests
To verify validation rules and prompt template formatting:
```bash
python tests/test_app.py
```
>>>>>>> 52ca8e3 (Initial commit)
