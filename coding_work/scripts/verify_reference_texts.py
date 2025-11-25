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

    def __init__(self, workers: int = 5, chunk_size: int = 5):
        """
        Initialize the verifier

        Args:
            workers: Number of parallel workers
            chunk_size: Number of pages per chunk (default: 5)
        """
        self.workers = workers
        self.chunk_size = chunk_size
        self.overlap = 1  # 1 page overlap between chunks
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
        """Load reference texts from CSV"""
        if not PDF_REFERENCES_CSV.exists():
            raise FileNotFoundError(f"References CSV not found: {PDF_REFERENCES_CSV}")

        print(f"📂 Loading reference data from: {PDF_REFERENCES_CSV}")
        self.references_df = pd.read_csv(PDF_REFERENCES_CSV)
        print(f"✅ Loaded {len(self.references_df)} papers with reference texts")

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
        Verify reference text in PDF using 2-page chunking

        Args:
            pdf_path: Path to PDF file
            reference_text: Reference text to verify

        Returns:
            Verification result with found status and details
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)

            print(f"   📄 Scanning {total_pages} pages in {self.chunk_size}-page chunks (1-page overlap)...")

            # Iterate through PDF in chunks with overlap
            # Step size = chunk_size - overlap (e.g., 5 pages - 1 overlap = step by 4)
            step = self.chunk_size - self.overlap

            for start_page in range(0, total_pages, step):
                end_page = min(start_page + self.chunk_size, total_pages)

                print(f"   🔎 Checking pages {start_page + 1}-{end_page}...")

                # Extract chunk
                chunk_text = self.extract_pdf_chunk(pdf_path, start_page, end_page)

                if not chunk_text.strip():
                    print(f"      ⚠️  Empty chunk, skipping")
                    continue

                # Verify with Claude CLI
                result = self.verify_with_claude_cli(
                    reference_text,
                    chunk_text,
                    start_page + 1,  # 1-indexed for display
                    end_page
                )

                # Log result for this chunk
                print(f"      Result: found={result.get('found', False)}, "
                      f"match_type={result.get('match_type', 'UNKNOWN')}, "
                      f"confidence={result.get('confidence', 0)}")

                # If found, return immediately (early exit)
                if result.get("found", False):
                    result["page_numbers"] = f"{start_page + 1}-{end_page}"
                    print(f"   ✅ Found on pages {result['page_numbers']}")
                    return result

            # Not found in any chunk
            print(f"   ❌ Not found in any chunk")
            return {
                "found": False,
                "match_type": "NONE",
                "confidence": 0,
                "location_description": f"Searched all {total_pages} pages in {self.chunk_size}-page chunks",
                "issue": "HALLUCINATION",  # 원문에 없으면 환각!
                "page_numbers": "N/A"
            }

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

        # Process tasks in parallel
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(self.process_verification_task, task): task
                for task in tasks
            }

            # Process completed tasks
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()

                    # Progress update
                    completed = self.progress_data["completed"]
                    failed = self.progress_data["failed"]
                    total = self.progress_data["total_tasks"]

                    print(f"\n{'='*60}")
                    print(f"Progress: {completed + failed}/{total} ({(completed + failed) / total * 100:.1f}%)")
                    print(f"✅ Completed: {completed} | ❌ Failed: {failed}")
                    print(f"{'='*60}")

                except Exception as e:
                    print(f"❌ Unexpected error: {str(e)}")

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

    args = parser.parse_args()

    # Parse index filter
    index_filter = None
    if args.index:
        index_filter = [idx.strip() for idx in args.index.split(',')]

    # Create verifier
    verifier = ReferenceVerifier(workers=args.workers, chunk_size=args.chunk_size)

    # Run verification
    verifier.run_verification(
        index_filter=index_filter,
        category_filter=args.category,
        dry_run=args.dry_run
    )


if __name__ == "__main__":
    main()
