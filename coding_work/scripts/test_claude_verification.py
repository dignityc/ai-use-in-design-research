#!/usr/bin/env python3
"""
Quick test of Claude CLI verification for debugging
"""

import subprocess
import json
import pdfplumber
from pathlib import Path

# Test with paper 167
pdf_path = Path("../../Papers/167_Optimizing HMI for Intelligent Electric Vehicles Using BCI and Deep Neural Networks with Genetic Algorithms.pdf")

# Extract first 2 pages
with pdfplumber.open(pdf_path) as pdf:
    chunk_text = ""
    for i in range(2):
        chunk_text += pdf.pages[i].extract_text()

# Clean
chunk_text = chunk_text.replace('\x00', '')

# Reference text to find
reference_text = """This study utilizes a brain—computer interface (BCI)—based deep neural network (DNN) and genetic algorithm (GA) method."""

# Create prompt
prompt = f"""TASK: Verify if the REFERENCE TEXT appears in the PDF EXCERPT below.

REFERENCE TEXT TO FIND:
\"\"\"
{reference_text}
\"\"\"

PDF EXCERPT (Pages 1-2):
\"\"\"
{chunk_text[:3000]}
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

print("=== CALLING CLAUDE CLI ===\n")

# Call Claude CLI
result = subprocess.run(
    ["claude", "-p", "--output-format", "json", prompt],
    capture_output=True,
    text=True,
    timeout=60
)

print(f"Return code: {result.returncode}")
print(f"\n=== STDOUT ===")
print(result.stdout)
print(f"\n=== STDERR ===")
print(result.stderr)

# Try to parse
try:
    response_text = result.stdout.strip()

    # Extract JSON from markdown if present
    if "```json" in response_text:
        json_start = response_text.find("```json") + 7
        json_end = response_text.find("```", json_start)
        response_text = response_text[json_start:json_end].strip()
    elif "```" in response_text:
        json_start = response_text.find("```") + 3
        json_end = response_text.find("```", json_start)
        response_text = response_text[json_start:json_end].strip()

    parsed = json.loads(response_text)

    print(f"\n=== PARSED JSON ===")
    print(json.dumps(parsed, indent=2))

except Exception as e:
    print(f"\n=== PARSE ERROR ===")
    print(f"Error: {e}")
