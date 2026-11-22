"""
Unit tests for AI Study Pack Generator validation, formatting, and components.
"""

import sys
import os
import unittest
from io import BytesIO

# Add code/ to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "code")))

from app import (
    validate_academic_notes,
    compile_study_pack_markdown,
    extract_text_from_pdf,
    PROMPT_1_SUMMARY,
    PROMPT_2_KEY_TERMS,
    PROMPT_3_PRACTICE_QA,
)
import pypdf


class TestStudyPackGenerator(unittest.TestCase):
    def test_imports(self):
        """Verify all critical libraries can be imported without error."""
        import streamlit
        import pypdf
        import dotenv
        from google import genai
        from google.genai import types
        self.assertIsNotNone(streamlit)
        self.assertIsNotNone(pypdf)
        self.assertIsNotNone(dotenv)
        self.assertIsNotNone(genai)

    def test_validation_empty(self):
        """Verify that empty text is rejected."""
        valid, msg = validate_academic_notes("")
        self.assertFalse(valid)
        self.assertIn("empty", msg.lower())

    def test_validation_too_short(self):
        """Verify that text under 30 characters is rejected."""
        valid, msg = validate_academic_notes("Too short notes")
        self.assertFalse(valid)
        self.assertIn("short", msg.lower())

    def test_validation_repetitive_gibberish(self):
        """Verify that repetitive character spam is rejected."""
        valid1, _ = validate_academic_notes("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        self.assertFalse(valid1)

        valid2, msg2 = validate_academic_notes("word word word word word word word word word word")
        self.assertFalse(valid2)
        self.assertIn("repetitive", msg2.lower())

    def test_validation_symbol_spam(self):
        """Verify that non-text/symbol heavy junk is rejected."""
        valid, _ = validate_academic_notes("!@#$%^&*()!@#$%^&*()!@#$%^&*()!@#$%^&*()")
        self.assertFalse(valid)

    def test_validation_valid_notes(self):
        """Verify that standard academic lecture notes pass validation."""
        valid_notes = (
            "Photosynthesis is the biological process used by plants and other organisms "
            "to convert light energy into chemical energy. This chemical energy is stored in carbohydrate "
            "molecules, such as sugars, which are synthesized from carbon dioxide and water."
        )
        valid, msg = validate_academic_notes(valid_notes)
        self.assertTrue(valid)
        self.assertEqual(msg, "")

    def test_prompt_formatting(self):
        """Verify prompt templates format properly without KeyError or formatting bugs."""
        p1 = PROMPT_1_SUMMARY.format(lecture_notes="Sample lecture notes on machine learning.")
        self.assertIn("Sample lecture notes on machine learning.", p1)
        self.assertIn("STRICT GROUNDING RULES", p1)

        p2 = PROMPT_2_KEY_TERMS.format(
            lecture_notes="Sample lecture notes.",
            summary="Sample summary."
        )
        self.assertIn("Sample lecture notes.", p2)
        self.assertIn("Sample summary.", p2)

        p3 = PROMPT_3_PRACTICE_QA.format(
            lecture_notes="Sample lecture notes.",
            key_terms="Term 1: Definition 1"
        )
        self.assertIn("Term 1: Definition 1", p3)
        self.assertIn("Not provided in notes", p3)

    def test_compile_study_pack_markdown(self):
        """Verify markdown compilation incorporates all sections and metadata."""
        md = compile_study_pack_markdown(
            summary="- Point 1\n- Point 2",
            key_terms="- **AI**: Artificial Intelligence",
            practice_qa="### Question 1: What is AI?\n- **Model Answer**: ...",
            model_name="gemini-2.5-flash"
        )
        self.assertIn("# 📚 AI-Generated Study Pack", md)
        self.assertIn("## 📝 1. Grounded Executive Summary", md)
        self.assertIn("- Point 1", md)
        self.assertIn("## 🔑 2. Key Terms & Definitions", md)
        self.assertIn("- **AI**: Artificial Intelligence", md)
        self.assertIn("## ❓ 3. Exam Practice Questions & Solutions", md)
        self.assertIn("gemini-2.5-flash", md)

    def test_pdf_extraction(self):
        """Verify PDF text extraction with a synthesized in-memory PDF."""
        writer = pypdf.PdfWriter()
        writer.add_blank_page(width=200, height=200)
        pdf_bytes = BytesIO()
        writer.write(pdf_bytes)
        pdf_bytes.seek(0)
        extracted = extract_text_from_pdf(pdf_bytes)
        self.assertIsInstance(extracted, str)


if __name__ == "__main__":
    unittest.main()
