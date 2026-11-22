# 🧪 Milestone 2 Test Evaluation & Results Matrix
*Generated on: 2026-11-22 18:14:15* | *Course: SCSE4041* | *Team: PE-B25-45 (Visionaries)*

## 📊 Executive Summary Metrics
- **Total Benchmark Cases**: `12`
- **Academic Inputs Accepted & Processed**: `10`
- **Invalid Inputs Correctly Filtered (Guardrails)**: `2`
- **Benchmark Pass Rate**: `100.0% (12/12)`
- **Hallucinations Detected**: `0` (Strictly grounded)

---

## 📋 Comprehensive Test Cases & Evaluation Matrix

| ID | Category | Domain / Topic | Chars | Validation Status | Chain Status | Grounding Adherence | Test Result |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-01** | Normal | DBMS | 1,040 | ✅ Valid | ✅ Completed | 100% Grounded | **✅ PASS** |
| **TC-02** | Normal | Machine Learning | 1,036 | ✅ Valid | ✅ Completed | 100% Grounded | **✅ PASS** |
| **TC-03** | Normal | Operating Systems | 1,017 | ✅ Valid | ✅ Completed | 100% Grounded | **✅ PASS** |
| **TC-04** | Normal | Data Structures & Algorithms | 994 | ✅ Valid | ✅ Completed | 100% Grounded | **✅ PASS** |
| **TC-05** | Normal | Computer Networks | 937 | ✅ Valid | ✅ Completed | 100% Grounded | **✅ PASS** |
| **TC-06** | Normal | Software Engineering | 998 | ✅ Valid | ✅ Completed | 100% Grounded | **✅ PASS** |
| **TC-07** | Edge | Computer Science (Bilingual/Hinglish) | 781 | ✅ Valid | ✅ Completed | 100% Grounded | **✅ PASS** |
| **TC-08** | Edge | Computer Science (Fragmented Notes) | 448 | ✅ Valid | ✅ Completed | 100% Grounded | **✅ PASS** |
| **TC-09** | Edge | Mathematics & Probability | 597 | ✅ Valid | ✅ Completed | 100% Grounded | **✅ PASS** |
| **TC-10** | Edge | Contradictory / Erroneous Content | 442 | ✅ Valid | ✅ Completed | 100% Grounded | **✅ PASS** |
| **TC-11** | Invalid | Input Edge Case | 0 | 🛑 Rejected | ⛔ Skipped | N/A (Correctly Rejected) | **✅ PASS** |
| **TC-12** | Invalid | Input Edge Case | 11 | 🛑 Rejected | ⛔ Skipped | N/A (Correctly Rejected) | **✅ PASS** |

---

## 🔍 In-Depth Test Category Observations

### 1. Normal Academic Cases (TC-01 through TC-06)
- **Domains Covered**: DBMS Normalization, Machine Learning Paradigms, OS CPU Scheduling & Deadlocks, Data Structures (AVL Trees), Computer Networks (TCP Handshake), and Software Engineering (Agile vs Waterfall).
- **Result**: All 6 inputs passed heuristic validation. The 3-step prompt chain cleanly generated executive summaries, extracted technical keywords, and constructed 5 targeted practice questions.
- **Grounding Adherence**: 100%. All model answers cited facts explicitly presented in the source notes without extraneous textbook additions.

### 2. Edge Cases (TC-07 through TC-10)
- **TC-07 (Bilingual/Hinglish)**: Accurately digested conversational bilingual lecture notes on ACID transactions, isolating technical terms (`Atomicity`, `Write-Ahead Logging`) while preserving English definitions.
- **TC-08 (Bullet-Only Fragments)**: Handled disjointed compiler phase shorthand without hallucinating missing transitional prose.
- **TC-09 (Mathematical Formulas)**: Preserved Bayes' Theorem formula notations (`P(A|B) = [P(B|A)*P(A)]/P(B)`) and correctly formatted probability terms.
- **TC-10 (Contradictory Networking Notes)**: Verified extreme anti-hallucination obedience. Even when the notes claimed contradictory statements (e.g. *TCP is connectionless*), the prompt chain strictly adhered to the user's text and did not 'correct' it using external knowledge.

### 3. Invalid Guardrail Cases (TC-11 and TC-12)
- **TC-11 (Empty String `""`)**: Pre-LLM heuristic check immediately stopped execution and raised a descriptive warning, preventing wasteful API calls.
- **TC-12 (Short Noise `"idk help me"`)**: Flagged for insufficient character length (< 30 characters) and lack of academic substance, returning an actionable error message.

---
*Report compiled by Automated Benchmark Suite (`code/run_tests.py`)*