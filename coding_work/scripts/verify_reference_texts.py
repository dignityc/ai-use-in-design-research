#!/usr/bin/env python3
"""
Reference Text Verification System

Verifies that reference texts from PDF analysis actually exist in the original PDFs.
Uses 2-page chunking and Claude CLI for thorough verification.

Author: Auto-generated
Date: 2025-11-07
"""

import os
import sys
import json
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import pandas as pd
import pdfplumber

# Add parent directory to path for imports
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Configuration
PAPERS_DIR = PROJECT_ROOT / "Papers"
RESULTS_DIR = SCRIPT_DIR.parent / "results"
PDF_ANALYSIS_DIR = RESULTS_DIR / "pdf_analysis"
PDF_REFERENCES_CSV = PDF_ANALYSIS_DIR / "pdf_references.csv"

# Output files
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
VERIFICATION_RESULTS_CSV = RESULTS_DIR / f"reference_verification_{TIMESTAMP}.csv"
VERIFICATION_PROGRESS_JSON = RESULTS_DIR / f"reference_verification_progress_{TIMESTAMP}.json"

# Categories to verify (7 categories)
CATEGORIES = [
    "Design Discipline",
    "Data About",
    "Data Modality",
    "AI methods",
    "AI Assistance Types (Lee and Kim, 2025)",
    "Design Phase",
    "Design Practice/Task"
]

# Thread-safe locks
csv_lock = threading.Lock()
progress_lock = threading.Lock()


class ReferenceVerifier:
    """Verifies reference texts against original PDF content"""

    def __init__(self, workers: int = 5, chunk_size: int = 5, source: str = "csv"):
        """
        Initialize the verifier

        Args:
            workers: Number of parallel workers
            chunk_size: Number of pages per chunk (default: 5)
            source: Data source - 'csv' for J's papers, 'sheets' for M's papers
        """
        self.workers = workers
        self.chunk_size = chunk_size
        self.overlap = 1  # 1 page overlap between chunks
        self.source = source
        self.progress_data = {
            "total_tasks": 0,
            "completed": 0,
            "failed": 0,
            "in_progress": [],
            "completed_tasks": [],
            "failed_tasks": {}
        }

        # Load reference data
        self.references_df = None
        self.load_references()

        # Initialize results CSV with headers
        self.init_results_csv()

    def load_references(self):
        """Load reference texts from CSV or Google Sheets"""
        if self.source == "csv":
            # Load from CSV (J's papers)
            if not PDF_REFERENCES_CSV.exists():
                raise FileNotFoundError(f"References CSV not found: {PDF_REFERENCES_CSV}")

            print(f"📂 Loading reference data from: {PDF_REFERENCES_CSV}")
            self.references_df = pd.read_csv(PDF_REFERENCES_CSV)
            print(f"✅ Loaded {len(self.references_df)} papers with reference texts (J's papers)")

        elif self.source == "sheets":
            # Load from Google Sheets (M's papers)
            print(f"📂 Loading reference data from Google Sheets (M's papers)...")
            self.references_df = self._load_from_google_sheets()
            print(f"✅ Loaded {len(self.references_df)} papers with reference texts (M's papers)")

    def _load_from_google_sheets(self) -> pd.DataFrame:
        """
        Load notes from Google Sheets CodedPapers_2 sheet

        Returns:
            DataFrame with Index, Article Title, and category notes
        """
        try:
            import gspread
            from google.oauth2.service_account import Credentials

            # Setup credentials
            CREDENTIALS_DIR = SCRIPT_DIR.parent / "credentials"
            CREDENTIALS_FILE = CREDENTIALS_DIR / "gen-lang-client-0444199460-38266703559b.json"
            SPREADSHEET_ID = "1MgMKl7b8y5hPScQZJQ5y8y-J_UY1qalgVnQEFOucbBM"

            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]

            creds = Credentials.from_service_account_file(str(CREDENTIALS_FILE), scopes=scopes)
            client = gspread.authorize(creds)

            spreadsheet = client.open_by_key(SPREADSHEET_ID)
            worksheet = spreadsheet.worksheet("CodedPapers_2")

            # Get all values and notes
            all_values = worksheet.get_all_values()
            all_notes = worksheet.get_notes()

            # Build DataFrame
            headers = all_values[0]
            data_rows = all_values[1:]

            # Find column indices
            idx_col = headers.index("Index") if "Index" in headers else 0
            title_col = headers.index("Article Title") if "Article Title" in headers else 1

            # Category columns (G-M in sheets, 0-indexed: 6-12)
            category_cols = {
                "Design Discipline": 6,
                "Data About": 7,
                "Data Modality": 8,
                "AI methods": 9,
                "AI Assistance Types (Lee and Kim, 2025)": 10,
                "Design Phase": 11,
                "Design Practice/Task": 12
            }

            # Build records with notes as reference text
            records = []
            for row_idx, row in enumerate(data_rows, start=2):  # 2 because 1-indexed + header
                if not row[idx_col]:  # Skip empty rows
                    continue

                record = {
                    "Index": row[idx_col],
                    "Article Title": row[title_col] if title_col < len(row) else ""
                }

                # Get notes for each category
                for cat_name, col_idx in category_cols.items():
                    # Get note from this cell (row_idx is 1-indexed in sheets)
                    note_key = f"R{row_idx}C{col_idx + 1}"  # 1-indexed for notes

                    # Notes dict uses (row, col) tuple with 0-indexed
                    note = ""
                    for (r, c), n in all_notes.items() if isinstance(all_notes, dict) else []:
                        if r == row_idx - 1 and c == col_idx:
                            note = n
                            break

                    # Alternative: check if all_notes is a list of lists
                    if isinstance(all_notes, list) and row_idx - 1 < len(all_notes):
                        if col_idx < len(all_notes[row_idx - 1]):
                            note = all_notes[row_idx - 1][col_idx] or ""

                    record[cat_name] = note

                records.append(record)

            df = pd.DataFrame(records)
            print(f"   Found {len(df)} rows with notes")

            # Filter to only rows that have at least one note
            has_notes = df[CATEGORIES].apply(lambda x: any(str(v).strip() for v in x if pd.notna(v)), axis=1)
            df = df[has_notes]
            print(f"   {len(df)} rows have at least one note")

            return df

        except Exception as e:
            print(f"❌ Failed to load from Google Sheets: {str(e)}")
            raise

    def init_results_csv(self):
        """Initialize results CSV with headers"""
        headers = [
            "Index",
            "Article_Title",
            "Category",
            "Reference_Text_Preview",
            "Found",
            "Page_Numbers",
            "Match_Confidence",
            "Verification_Method",
            "Issue_Type",
            "Full_Reference_Text",
            "Notes",
            "Timestamp"
        ]

        if not VERIFICATION_RESULTS_CSV.exists():
            df = pd.DataFrame(columns=headers)
            df.to_csv(VERIFICATION_RESULTS_CSV, index=False)
            print(f"✅ Initialized results CSV: {VERIFICATION_RESULTS_CSV}")

    def _extract_full_pdf_text(self, pdf_path: Path) -> str:
        """
        Extract full text from PDF for local search

        Args:
            pdf_path: Path to PDF file

        Returns:
            Full text from all pages concatenated
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                texts = [page.extract_text() or '' for page in pdf.pages]
            full_text = ' '.join(texts)
            # Clean problematic characters
            full_text = full_text.replace('\x00', '')
            return full_text
        except Exception as e:
            print(f"   ⚠️  PDF text extraction error: {str(e)}")
            return ""

    def _local_text_search(self, reference_text: str, pdf_text: str) -> Dict:
        """
        Perform local text search with normalization

        Args:
            reference_text: Reference text to search for
            pdf_text: Full PDF text to search in

        Returns:
            Search result dictionary
        """
        import re

        # Normalize both texts (lowercase, collapse whitespace)
        ref_norm = re.sub(r'\s+', ' ', reference_text.lower().strip())
        pdf_norm = re.sub(r'\s+', ' ', pdf_text.lower())

        # Skip if reference is too short
        if len(ref_norm) < 20:
            return {"found": False, "reason": "Reference too short for reliable search"}

        # Full match search
        if ref_norm in pdf_norm:
            return {
                "found": True,
                "match_type": "EXACT",
                "confidence": 100,
                "location_description": "Found via local text search (full match)",
                "issue": "NONE",
                "page_numbers": "LOCAL"
            }

        # Partial match (first 50 chars)
        partial = ref_norm[:50]
        if len(partial) > 20 and partial in pdf_norm:
            return {
                "found": True,
                "match_type": "PARTIAL",
                "confidence": 80,
                "location_description": "Found via local text search (partial match - first 50 chars)",
                "issue": "NONE",
                "page_numbers": "LOCAL"
            }

        # Try with first sentence only (more flexible)
        first_sentence = ref_norm.split('.')[0] if '.' in ref_norm else ref_norm[:80]
        if len(first_sentence) > 30 and first_sentence in pdf_norm:
            return {
                "found": True,
                "match_type": "PARTIAL",
                "confidence": 70,
                "location_description": "Found via local text search (first sentence match)",
                "issue": "NONE",
                "page_numbers": "LOCAL"
            }

        return {"found": False}

    def _split_pdf_to_sentences(self, pdf_path: Path) -> List[str]:
        """
        PDF를 문장 단위로 분리

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of sentences from PDF
        """
        import re

        try:
            full_text = self._extract_full_pdf_text(pdf_path)
            if not full_text:
                return []

            # 문장 분리 (마침표, 물음표, 느낌표 기준)
            # 단, 약어(e.g., i.e., etc.)는 보존
            sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', full_text)

            # 너무 짧은 문장 필터링 (최소 20자)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

            return sentences

        except Exception as e:
            print(f"   ⚠️  Sentence splitting error: {str(e)}")
            return []

    def _extract_candidate_sentences(self, comment: str, sentences: List[str], top_k: int = 20) -> List[str]:
        """
        TF-IDF 코사인 유사도로 코멘트와 관련된 후보 문장 추출

        Args:
            comment: Comment text to match
            sentences: List of PDF sentences
            top_k: Number of candidates to return

        Returns:
            List of top-k candidate sentences
        """
        if not sentences:
            return []

        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            # TF-IDF 벡터화
            vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
            all_texts = [comment] + sentences

            tfidf_matrix = vectorizer.fit_transform(all_texts)

            # 코멘트(0번)와 각 문장의 유사도 계산
            similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

            # 상위 K개 인덱스 (유사도 높은 순)
            top_indices = similarities.argsort()[-top_k:][::-1]

            # 유사도가 0.05 이상인 것만 반환
            candidates = []
            for idx in top_indices:
                if similarities[idx] > 0.05:
                    candidates.append(sentences[idx])

            return candidates

        except Exception as e:
            print(f"   ⚠️  Candidate extraction error: {str(e)}")
            # Fallback: 키워드 기반 추출
            return self._extract_candidates_keyword(comment, sentences, top_k)

    def _extract_candidates_keyword(self, comment: str, sentences: List[str], top_k: int = 10) -> List[str]:
        """
        키워드 기반 후보 문장 추출 (fallback)

        Args:
            comment: Comment text
            sentences: List of PDF sentences
            top_k: Number of candidates

        Returns:
            List of candidate sentences
        """
        import re

        # 코멘트에서 주요 단어 추출 (3글자 이상, 불용어 제외)
        stopwords = {'the', 'and', 'for', 'are', 'was', 'were', 'been', 'being', 'have', 'has', 'had',
                     'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
                     'this', 'that', 'these', 'those', 'with', 'from', 'into', 'through', 'during',
                     'before', 'after', 'above', 'below', 'between', 'under', 'again', 'further',
                     'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'each',
                     'few', 'more', 'most', 'other', 'some', 'such', 'only', 'own', 'same', 'than',
                     'too', 'very', 'can', 'just', 'also', 'which', 'their', 'about', 'based'}

        words = re.findall(r'\b[a-zA-Z]{3,}\b', comment.lower())
        keywords = [w for w in words if w not in stopwords]

        # 각 문장에 키워드 매칭 점수 계산
        scored = []
        for sent in sentences:
            sent_lower = sent.lower()
            score = sum(1 for kw in keywords if kw in sent_lower)
            if score > 0:
                scored.append((score, sent))

        # 점수 높은 순 정렬
        scored.sort(reverse=True, key=lambda x: x[0])

        return [sent for _, sent in scored[:top_k]]

    def _verify_with_candidates(self, comment: str, candidates: List[str]) -> Dict:
        """
        후보 문장들과 코멘트를 Claude CLI에 전달하여 1회 검증

        Args:
            comment: Comment text to verify
            candidates: List of candidate sentences from PDF

        Returns:
            Verification result dictionary
        """
        if not candidates:
            return {
                "found": False,
                "match_type": "NONE",
                "confidence": 0,
                "location_description": "No candidate sentences found",
                "issue": "HALLUCINATION"
            }

        # 후보 문장 포맷팅
        candidates_text = "\n".join([f"{i+1}. \"{c[:300]}{'...' if len(c) > 300 else ''}\""
                                      for i, c in enumerate(candidates)])

        prompt = f"""TASK: Verify if the COMMENT is based on content from the PDF.

COMMENT (to verify):
\"\"\"{comment}\"\"\"

CANDIDATE SENTENCES (extracted from PDF based on similarity):
{candidates_text}

INSTRUCTIONS:
1. Check if any candidate sentence(s) support the COMMENT
2. The COMMENT may be:
   - EXACT: Direct quote from PDF
   - PARAPHRASE: Rephrased but same meaning
   - SEMANTIC: Related concept but different wording
   - NONE: No matching content in candidates

OUTPUT FORMAT (JSON only, no markdown):
{{
  "found": true/false,
  "matching_candidates": [1, 3],
  "match_type": "EXACT/PARAPHRASE/SEMANTIC/NONE",
  "confidence": 0-100,
  "issue": "NONE/PARAPHRASE/HALLUCINATION",
  "explanation": "brief explanation"
}}

Return ONLY the JSON object."""

        try:
            result = subprocess.run(
                ["claude", "-p", "--output-format", "json", prompt],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                return {
                    "found": False,
                    "match_type": "ERROR",
                    "confidence": 0,
                    "location_description": f"Claude CLI error: {result.stderr}",
                    "issue": "CLI_ERROR"
                }

            # Parse response
            response_text = result.stdout.strip()
            outer_json = json.loads(response_text)
            inner_result = outer_json.get("result", "")

            # Handle markdown code blocks
            if "```json" in inner_result:
                json_start = inner_result.find("```json") + 7
                json_end = inner_result.find("```", json_start)
                inner_result = inner_result[json_start:json_end].strip()
            elif "```" in inner_result:
                json_start = inner_result.find("```") + 3
                json_end = inner_result.find("```", json_start)
                inner_result = inner_result[json_start:json_end].strip()

            verification_result = json.loads(inner_result)
            verification_result["page_numbers"] = "CANDIDATES"

            return verification_result

        except subprocess.TimeoutExpired:
            return {
                "found": False,
                "match_type": "ERROR",
                "confidence": 0,
                "location_description": "Claude CLI timeout",
                "issue": "TIMEOUT"
            }
        except json.JSONDecodeError as e:
            return {
                "found": False,
                "match_type": "ERROR",
                "confidence": 0,
                "location_description": f"JSON parse error: {str(e)}",
                "issue": "PARSE_ERROR"
            }
        except Exception as e:
            return {
                "found": False,
                "match_type": "ERROR",
                "confidence": 0,
                "location_description": f"Verification error: {str(e)}",
                "issue": "UNKNOWN_ERROR"
            }

    def _verify_category(self, category: str, reference_text: str,
                         full_text: str, sentences: List[str]) -> Dict:
        """
        카테고리 하나 검증 (PDF 전처리 결과 재사용)

        Args:
            category: Category name
            reference_text: Reference text to verify
            full_text: Pre-extracted full PDF text
            sentences: Pre-split sentences from PDF

        Returns:
            Verification result dictionary
        """
        try:
            # Stage 1: 로컬 검색 (full_text 재사용)
            if full_text:
                local_result = self._local_text_search(reference_text, full_text)
                if local_result.get("found", False):
                    return local_result

            # Stage 2: 후보 추출 (sentences 재사용) + Claude CLI
            if not sentences:
                return {
                    "found": False,
                    "match_type": "NONE",
                    "confidence": 0,
                    "location_description": "No sentences available",
                    "issue": "OCR_ERROR",
                    "page_numbers": "N/A"
                }

            candidates = self._extract_candidate_sentences(reference_text, sentences, top_k=20)

            if not candidates:
                return {
                    "found": False,
                    "match_type": "NONE",
                    "confidence": 0,
                    "location_description": "No similar sentences found",
                    "issue": "HALLUCINATION",
                    "page_numbers": "N/A"
                }

            result = self._verify_with_candidates(reference_text, candidates)
            return result

        except Exception as e:
            return {
                "found": False,
                "match_type": "ERROR",
                "confidence": 0,
                "location_description": f"Category verification error: {str(e)}",
                "issue": "UNKNOWN_ERROR",
                "page_numbers": "N/A"
            }

    def process_paper_with_cache(self, index: str, article_title: str,
                                  pdf_path: Path, tasks: List[Tuple]) -> List[Dict]:
        """
        한 논문의 모든 카테고리를 캐싱 + 병렬로 처리

        Args:
            index: Paper index
            article_title: Paper title
            pdf_path: Path to PDF file
            tasks: List of (category, reference_text) tuples

        Returns:
            List of verification results
        """
        print(f"\n{'='*60}")
        print(f"📄 [{index}] Processing paper with {len(tasks)} categories")
        print(f"   PDF: {pdf_path.name}")
        print(f"{'='*60}")

        # Step 1: PDF 전처리 (1회만)
        print(f"   📖 Extracting PDF text (1 time)...")
        full_text = self._extract_full_pdf_text(pdf_path)
        print(f"      Text length: {len(full_text)} chars")

        print(f"   📝 Splitting into sentences (1 time)...")
        sentences = self._split_pdf_to_sentences(pdf_path)
        print(f"      Sentences: {len(sentences)}")

        # Step 2: 카테고리별 병렬 처리
        print(f"   🚀 Running {len(tasks)} categories in parallel...")

        results = []

        with ThreadPoolExecutor(max_workers=7) as executor:
            # Submit all category verifications
            future_to_task = {}
            for category, reference_text in tasks:
                task_id = f"{index}_{category}"

                # Mark as in progress
                with progress_lock:
                    self.progress_data["in_progress"].append(task_id)

                future = executor.submit(
                    self._verify_category,
                    category, reference_text, full_text, sentences
                )
                future_to_task[future] = (category, reference_text, task_id)

            # Collect results
            for future in as_completed(future_to_task):
                category, reference_text, task_id = future_to_task[future]
                try:
                    result = future.result()

                    # Save result
                    self.save_verification_result(index, article_title, category, reference_text, result)

                    # Update progress
                    self.update_progress(task_id, "completed")

                    # Log result
                    found = "✅" if result.get("found", False) else "❌"
                    match_type = result.get("match_type", "UNKNOWN")
                    print(f"      {found} {category}: {match_type}")

                    results.append(result)

                except Exception as e:
                    error_msg = f"Task error: {str(e)}"
                    print(f"      ❌ {category}: ERROR - {error_msg}")

                    error_result = {
                        "found": False,
                        "match_type": "ERROR",
                        "confidence": 0,
                        "location_description": error_msg,
                        "issue": "PROCESSING_ERROR",
                        "page_numbers": "N/A"
                    }
                    self.save_verification_result(index, article_title, category, reference_text, error_result)
                    self.update_progress(task_id, "failed", error_msg)
                    results.append(error_result)

        return results

    def extract_pdf_chunk(self, pdf_path: Path, start_page: int, end_page: int) -> str:
        """
        Extract text from a specific page range

        Args:
            pdf_path: Path to PDF file
            start_page: Start page (0-indexed)
            end_page: End page (exclusive, 0-indexed)

        Returns:
            Extracted text from the page range
        """
        try:
            chunk_text = []

            with pdfplumber.open(pdf_path) as pdf:
                for page_idx in range(start_page, min(end_page, len(pdf.pages))):
                    page = pdf.pages[page_idx]
                    page_text = page.extract_text()

                    if page_text and page_text.strip():
                        chunk_text.append(f"=== Page {page_idx + 1} ===\n{page_text}")

            full_chunk = "\n\n".join(chunk_text)

            # Clean problematic characters
            full_chunk = full_chunk.replace('\x00', '')  # Remove null bytes

            return full_chunk

        except Exception as e:
            raise RuntimeError(f"Failed to extract chunk from {pdf_path.name}: {str(e)}")

    def verify_with_claude_cli(self, reference_text: str, pdf_chunk: str,
                               page_start: int, page_end: int) -> Dict:
        """
        Verify reference text using Claude CLI

        Args:
            reference_text: Reference text to verify
            pdf_chunk: PDF text chunk to search in
            page_start: Start page number (1-indexed for display)
            page_end: End page number (1-indexed for display)

        Returns:
            Verification result dictionary
        """
        prompt = f"""TASK: Verify if the REFERENCE TEXT appears in the PDF EXCERPT below.

REFERENCE TEXT TO FIND:
\"\"\"
{reference_text}
\"\"\"

PDF EXCERPT (Pages {page_start}-{page_end}):
\"\"\"
{pdf_chunk}
\"\"\"

INSTRUCTIONS:
1. Check if the reference text appears EXACTLY or with minor variations (OCR errors, whitespace, punctuation)
2. Consider these match types:
   - EXACT: Word-for-word match
   - FUZZY: Minor variations (typos, spacing, punctuation)
   - SEMANTIC: Same meaning but paraphrased
   - NONE: Not found or completely different
3. Flag potential issues:
   - HALLUCINATION: Reference text doesn't exist in PDF
   - PARAPHRASE: Reference is a summary/synthesis, not a direct quote
   - OCR_ERROR: PDF has text extraction issues
   - NONE: No issues detected

OUTPUT FORMAT (JSON only, no markdown):
{{
  "found": true/false,
  "match_type": "EXACT/FUZZY/SEMANTIC/NONE",
  "confidence": 0-100,
  "location_description": "brief description of where found or why not found",
  "issue": "NONE/HALLUCINATION/PARAPHRASE/OCR_ERROR"
}}

Return ONLY the JSON object, no additional text."""

        try:
            # Call Claude CLI with JSON output
            result = subprocess.run(
                ["claude", "-p", "--output-format", "json", prompt],
                capture_output=True,
                text=True,
                timeout=60  # 60 second timeout
            )

            if result.returncode != 0:
                return {
                    "found": False,
                    "match_type": "ERROR",
                    "confidence": 0,
                    "location_description": f"Claude CLI error: {result.stderr}",
                    "issue": "HALLUCINATION"  # API 에러 = 검증 실패 = 환각
                }

            # Parse JSON response
            response_text = result.stdout.strip()

            # Claude CLI returns nested JSON: outer JSON has "result" field
            outer_json = json.loads(response_text)

            # Extract the inner result
            inner_result = outer_json.get("result", "")

            # The inner result may be wrapped in markdown code blocks
            if "```json" in inner_result:
                json_start = inner_result.find("```json") + 7
                json_end = inner_result.find("```", json_start)
                inner_result = inner_result[json_start:json_end].strip()
            elif "```" in inner_result:
                json_start = inner_result.find("```") + 3
                json_end = inner_result.find("```", json_start)
                inner_result = inner_result[json_start:json_end].strip()

            # Parse the actual verification result
            verification_result = json.loads(inner_result)

            return verification_result

        except subprocess.TimeoutExpired:
            return {
                "found": False,
                "match_type": "ERROR",
                "confidence": 0,
                "location_description": "Claude CLI timeout (60s)",
                "issue": "TIMEOUT"
            }
        except json.JSONDecodeError as e:
            return {
                "found": False,
                "match_type": "ERROR",
                "confidence": 0,
                "location_description": f"JSON parse error: {str(e)}\nResponse: {response_text[:200]}",
                "issue": "PARSE_ERROR"
            }
        except Exception as e:
            return {
                "found": False,
                "match_type": "ERROR",
                "confidence": 0,
                "location_description": f"Verification error: {str(e)}",
                "issue": "UNKNOWN_ERROR"
            }

    def verify_reference_in_pdf(self, pdf_path: Path, reference_text: str) -> Dict:
        """
        Verify reference text in PDF using 2-stage approach:
        1. Local text search (fast, no API cost)
        2. Claude CLI verification (for semantic matching)

        Args:
            pdf_path: Path to PDF file
            reference_text: Reference text to verify

        Returns:
            Verification result with found status and details
        """
        try:
            # === Stage 1: Local Text Search (Fast, No Cost) ===
            print(f"   🔍 [Stage 1] Local text search...")
            full_text = self._extract_full_pdf_text(pdf_path)

            if full_text:
                local_result = self._local_text_search(reference_text, full_text)

                if local_result.get("found", False):
                    print(f"   ✅ [LOCAL] Found! match_type={local_result.get('match_type')}")
                    return local_result
                else:
                    print(f"   ⚠️  [LOCAL] Not found → proceeding to Claude CLI verification...")
            else:
                print(f"   ⚠️  [LOCAL] PDF text extraction failed → proceeding to Claude CLI...")

            # === Stage 2: Efficient Candidate-based Verification ===
            print(f"   🤖 [Stage 2] Candidate-based Claude CLI verification...")

            # Step 2a: PDF를 문장으로 분리
            print(f"   📄 Splitting PDF into sentences...")
            sentences = self._split_pdf_to_sentences(pdf_path)
            print(f"      Found {len(sentences)} sentences")

            if not sentences:
                print(f"   ❌ No sentences extracted from PDF")
                return {
                    "found": False,
                    "match_type": "NONE",
                    "confidence": 0,
                    "location_description": "No sentences extracted from PDF",
                    "issue": "OCR_ERROR",
                    "page_numbers": "N/A"
                }

            # Step 2b: TF-IDF로 관련 후보 문장 추출
            print(f"   🔍 Extracting candidate sentences (TF-IDF)...")
            candidates = self._extract_candidate_sentences(reference_text, sentences, top_k=20)
            print(f"      Found {len(candidates)} candidates")

            if not candidates:
                print(f"   ❌ No relevant candidates found")
                return {
                    "found": False,
                    "match_type": "NONE",
                    "confidence": 0,
                    "location_description": "No similar sentences found in PDF",
                    "issue": "HALLUCINATION",
                    "page_numbers": "N/A"
                }

            # Step 2c: Claude CLI 1회 호출로 검증
            print(f"   🤖 Verifying with Claude CLI (1 call)...")
            result = self._verify_with_candidates(reference_text, candidates)

            # Log result
            print(f"      Result: found={result.get('found', False)}, "
                  f"match_type={result.get('match_type', 'UNKNOWN')}, "
                  f"confidence={result.get('confidence', 0)}")

            if result.get("found", False):
                print(f"   ✅ Match found!")
            else:
                print(f"   ❌ No match in candidates")

            return result

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return {
                "found": False,
                "match_type": "ERROR",
                "confidence": 0,
                "location_description": f"PDF processing error: {str(e)}",
                "issue": "HALLUCINATION",  # PDF 에러 = 검증 실패 = 환각
                "page_numbers": "N/A"
            }

    def save_verification_result(self, index: str, article_title: str, category: str,
                                 reference_text: str, result: Dict):
        """
        Save verification result to CSV (thread-safe)

        Args:
            index: Paper index
            article_title: Paper title
            category: Category name
            reference_text: Full reference text
            result: Verification result dictionary
        """
        with csv_lock:
            # Create result row
            row = {
                "Index": index,
                "Article_Title": article_title,
                "Category": category,
                "Reference_Text_Preview": reference_text[:100] + "..." if len(reference_text) > 100 else reference_text,
                "Found": "Y" if result.get("found", False) else "N",
                "Page_Numbers": result.get("page_numbers", "N/A"),
                "Match_Confidence": result.get("confidence", 0),
                "Verification_Method": result.get("match_type", "UNKNOWN"),
                "Issue_Type": result.get("issue", "UNKNOWN"),
                "Full_Reference_Text": reference_text,
                "Notes": result.get("location_description", ""),
                "Timestamp": datetime.now().isoformat()
            }

            # Append to CSV
            df = pd.DataFrame([row])
            df.to_csv(VERIFICATION_RESULTS_CSV, mode='a', header=False, index=False)

    def update_progress(self, task_id: str, status: str, error_msg: Optional[str] = None):
        """
        Update progress tracking (thread-safe)

        Args:
            task_id: Task identifier (e.g., "100_Design Discipline")
            status: Status ("completed" or "failed")
            error_msg: Optional error message for failed tasks
        """
        with progress_lock:
            if status == "completed":
                self.progress_data["completed"] += 1
                self.progress_data["completed_tasks"].append(task_id)
                if task_id in self.progress_data["in_progress"]:
                    self.progress_data["in_progress"].remove(task_id)

            elif status == "failed":
                self.progress_data["failed"] += 1
                self.progress_data["failed_tasks"][task_id] = {
                    "error": error_msg,
                    "timestamp": datetime.now().isoformat()
                }
                if task_id in self.progress_data["in_progress"]:
                    self.progress_data["in_progress"].remove(task_id)

            # Save progress to file
            with open(VERIFICATION_PROGRESS_JSON, 'w') as f:
                json.dump(self.progress_data, f, indent=2)

    def process_verification_task(self, task: Tuple[str, str, str, str, Path]) -> Dict:
        """
        Process a single verification task

        Args:
            task: Tuple of (index, article_title, category, reference_text, pdf_path)

        Returns:
            Verification result dictionary
        """
        index, article_title, category, reference_text, pdf_path = task
        task_id = f"{index}_{category}"

        try:
            print(f"\n🔍 [{index}] {category}")
            print(f"   PDF: {pdf_path.name}")
            print(f"   Reference preview: {reference_text[:80]}...")

            # Mark as in progress
            with progress_lock:
                self.progress_data["in_progress"].append(task_id)

            # Verify reference in PDF
            result = self.verify_reference_in_pdf(pdf_path, reference_text)

            # Save result
            self.save_verification_result(index, article_title, category, reference_text, result)

            # Update progress
            self.update_progress(task_id, "completed")

            return result

        except Exception as e:
            error_msg = f"Task processing error: {str(e)}"
            print(f"   ❌ {error_msg}")

            # Save error result
            error_result = {
                "found": False,
                "match_type": "ERROR",
                "confidence": 0,
                "location_description": error_msg,
                "issue": "PROCESSING_ERROR",
                "page_numbers": "N/A"
            }
            self.save_verification_result(index, article_title, category, reference_text, error_result)

            # Update progress
            self.update_progress(task_id, "failed", error_msg)

            return error_result

    def build_task_list(self, index_filter: Optional[List[str]] = None,
                       category_filter: Optional[str] = None) -> List[Tuple]:
        """
        Build list of verification tasks

        Args:
            index_filter: Optional list of paper indices to verify
            category_filter: Optional single category to verify

        Returns:
            List of task tuples
        """
        tasks = []

        for _, row in self.references_df.iterrows():
            index = str(row['Index'])
            article_title = str(row.get('Article Title', ''))

            # Apply index filter
            if index_filter and index not in index_filter:
                continue

            # Find corresponding PDF
            pdf_files = list(PAPERS_DIR.glob(f"{index}_*.pdf"))
            if not pdf_files:
                print(f"⚠️  PDF not found for index {index}")
                continue

            pdf_path = pdf_files[0]

            # Process each category
            for category in CATEGORIES:
                # Apply category filter
                if category_filter and category != category_filter:
                    continue

                reference_text = str(row.get(category, ''))

                # Skip if no reference text
                if not reference_text or reference_text.strip() == '' or reference_text == 'nan':
                    continue

                tasks.append((index, article_title, category, reference_text, pdf_path))

        return tasks

    def run_verification(self, index_filter: Optional[List[str]] = None,
                        category_filter: Optional[str] = None,
                        dry_run: bool = False):
        """
        Run verification process

        Args:
            index_filter: Optional list of paper indices to verify
            category_filter: Optional single category to verify
            dry_run: If True, only list tasks without executing
        """
        # Build task list
        tasks = self.build_task_list(index_filter, category_filter)

        if not tasks:
            print("❌ No tasks to process!")
            return

        self.progress_data["total_tasks"] = len(tasks)

        print(f"\n{'='*60}")
        print(f"📋 REFERENCE TEXT VERIFICATION")
        print(f"{'='*60}")
        print(f"Total tasks: {len(tasks)}")
        print(f"Workers: {self.workers}")
        print(f"Chunk size: {self.chunk_size} pages (with {self.overlap}-page overlap)")
        print(f"Results will be saved to: {VERIFICATION_RESULTS_CSV}")
        print(f"{'='*60}\n")

        if dry_run:
            print("🔍 DRY RUN - Listing tasks only:\n")
            for i, (index, title, category, ref_text, pdf_path) in enumerate(tasks, 1):
                print(f"{i}. [{index}] {category}")
                print(f"   PDF: {pdf_path.name}")
                print(f"   Reference: {ref_text[:80]}...")
                print()
            return

        # === v3: 논문 단위 그룹핑 + 카테고리 병렬 처리 ===
        start_time = time.time()

        # Step 1: 논문별로 tasks 그룹핑
        papers = {}  # {index: {"title": str, "pdf_path": Path, "categories": [(cat, ref_text), ...]}}
        for index, article_title, category, reference_text, pdf_path in tasks:
            if index not in papers:
                papers[index] = {
                    "title": article_title,
                    "pdf_path": pdf_path,
                    "categories": []
                }
            papers[index]["categories"].append((category, reference_text))

        print(f"\n📊 Grouped into {len(papers)} papers")
        print(f"   (Each paper will process categories in parallel)")

        # Step 2: 논문 단위로 병렬 처리
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            future_to_paper = {}

            for index, paper_data in papers.items():
                future = executor.submit(
                    self.process_paper_with_cache,
                    index,
                    paper_data["title"],
                    paper_data["pdf_path"],
                    paper_data["categories"]
                )
                future_to_paper[future] = index

            # Process completed papers
            for future in as_completed(future_to_paper):
                paper_index = future_to_paper[future]
                try:
                    results = future.result()

                    # Progress update
                    completed = self.progress_data["completed"]
                    failed = self.progress_data["failed"]
                    total = self.progress_data["total_tasks"]

                    print(f"\n{'='*60}")
                    print(f"📈 Overall Progress: {completed + failed}/{total} ({(completed + failed) / total * 100:.1f}%)")
                    print(f"   ✅ Completed: {completed} | ❌ Failed: {failed}")
                    print(f"{'='*60}")

                except Exception as e:
                    print(f"❌ Paper [{paper_index}] unexpected error: {str(e)}")

        elapsed_time = time.time() - start_time

        # Final summary
        self.print_summary(elapsed_time)

    def print_summary(self, elapsed_time: float):
        """Print verification summary"""
        print(f"\n{'='*60}")
        print(f"🎯 VERIFICATION COMPLETE")
        print(f"{'='*60}")
        print(f"Total tasks: {self.progress_data['total_tasks']}")
        print(f"✅ Completed: {self.progress_data['completed']}")
        print(f"❌ Failed: {self.progress_data['failed']}")
        print(f"⏱️  Time elapsed: {elapsed_time:.1f} seconds ({elapsed_time/60:.1f} minutes)")
        print(f"\n📊 Results saved to:")
        print(f"   {VERIFICATION_RESULTS_CSV}")
        print(f"   {VERIFICATION_PROGRESS_JSON}")

        # Load results for analysis
        if VERIFICATION_RESULTS_CSV.exists():
            results_df = pd.read_csv(VERIFICATION_RESULTS_CSV)

            print(f"\n📈 RESULTS BREAKDOWN:")
            print(f"   Found (Y): {len(results_df[results_df['Found'] == 'Y'])}")
            print(f"   Not Found (N): {len(results_df[results_df['Found'] == 'N'])}")

            print(f"\n🔍 VERIFICATION METHODS:")
            method_counts = results_df['Verification_Method'].value_counts()
            for method, count in method_counts.items():
                print(f"   {method}: {count}")

            print(f"\n⚠️  ISSUE TYPES:")
            issue_counts = results_df['Issue_Type'].value_counts()
            for issue, count in issue_counts.items():
                print(f"   {issue}: {count}")

        print(f"{'='*60}\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Verify reference texts against original PDFs"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=5,
        help="Number of parallel workers (default: 5)"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=5,
        help="Number of pages per chunk with 1-page overlap (default: 5)"
    )
    parser.add_argument(
        "--index",
        type=str,
        help="Comma-separated list of paper indices to verify (e.g., '100,101,102')"
    )
    parser.add_argument(
        "--category",
        type=str,
        choices=CATEGORIES,
        help="Single category to verify"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List tasks without executing"
    )
    parser.add_argument(
        "--source",
        type=str,
        choices=["csv", "sheets"],
        default="csv",
        help="Data source: 'csv' for J's papers (pdf_references.csv), 'sheets' for M's papers (Google Sheets notes)"
    )

    args = parser.parse_args()

    # Parse index filter
    index_filter = None
    if args.index:
        index_filter = [idx.strip() for idx in args.index.split(',')]

    # Create verifier
    verifier = ReferenceVerifier(workers=args.workers, chunk_size=args.chunk_size, source=args.source)

    # Run verification
    verifier.run_verification(
        index_filter=index_filter,
        category_filter=args.category,
        dry_run=args.dry_run
    )


if __name__ == "__main__":
    main()
