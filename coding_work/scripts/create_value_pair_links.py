#!/usr/bin/env python3
"""Build row-level Enhanced -> Impaired value co-occurrence links."""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from zipfile import ZipFile


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKBOOK = REPO_ROOT / "Value.xlsx"
OUTPUTS = [
    REPO_ROOT / "docs" / "value_pair_links.json",
    REPO_ROOT / "coding_work" / "results" / "value_pair_links.json",
]

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

VALUE_ORDER = [
    "Efficiency",
    "Learning/Skills development",
    "Accuracy",
    "Context appropriateness",
    "Creativity",
    "User-centredness",
    "Collaboration",
    "Feasibility",
    "Controllability",
    "Scalability",
    "AI-Literacy (Trust)",
    "Authenticity",
    "Affordability",
    "Other",
]

VALUE_MAP = {
    "Efficiency": "Efficiency",
    "Accuracy": "Accuracy",
    "Creativity": "Creativity",
    "Learning": "Learning/Skills development",
    "Skills Development": "Learning/Skills development",
    "Skills development": "Learning/Skills development",
    "Learning / Skills Development": "Learning/Skills development",
    "Learning (Gaining insigts)": "Learning/Skills development",
    "Context awareness": "Context appropriateness",
    "Context Awareness": "Context appropriateness",
    "Context Appropriateness": "Context appropriateness",
    "Collaboration": "Collaboration",
    "Feasibility": "Feasibility",
    "Feasibiltiy": "Feasibility",
    "Controllability": "Controllability",
    "Scalability": "Scalability",
    "Human-cnetredness": "User-centredness",
    "User-centeredness": "User-centredness",
    "Empathy": "User-centredness",
    "Empathy (Human-centredness)": "User-centredness",
    "AI-Literacy (Trust)": "AI-Literacy (Trust)",
    "Trust": "AI-Literacy (Trust)",
    "Authenticity": "Authenticity",
    "Affordability": "Affordability",
    "Intuition": "Other",
}


def clean(value: object) -> str:
    return str(value or "").replace("\u00a0", " ").strip()


def normalize_value(value: object) -> str:
    text = clean(value)
    if not text:
        return ""
    if text not in VALUE_MAP:
        raise ValueError(f"Unmapped value label: {text}")
    return VALUE_MAP[text]


def col_to_idx(cell_ref: str) -> int:
    letters = re.sub(r"[^A-Za-z]", "", cell_ref)
    idx = 0
    for char in letters:
        idx = idx * 26 + ord(char.upper()) - 64
    return idx


def load_shared_strings(zip_file: ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in zip_file.namelist():
        return []
    root = ET.fromstring(zip_file.read("xl/sharedStrings.xml"))
    return [
        "".join(text.text or "" for text in item.iter(f"{NS}t"))
        for item in root.findall(f"{NS}si")
    ]


def cell_value(cell: ET.Element, shared_strings: list[str]) -> str:
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        return "".join(text.text or "" for text in cell.iter(f"{NS}t"))
    value = cell.find(f"{NS}v")
    if value is None:
        return ""
    if cell_type == "s":
        return shared_strings[int(value.text or 0)]
    return value.text or ""


def read_rows() -> list[tuple[int, dict[int, str]]]:
    with ZipFile(WORKBOOK) as zip_file:
        shared_strings = load_shared_strings(zip_file)
        root = ET.fromstring(zip_file.read("xl/worksheets/sheet1.xml"))
        rows: list[tuple[int, dict[int, str]]] = []
        for row in root.findall(f".//{NS}row"):
            cells = {
                col_to_idx(cell.attrib["r"]): cell_value(cell, shared_strings)
                for cell in row.findall(f"{NS}c")
            }
            rows.append((int(row.attrib["r"]), cells))
        return rows


def build_data() -> dict[str, object]:
    rows = read_rows()
    pair_counts: Counter[tuple[str, str]] = Counter()
    source_rows = 0
    rows_with_enhanced = 0
    rows_with_impaired = 0
    rows_with_both = 0

    for _, row in rows[1:]:
        if not any(clean(row.get(col)) for col in range(1, 18)):
            continue
        source_rows += 1
        enhanced = list(
            dict.fromkeys(
                value
                for value in (normalize_value(row.get(13)), normalize_value(row.get(14)))
                if value
            )
        )
        impaired = list(
            dict.fromkeys(
                value
                for value in (normalize_value(row.get(15)), normalize_value(row.get(16)))
                if value
            )
        )
        rows_with_enhanced += bool(enhanced)
        rows_with_impaired += bool(impaired)
        if not (enhanced and impaired):
            continue
        rows_with_both += 1
        for enhanced_value in enhanced:
            for impaired_value in impaired:
                pair_counts[(enhanced_value, impaired_value)] += 1

    order = {value: idx for idx, value in enumerate(VALUE_ORDER)}
    enhanced_totals: Counter[str] = Counter()
    impaired_totals: Counter[str] = Counter()
    for (enhanced, impaired), count in pair_counts.items():
        enhanced_totals[enhanced] += count
        impaired_totals[impaired] += count

    nodes = [
        {
            "name": f"Enhanced · {value}",
            "label": value,
            "side": "enhanced",
            "total": enhanced_totals[value],
        }
        for value in VALUE_ORDER
        if enhanced_totals[value]
    ] + [
        {
            "name": f"Impaired · {value}",
            "label": value,
            "side": "impaired",
            "total": impaired_totals[value],
        }
        for value in VALUE_ORDER
        if impaired_totals[value]
    ]

    links = [
        {
            "source": f"Enhanced · {enhanced}",
            "target": f"Impaired · {impaired}",
            "enhanced": enhanced,
            "impaired": impaired,
            "value": count,
        }
        for (enhanced, impaired), count in sorted(
            pair_counts.items(),
            key=lambda item: (
                order[item[0][0]],
                order[item[0][1]],
            ),
        )
    ]
    top_pairs = sorted(
        links,
        key=lambda item: (-item["value"], order[item["enhanced"]], order[item["impaired"]]),
    )[:8]

    return {
        "source": WORKBOOK.name,
        "sheet": "Sheet1",
        "sourceRows": source_rows,
        "rowsWithEnhanced": rows_with_enhanced,
        "rowsWithImpaired": rows_with_impaired,
        "rowsWithBoth": rows_with_both,
        "pairOccurrences": sum(pair_counts.values()),
        "uniquePairs": len(pair_counts),
        "pairingRule": "Within each source row, every distinct Enhanced Value 1/2 is paired with every distinct Impaired Value 1/2.",
        "nodes": nodes,
        "links": links,
        "topPairs": top_pairs,
    }


def main() -> None:
    data = build_data()
    rendered = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    for output in OUTPUTS:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(
        f"Created {len(data['links'])} unique links from "
        f"{data['pairOccurrences']} pair occurrences across {data['rowsWithBoth']} rows."
    )


if __name__ == "__main__":
    main()
