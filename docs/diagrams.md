# 📐 Architecture & Workflow Diagrams
**Project:** AI-Powered Study Pack Generator Using Prompt Engineering  
**Course Code:** SCSE4041 | **Milestone 2**  
**Team:** PE-B25-45 (Visionaries)

---

## 1. 🔄 Sequential Prompt Workflow

This diagram illustrates the 3-step sequential prompt chain (`P1` → `P2` → `P3`), highlighting how context and intermediate outputs are conditioned and passed between steps.

```mermaid
flowchart TD
    A["Raw Lecture Material (PDF / Pasted Text)"] --> B["Pre-LLM Heuristic Validation Gate"]
    
    B -- "Fails Checks (< 30 chars, spam, noise)" --> C["Display Warning Banner (No LLM Call)"]
    
    B -- "Passes Checks" --> D["Step 1: P1_summary"]
    
    subgraph S1["Stage 1: Executive Summary"]
        D --> D1["Input: {lecture_notes}"]
        D1 --> D2["Strict Grounding Prompt"]
        D2 --> D3["Output: {summary}"]
    end
    
    D3 --> E["Step 2: P2_key_terms"]
    
    subgraph S2["Stage 2: Key Terms & Definitions"]
        E --> E1["Input: {lecture_notes} + {summary}"]
        E1 --> E2["Terminology Extraction Prompt"]
        E2 --> E3["Output: {key_terms}"]
    end
    
    E3 --> F["Step 3: P3_practice_qa"]
    
    subgraph S3["Stage 3: Assessment Generation"]
        F --> F1["Input: {lecture_notes} + {key_terms}"]
        F1 --> F2["5 Exam-Style Questions + Answer Key"]
        F2 --> F3["Explicit Fallback: 'Not provided in notes'"]
        F3 --> F4["Output: {practice_qa}"]
    end
    
    D3 --> G["Markdown Study Pack Compiler"]
    E3 --> G
    F4 --> G
    
    G --> H["Render UI Tabs (Summary, Terms, Q&A)"]
    G --> I["Downloadable Study Pack (.md)"]
```

---

## 2. 🧩 Task Decomposition Hierarchy

This diagram decomposes the high-level study pack generation problem into discrete, testable sub-tasks, comparing the monolithic Milestone 1 approach with our chained Milestone 2 architecture.

```mermaid
flowchart TB
    Root["AI-Powered Study Pack Generation"]
    
    subgraph Ingestion["1. Ingestion & Pre-processing"]
        Root --> T1["Text Ingestion Layer"]
        T1 --> T1A["PDF Byte Parser (pypdf)"]
        T1 --> T1B["Raw Text Editor Input"]
        T1 --> T1C["Heuristic Guardrail Validator"]
    end
    
    subgraph Chaining["2. Prompt Chaining Engine"]
        Root --> T2["Sequential Prompt Execution"]
        T2 --> T2A["Task 1: Thematic Summarization (P1)"]
        T2 --> T2B["Task 2: Academic Term Extraction (P2)"]
        T2 --> T2C["Task 3: Exam Q&A Construction (P3)"]
    end
    
    subgraph Guardrails["3. Strict Grounding Constraints"]
        Root --> T3["Anti-Hallucination Policies"]
        T3 --> T3A["Zero Outside Extrapolation Rule"]
        T3 --> T3B["Bounded Term Scope Rule"]
        T3 --> T3C["Missing Fact Sentinel: 'Not provided in notes'"]
    end
    
    subgraph Delivery["4. Output Presentation & Export"]
        Root --> T4["User Presentation Layer"]
        T4 --> T4A["Real-time Execution Status Tracker"]
        T4 --> T4B["Responsive Multi-Tab Display"]
        T4 --> T4C["Single-Click Markdown Exporter"]
    end
```

---

## 3. 🔁 End-to-End Input-Output Flow

This sequence diagram depicts the chronological message exchange between the Student, the Streamlit UI, the Validation Engine, and the Google Gemini API.

```mermaid
sequenceDiagram
    autonumber
    actor User as Student / Evaluator
    participant UI as Streamlit Web App (code/app.py)
    participant Val as Input Validator
    participant Gemini as Google GenAI (gemini-2.5-flash)
    participant State as Streamlit Session State

    User->>UI: Enter API Key, Select Model, Input Notes/PDF
    User->>UI: Click "Generate Study Pack"
    UI->>Val: validate_academic_notes(text)
    
    alt Invalid Input (empty, <30 chars, noise)
        Val-->>UI: Return False + Descriptive Error
        UI-->>User: Show Warning Banner (Execution Halts)
    else Valid Input
        Val-->>UI: Return True
        UI->>UI: Open st.status("Executing 3-Step Chain...")
        
        Note over UI,Gemini: Step 1: Summary Generation (P1)
        UI->>Gemini: generate_content(P1_prompt with {lecture_notes}, temp=0.2)
        Gemini-->>UI: Returns {summary}
        UI->>UI: Update status ("P1 Complete")
        
        Note over UI,Gemini: Step 2: Key Terms Extraction (P2)
        UI->>Gemini: generate_content(P2_prompt with {lecture_notes} + {summary}, temp=0.2)
        Gemini-->>UI: Returns {key_terms}
        UI->>UI: Update status ("P2 Complete")
        
        Note over UI,Gemini: Step 3: Practice Q&A Formulation (P3)
        UI->>Gemini: generate_content(P3_prompt with {lecture_notes} + {key_terms}, temp=0.2)
        Gemini-->>UI: Returns {practice_qa}
        UI->>UI: Update status ("P3 Complete: All Done!")
        
        UI->>State: Store {summary, key_terms, practice_qa, timestamp}
        State-->>UI: Persist in memory
        UI->>User: Display Results in 3 Tabs + Enable .md Download
    end
```

---

## 4. 🏛️ System Architecture

This diagram illustrates the multi-tier architectural layers of the application, showing clean separation of concerns between presentation, orchestration, model integration, and evaluation.

```mermaid
flowchart LR
    subgraph UI_Layer["Presentation Tier (Streamlit)"]
        Sidebar["Sidebar Controls\n- API Key (Masked)\n- Model Selector\n- Temperature Slider"]
        MainInput["Input Area\n- PDF Upload (pypdf)\n- Multi-line Text Area"]
        OutputTabs["Output Viewer\n- 📝 Summary Tab\n- 🔑 Key Terms Tab\n- ❓ Practice Q&A Tab"]
        DownloadBtn["📥 Download (.md) Button"]
    end

    subgraph Logic_Layer["Application & Controller Tier"]
        Validator["Heuristic Guardrail Validator\n(Character, Token & Noise Filters)"]
        ChainOrch["Prompt Chain Orchestrator\n(P1 -> P2 -> P3 Sequence Controller)"]
        MDCompiler["Markdown Compiler\n(Formatting & Timestamping)"]
        BenchRunner["Automated Benchmark Runner\n(code/run_tests.py)"]
    end

    subgraph Service_Layer["Foundation Model Tier (Google Gemini)"]
        GenAIClient["Google GenAI SDK (google-genai)"]
        GeminiFlash["gemini-2.5-flash (Default)\nTemperature: 0.2"]
        PromptTemplates["Prompt Templates\n- P1_summary.txt\n- P2_key_terms.txt\n- P3_practice_qa.txt"]
    end

    subgraph Data_Layer["Storage & Artifacts Tier"]
        TestInputs["test-data/test_inputs.json\n(12 Test Cases)"]
        TestOutputs["test-data/test_outputs.json\n(Execution Logs)"]
        TestTable["test-data/test_results_table.md\n(Results Matrix)"]
    end

    Sidebar --> ChainOrch
    MainInput --> Validator
    Validator -- "Valid" --> ChainOrch
    ChainOrch --> PromptTemplates
    PromptTemplates --> GenAIClient
    GenAIClient --> GeminiFlash
    GeminiFlash --> ChainOrch
    ChainOrch --> MDCompiler
    MDCompiler --> OutputTabs
    MDCompiler --> DownloadBtn

    BenchRunner --> TestInputs
    BenchRunner --> ChainOrch
    BenchRunner --> TestOutputs
    BenchRunner --> TestTable
```
