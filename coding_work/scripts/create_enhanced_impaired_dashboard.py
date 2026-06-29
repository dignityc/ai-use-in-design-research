#!/usr/bin/env python3
"""Create an interactive Enhanced vs Impaired value comparison dashboard."""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
WORKBOOK = ROOT / "00_Final.xlsx"
OUTPUT = ROOT / "results" / "enhanced_impaired_value_comparison.html"

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

VALUE_BUCKETS = [
    "AI-Literacy (Trust)",
    "Authenticity",
    "Affordability",
    "Efficiency",
    "Controllability",
    "Collaboration",
    "Learning/Skills development",
    "Accuracy",
    "Context appropriateness",
    "Creativity",
    "Scalability",
    "Feasibility",
    "User-centredness",
    "Other",
]

DIMENSIONS = [
    "Background Research & Sensemaking",
    "Ideation & Design Generation",
    "Design & Process Evaluation",
    "Planning, Coordination & Management",
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
        "".join(text.text or "" for text in shared.iter(f"{NS}t"))
        for shared in root.findall(f"{NS}si")
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


def read_sheet(zip_file: ZipFile, sheet_xml: str) -> list[tuple[int, dict[int, str]]]:
    shared_strings = load_shared_strings(zip_file)
    root = ET.fromstring(zip_file.read(sheet_xml))
    rows: list[tuple[int, dict[int, str]]] = []
    for row in root.findall(f".//{NS}row"):
        cells: dict[int, str] = {}
        for cell in row.findall(f"{NS}c"):
            cells[col_to_idx(cell.attrib["r"])] = cell_value(cell, shared_strings)
        rows.append((int(row.attrib["r"]), cells))
    return rows


def normalize_discipline(value: object) -> str:
    text = clean(value)
    if text == "Product Engineering":
        return "ED"
    if text.startswith("Service"):
        return "SD"
    if text.startswith("UIUX"):
        return "UIUX"
    return ""


def normalize_value(value: object) -> str:
    text = clean(value)
    if not text:
        return ""
    if text not in VALUE_MAP:
        raise ValueError(f"Unmapped value label: {text}")
    return VALUE_MAP[text]


def read_final_rows() -> list[tuple[int, dict[int, str]]]:
    with ZipFile(WORKBOOK) as zip_file:
        return read_sheet(zip_file, "xl/worksheets/sheet2.xml")


def build_data() -> dict[str, object]:
    rows = read_final_rows()
    totals = {
        bucket: {"value": bucket, "enhanced": 0, "impaired": 0, "total": 0, "net": 0}
        for bucket in VALUE_BUCKETS
    }
    dimension_value = {
        dimension: {
            bucket: {"enhanced": 0, "impaired": 0, "net": 0, "total": 0}
            for bucket in VALUE_BUCKETS
        }
        for dimension in DIMENSIONS
    }
    dimension_totals = {
        dimension: {"dimension": dimension, "enhanced": 0, "impaired": 0, "total": 0, "net": 0}
        for dimension in DIMENSIONS
    }
    discipline_totals = {
        discipline: {"discipline": discipline, "enhanced": 0, "impaired": 0, "total": 0, "net": 0}
        for discipline in ["ED", "SD", "UIUX"]
    }

    excluded_rows: list[int] = []
    source_rows = 0
    eligible_rows = 0

    for excel_row, row in rows[1:]:
        if not any(clean(row.get(col)) for col in range(1, 18)):
            continue
        source_rows += 1
        dimension = clean(row.get(8))
        phase = clean(row.get(3))
        discipline = normalize_discipline(row.get(2))
        if not (dimension and phase and discipline):
            excluded_rows.append(excel_row)
            continue
        eligible_rows += 1

        for raw in (row.get(13), row.get(14)):
            bucket = normalize_value(raw)
            if not bucket:
                continue
            totals[bucket]["enhanced"] += 1
            totals[bucket]["total"] += 1
            dimension_value[dimension][bucket]["enhanced"] += 1
            dimension_value[dimension][bucket]["total"] += 1
            dimension_totals[dimension]["enhanced"] += 1
            dimension_totals[dimension]["total"] += 1
            discipline_totals[discipline]["enhanced"] += 1
            discipline_totals[discipline]["total"] += 1

        for raw in (row.get(15), row.get(16)):
            bucket = normalize_value(raw)
            if not bucket:
                continue
            totals[bucket]["impaired"] += 1
            totals[bucket]["total"] += 1
            dimension_value[dimension][bucket]["impaired"] += 1
            dimension_value[dimension][bucket]["total"] += 1
            dimension_totals[dimension]["impaired"] += 1
            dimension_totals[dimension]["total"] += 1
            discipline_totals[discipline]["impaired"] += 1
            discipline_totals[discipline]["total"] += 1

    for item in totals.values():
        item["net"] = item["enhanced"] - item["impaired"]
        item["shareEnhanced"] = item["enhanced"] / item["total"] if item["total"] else 0
    for dimension in DIMENSIONS:
        dimension_totals[dimension]["net"] = (
            dimension_totals[dimension]["enhanced"] - dimension_totals[dimension]["impaired"]
        )
        for bucket in VALUE_BUCKETS:
            item = dimension_value[dimension][bucket]
            item["net"] = item["enhanced"] - item["impaired"]
    for item in discipline_totals.values():
        item["net"] = item["enhanced"] - item["impaired"]

    by_value = sorted(totals.values(), key=lambda item: item["total"], reverse=True)
    return {
        "sourceRows": source_rows,
        "eligibleRows": eligible_rows,
        "excludedRows": excluded_rows,
        "enhancedTotal": sum(item["enhanced"] for item in totals.values()),
        "impairedTotal": sum(item["impaired"] for item in totals.values()),
        "combinedTotal": sum(item["total"] for item in totals.values()),
        "values": by_value,
        "valueOrder": [item["value"] for item in by_value],
        "dimensions": list(dimension_totals.values()),
        "disciplines": list(discipline_totals.values()),
        "dimensionValue": dimension_value,
    }


def html_template(data: dict[str, object]) -> str:
    data_json = json.dumps(data, ensure_ascii=False)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Enhanced vs Impaired Value Comparison</title>
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Crect width='16' height='16' rx='3' fill='%232754c5'/%3E%3Cpath d='M4 9h8v2H4zM4 5h5v2H4z' fill='white'/%3E%3C/svg%3E" />
  <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
  <style>
    :root {{
      --ink: #172033;
      --muted: #667085;
      --line: #d8dee9;
      --panel: #ffffff;
      --page: #f5f7fb;
      --green: #1f8a4c;
      --green-soft: #dff4e8;
      --red: #c43131;
      --red-soft: #f9dfdf;
      --blue: #2754c5;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--page);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      letter-spacing: 0;
    }}
    .shell {{
      max-width: 1480px;
      margin: 0 auto;
      padding: 28px;
    }}
    header {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 20px;
      align-items: end;
      margin-bottom: 18px;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 30px;
      line-height: 1.1;
      font-weight: 760;
    }}
    .sub {{
      max-width: 940px;
      margin: 0;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.55;
    }}
    .toolbar {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      padding: 8px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
    }}
    .toolbar-note {{
      flex-basis: 100%;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.35;
      padding: 0 2px 2px;
    }}
    select, button {{
      height: 34px;
      border-radius: 6px;
      border: 1px solid #cfd6e3;
      background: #fff;
      color: var(--ink);
      padding: 0 10px;
      font: inherit;
      font-size: 13px;
    }}
    button {{
      cursor: pointer;
      font-weight: 650;
    }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 14px;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px 16px;
      min-height: 86px;
    }}
    .label {{
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
    }}
    .metric {{
      margin-top: 8px;
      font-size: 28px;
      font-weight: 760;
      line-height: 1;
    }}
    .metric.green {{ color: var(--green); }}
    .metric.red {{ color: var(--red); }}
    .metric.blue {{ color: var(--blue); }}
    .note {{
      margin-top: 8px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.35;
    }}
    .grid {{
      display: grid;
      grid-template-columns: minmax(0, 1.1fr) minmax(420px, .9fr);
      gap: 14px;
    }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
    }}
    .panel-head {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      padding: 13px 16px;
      border-bottom: 1px solid var(--line);
      background: #fbfcff;
    }}
    .panel-title {{
      margin: 0;
      font-size: 15px;
      font-weight: 760;
    }}
    .panel-title-row {{
      display: flex;
      align-items: center;
      gap: 8px;
      min-width: 0;
    }}
    .panel-caption {{
      color: var(--muted);
      font-size: 12px;
      text-align: right;
    }}
    .scope-badge {{
      display: inline-flex;
      align-items: center;
      height: 22px;
      padding: 0 8px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 760;
      line-height: 1;
      border: 1px solid transparent;
      white-space: nowrap;
    }}
    .scope-badge.filtered {{
      color: #166534;
      background: #dcfce7;
      border-color: #bbf7d0;
    }}
    .scope-badge.global {{
      color: #334155;
      background: #e2e8f0;
      border-color: #cbd5e1;
    }}
    .chart {{
      width: 100%;
      height: 430px;
    }}
    .wide {{
      grid-column: 1 / -1;
    }}
    .wide .chart {{
      height: 480px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}
    th, td {{
      padding: 9px 10px;
      border-bottom: 1px solid #edf0f5;
      text-align: right;
      white-space: nowrap;
    }}
    th:first-child, td:first-child {{
      text-align: left;
      white-space: normal;
    }}
    th {{
      color: var(--muted);
      font-size: 12px;
      background: #fbfcff;
    }}
    .table-wrap {{
      max-height: 430px;
      overflow: auto;
    }}
    .pos {{ color: var(--green); font-weight: 700; }}
    .neg {{ color: var(--red); font-weight: 700; }}
    @media (max-width: 1050px) {{
      header, .grid, .cards {{ grid-template-columns: 1fr; }}
      .toolbar {{ align-items: stretch; flex-direction: column; }}
      select, button {{ width: 100%; }}
      .chart, .wide .chart {{ height: 390px; }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <header>
      <div>
        <h1>Enhanced vs Impaired Value Comparison</h1>
        <p class="sub">Interactive dashboard generated from <strong>00_Final.xlsx</strong>. Enhanced Value 1/2 and Impaired Value 1/2 are normalized into shared value buckets, then compared across value dimensions and aggregated design dimensions.</p>
      </div>
      <div class="toolbar">
        <select id="dimensionFilter" aria-label="Dimension filter">
          <option value="All">All dimensions</option>
        </select>
        <button id="resetBtn" type="button">Reset View</button>
        <div class="toolbar-note">Filter changes panels marked <strong>Filtered</strong>. Panels marked <strong>Global</strong> stay fixed for whole-dataset context.</div>
      </div>
    </header>

    <section class="cards">
      <div class="card"><div class="label">Rows Used</div><div class="metric blue" id="eligibleRows"></div><div class="note" id="rowNote"></div></div>
      <div class="card"><div class="label">Enhanced Counts</div><div class="metric green" id="enhancedTotal"></div><div class="note">Positive value mentions</div></div>
      <div class="card"><div class="label">Impaired Counts</div><div class="metric red" id="impairedTotal"></div><div class="note">Negative value mentions</div></div>
      <div class="card"><div class="label">Net Balance</div><div class="metric" id="netTotal"></div><div class="note">Enhanced minus impaired</div></div>
    </section>

    <main class="grid">
      <section class="panel wide">
        <div class="panel-head"><div class="panel-title-row"><h2 class="panel-title">Diverging Value Balance</h2><span class="scope-badge filtered">Filtered</span></div><div class="panel-caption">Changes with dimension filter</div></div>
        <div id="divergingChart" class="chart"></div>
      </section>
      <section class="panel">
        <div class="panel-head"><div class="panel-title-row"><h2 class="panel-title">Difference Heatmap</h2><span class="scope-badge global">Global</span></div><div class="panel-caption">Fixed: all dimensions, enhanced - impaired</div></div>
        <div id="heatmapChart" class="chart"></div>
      </section>
      <section class="panel">
        <div class="panel-head"><div class="panel-title-row"><h2 class="panel-title">Trade-off Scatter</h2><span class="scope-badge filtered">Filtered</span></div><div class="panel-caption">Changes with dimension filter</div></div>
        <div id="scatterChart" class="chart"></div>
      </section>
      <section class="panel">
        <div class="panel-head"><div class="panel-title-row"><h2 class="panel-title">Design Dimension Totals</h2><span class="scope-badge global">Global</span></div><div class="panel-caption">Fixed: whole-dataset context</div></div>
        <div id="dimensionChart" class="chart"></div>
      </section>
      <section class="panel">
        <div class="panel-head"><div class="panel-title-row"><h2 class="panel-title">Value Summary Table</h2><span class="scope-badge filtered">Filtered</span></div><div class="panel-caption">Changes with dimension filter</div></div>
        <div class="table-wrap"><table id="summaryTable"></table></div>
      </section>
    </main>
  </div>
  <script>
    const DATA = {data_json};
    const COLORS = {{
      green: '#1f8a4c',
      greenSoft: '#dff4e8',
      red: '#c43131',
      redSoft: '#f9dfdf',
      blue: '#2754c5',
      text: '#172033',
      muted: '#667085'
    }};

    const charts = {{
      diverging: echarts.init(document.getElementById('divergingChart')),
      heatmap: echarts.init(document.getElementById('heatmapChart')),
      scatter: echarts.init(document.getElementById('scatterChart')),
      dimension: echarts.init(document.getElementById('dimensionChart'))
    }};
    const DIM_LABELS = {{
      'Background Research & Sensemaking': 'Background Research',
      'Ideation & Design Generation': 'Ideation & Generation',
      'Design & Process Evaluation': 'Design Evaluation',
      'Planning, Coordination & Management': 'Planning & Management'
    }};
    const shortDimension = name => DIM_LABELS[name] || name;

    const format = new Intl.NumberFormat('en-US');
    document.getElementById('eligibleRows').textContent = format.format(DATA.eligibleRows);
    document.getElementById('enhancedTotal').textContent = format.format(DATA.enhancedTotal);
    document.getElementById('impairedTotal').textContent = format.format(DATA.impairedTotal);
    const net = DATA.enhancedTotal - DATA.impairedTotal;
    const netEl = document.getElementById('netTotal');
    netEl.textContent = `${{net >= 0 ? '+' : ''}}${{format.format(net)}}`;
    netEl.className = `metric ${{net >= 0 ? 'green' : 'red'}}`;
    document.getElementById('rowNote').textContent = `${{DATA.sourceRows}} source rows; excluded rows: ${{DATA.excludedRows.join(', ') || 'none'}}`;

    const filter = document.getElementById('dimensionFilter');
    Object.keys(DATA.dimensionValue).forEach(name => {{
      const option = document.createElement('option');
      option.value = name;
      option.textContent = name;
      filter.appendChild(option);
    }});

    function currentValues() {{
      const selected = filter.value;
      if (selected === 'All') return DATA.values;
      return DATA.valueOrder.map(value => {{
        const d = DATA.dimensionValue[selected][value];
        return {{
          value,
          enhanced: d.enhanced,
          impaired: d.impaired,
          total: d.total,
          net: d.net,
          shareEnhanced: d.total ? d.enhanced / d.total : 0
        }};
      }}).sort((a, b) => b.total - a.total);
    }}

    function renderDiverging(values) {{
      const labels = values.map(d => d.value).reverse();
      charts.diverging.setOption({{
        grid: {{ left: 190, right: 42, top: 28, bottom: 34 }},
        tooltip: {{
          trigger: 'axis',
          axisPointer: {{ type: 'shadow' }},
          formatter: params => {{
            const row = values.find(v => v.value === params[0].axisValue);
            return `<b>${{row.value}}</b><br/>Enhanced: ${{row.enhanced}}<br/>Impaired: ${{row.impaired}}<br/>Net: ${{row.net >= 0 ? '+' : ''}}${{row.net}}`;
          }}
        }},
        legend: {{ top: 0, right: 10 }},
        xAxis: {{
          type: 'value',
          axisLabel: {{ formatter: value => Math.abs(value) }},
          splitLine: {{ lineStyle: {{ color: '#eef2f7' }} }}
        }},
        yAxis: {{ type: 'category', data: labels, axisLabel: {{ color: COLORS.text }} }},
        series: [
          {{
            name: 'Impaired',
            type: 'bar',
            stack: 'balance',
            data: values.map(d => -d.impaired).reverse(),
            itemStyle: {{ color: COLORS.red }},
            barWidth: 16
          }},
          {{
            name: 'Enhanced',
            type: 'bar',
            stack: 'balance',
            data: values.map(d => d.enhanced).reverse(),
            itemStyle: {{ color: COLORS.green }},
            barWidth: 16
          }}
        ]
      }});
    }}

    function renderHeatmap() {{
      const dims = Object.keys(DATA.dimensionValue);
      const values = DATA.valueOrder;
      const points = [];
      dims.forEach((dimension, y) => {{
        values.forEach((value, x) => {{
          points.push([x, y, DATA.dimensionValue[dimension][value].net]);
        }});
      }});
      charts.heatmap.setOption({{
        grid: {{ left: 150, right: 20, top: 24, bottom: 116 }},
        tooltip: {{
          formatter: item => {{
            const value = values[item.value[0]];
            const dimension = dims[item.value[1]];
            const d = DATA.dimensionValue[dimension][value];
            return `<b>${{value}}</b><br/>${{dimension}}<br/>Enhanced: ${{d.enhanced}}<br/>Impaired: ${{d.impaired}}<br/>Net: ${{d.net >= 0 ? '+' : ''}}${{d.net}}`;
          }}
        }},
        xAxis: {{ type: 'category', data: values, axisLabel: {{ rotate: 45, interval: 0, color: COLORS.text }} }},
        yAxis: {{ type: 'category', data: dims.map(shortDimension), axisLabel: {{ color: COLORS.text }} }},
        visualMap: {{
          min: -15,
          max: 15,
          calculable: true,
          orient: 'horizontal',
          left: 'center',
          bottom: 12,
          inRange: {{ color: ['#b91c1c', '#ffffff', '#1f8a4c'] }}
        }},
        series: [{{
          type: 'heatmap',
          data: points,
          label: {{ show: true, formatter: p => p.value[2] ? p.value[2] : '', color: COLORS.text }},
          emphasis: {{ itemStyle: {{ borderColor: '#111827', borderWidth: 1 }} }}
        }}]
      }});
    }}

    function renderScatter(values) {{
      charts.scatter.setOption({{
        grid: {{ left: 58, right: 24, top: 20, bottom: 48 }},
        tooltip: {{
          formatter: item => {{
            const d = item.data;
            return `<b>${{d[3]}}</b><br/>Enhanced: ${{d[0]}}<br/>Impaired: ${{d[1]}}<br/>Total: ${{d[2]}}<br/>Net: ${{d[4] >= 0 ? '+' : ''}}${{d[4]}}`;
          }}
        }},
        xAxis: {{ name: 'Enhanced', nameLocation: 'middle', nameGap: 30, splitLine: {{ lineStyle: {{ color: '#eef2f7' }} }} }},
        yAxis: {{ name: 'Impaired', nameLocation: 'middle', nameGap: 40, splitLine: {{ lineStyle: {{ color: '#eef2f7' }} }} }},
        series: [{{
          type: 'scatter',
          data: values.map(d => [d.enhanced, d.impaired, d.total, d.value, d.net]),
          symbolSize: data => Math.max(12, Math.sqrt(data[2]) * 5),
          itemStyle: {{ color: data => data.data[4] >= 0 ? COLORS.green : COLORS.red, opacity: 0.76 }},
          label: {{ show: true, formatter: p => p.data[3], position: 'right', color: COLORS.text, fontSize: 10 }}
        }}]
      }});
    }}

    function renderDimensionTotals() {{
      const dims = DATA.dimensions.map(d => shortDimension(d.dimension));
      const enhanced = DATA.dimensions.map(d => d.enhanced);
      const impaired = DATA.dimensions.map(d => d.impaired);
      charts.dimension.setOption({{
        grid: {{ left: 170, right: 42, top: 30, bottom: 28 }},
        tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'shadow' }} }},
        legend: {{ top: 0, right: 10 }},
        xAxis: {{ type: 'value', splitLine: {{ lineStyle: {{ color: '#eef2f7' }} }} }},
        yAxis: {{ type: 'category', data: [...dims].reverse(), axisLabel: {{ color: COLORS.text }} }},
        series: [
          {{ name: 'Enhanced', type: 'bar', data: [...enhanced].reverse(), itemStyle: {{ color: COLORS.green }}, barWidth: 14 }},
          {{ name: 'Impaired', type: 'bar', data: [...impaired].reverse(), itemStyle: {{ color: COLORS.red }}, barWidth: 14 }}
        ]
      }});
    }}

    function renderTable(values) {{
      const table = document.getElementById('summaryTable');
      const rows = values.map(d => `
        <tr>
          <td>${{d.value}}</td>
          <td class="pos">${{d.enhanced}}</td>
          <td class="neg">${{d.impaired}}</td>
          <td>${{d.total}}</td>
          <td class="${{d.net >= 0 ? 'pos' : 'neg'}}">${{d.net >= 0 ? '+' : ''}}${{d.net}}</td>
          <td>${{Math.round(d.shareEnhanced * 100)}}%</td>
        </tr>`).join('');
      table.innerHTML = `<thead><tr><th>Value</th><th>Enhanced</th><th>Impaired</th><th>Total</th><th>Net</th><th>Enhanced Share</th></tr></thead><tbody>${{rows}}</tbody>`;
    }}

    function renderAll() {{
      const values = currentValues();
      renderDiverging(values);
      renderHeatmap();
      renderScatter(values);
      renderDimensionTotals();
      renderTable(values);
    }}

    filter.addEventListener('change', renderAll);
    document.getElementById('resetBtn').addEventListener('click', () => {{
      filter.value = 'All';
      renderAll();
    }});
    window.addEventListener('resize', () => Object.values(charts).forEach(chart => chart.resize()));
    renderAll();
  </script>
</body>
</html>
"""


def main() -> None:
    data = build_data()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(html_template(data), encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT), **{k: data[k] for k in ["sourceRows", "eligibleRows", "enhancedTotal", "impairedTotal", "combinedTotal", "excludedRows"]}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
