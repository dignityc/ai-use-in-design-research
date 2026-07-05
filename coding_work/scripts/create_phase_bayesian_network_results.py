#!/usr/bin/env python3
"""Create Bayesian-network style phase dependency analysis results.

The project environment does not include pgmpy, so this script implements a
small discrete structure-learning routine for the dashboard data:
- expand each enhanced/impaired value into a value-mention event
- learn tier-constrained parent sets with BIC/AIC local scores
- estimate bootstrap edge stability by resampling events
- export compact conditional distributions for dashboard inspection
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import random
from collections import Counter
from pathlib import Path
from typing import Iterable

import pandas as pd


VALUE_NORMALIZATION = {
    "Context awareness": "Context Awareness",
    "Context Appropriateness": "Context Awareness",
    "Feasibiltiy": "Feasibility",
    "Human-cnetredness": "Human-centeredness",
    "Empathy (Human-centredness)": "Empathy / Human-centeredness",
    "Empathy": "Empathy / Human-centeredness",
    "User-centeredness": "Empathy / Human-centeredness",
    "Learning (Gaining insigts)": "Learning / Skills Development",
    "Learning": "Learning / Skills Development",
    "Skills development": "Learning / Skills Development",
    "Skills Development": "Learning / Skills Development",
}

CATEGORY_NORMALIZATION = {
    "Project Planning & Workflow Management  (BL)": "Project Planning & Workflow Management",
    "Domain & Technical Knowledge Gathering": "Domain, Technical, & Market Knowledge Gathering",
}

VARIABLES = ["Phase", "Discipline", "Dimension", "Category", "AssistanceType", "Polarity", "Value"]

TIERS = {
    "Phase": 0,
    "Discipline": 0,
    "Dimension": 1,
    "Category": 2,
    "AssistanceType": 3,
    "Polarity": 4,
    "Value": 5,
}


def clean(value: object) -> str:
    return str(value or "").strip()


def normalize_value(value: object) -> str:
    value = clean(value)
    return VALUE_NORMALIZATION.get(value, value)


def normalize_category(value: object) -> str:
    value = clean(value)
    return CATEGORY_NORMALIZATION.get(value, value)


def expand_events(rows: list[dict]) -> pd.DataFrame:
    events: list[dict[str, str]] = []
    for source_row in rows:
        if not source_row.get("eligible"):
            continue

        base = {
            "SourceRow": source_row.get("rowNumber"),
            "Phase": clean(source_row.get("phase")),
            "Discipline": clean(source_row.get("discipline")),
            "Dimension": clean(source_row.get("dimension")),
            "Category": normalize_category(source_row.get("category")),
            "AssistanceType": clean(source_row.get("assistanceType")),
        }

        for field in ("enhanced1", "enhanced2"):
            value = normalize_value(source_row.get(field))
            if value:
                event = dict(base)
                event["Polarity"] = "Enhanced"
                event["Value"] = value
                events.append(event)

        for field in ("impaired1", "impaired2"):
            value = normalize_value(source_row.get(field))
            if value:
                event = dict(base)
                event["Polarity"] = "Impaired"
                event["Value"] = value
                events.append(event)

    return pd.DataFrame(events)


def local_score(data: pd.DataFrame, child: str, parents: Iterable[str], criterion: str) -> dict:
    parents = tuple(parents)
    n = len(data)
    child_cardinality = data[child].nunique()

    if not parents:
        counts = data[child].value_counts()
        log_likelihood = sum(count * math.log(count / n) for count in counts if count)
        parameters = child_cardinality - 1
    else:
        parent_cardinality = 1
        for parent in parents:
            parent_cardinality *= data[parent].nunique()
        parameters = (child_cardinality - 1) * parent_cardinality
        log_likelihood = 0.0
        for _, group in data.groupby(list(parents), observed=True):
            denominator = len(group)
            for count in group[child].value_counts():
                if count:
                    log_likelihood += count * math.log(count / denominator)

    penalty = parameters if criterion == "aic" else 0.5 * parameters * math.log(n)
    return {
        "score": log_likelihood - penalty,
        "logLikelihood": log_likelihood,
        "parameters": parameters,
        "parents": list(parents),
    }


def parent_candidates(child: str, max_parents: int) -> list[tuple[str, ...]]:
    candidates = [variable for variable in VARIABLES if TIERS[variable] < TIERS[child]]
    parent_sets: list[tuple[str, ...]] = []
    for size in range(0, min(max_parents, len(candidates)) + 1):
        parent_sets.extend(itertools.combinations(candidates, size))
    return parent_sets


def learn_structure(data: pd.DataFrame, criterion: str, max_parents: int) -> dict:
    selected: dict[str, dict] = {}
    top_parent_sets: dict[str, list[dict]] = {}

    for child in VARIABLES:
        scored = [local_score(data, child, parents, criterion) for parents in parent_candidates(child, max_parents)]
        scored.sort(key=lambda item: item["score"], reverse=True)
        selected[child] = scored[0]
        top_parent_sets[child] = scored[:8]

    edges = []
    for child, model in selected.items():
        full_score = model["score"]
        for parent in model["parents"]:
            reduced = [candidate for candidate in model["parents"] if candidate != parent]
            reduced_score = local_score(data, child, reduced, criterion)["score"]
            edges.append(
                {
                    "source": parent,
                    "target": child,
                    "criterion": criterion.upper(),
                    "deltaScore": full_score - reduced_score,
                }
            )

    return {"criterion": criterion.upper(), "selected": selected, "topParentSets": top_parent_sets, "edges": edges}


def bootstrap_stability(data: pd.DataFrame, criterion: str, max_parents: int, iterations: int, seed: int) -> list[dict]:
    random.seed(seed)
    edge_counts: Counter[tuple[str, str]] = Counter()
    records = data.to_dict("records")

    for _ in range(iterations):
        sample = pd.DataFrame([records[random.randrange(len(records))] for _ in range(len(records))])
        model = learn_structure(sample, criterion, max_parents)
        for edge in model["edges"]:
            edge_counts[(edge["source"], edge["target"])] += 1

    result = []
    for (source, target), count in edge_counts.most_common():
        result.append({"source": source, "target": target, "criterion": criterion.upper(), "stability": count / iterations})
    return result


def distribution(data: pd.DataFrame, group_fields: list[str], target: str, minimum_n: int = 1, top_n: int = 8) -> list[dict]:
    rows = []
    for key, group in data.groupby(group_fields, observed=True):
        if len(group) < minimum_n:
            continue
        if not isinstance(key, tuple):
            key = (key,)
        counts = group[target].value_counts()
        rows.append(
            {
                "group": dict(zip(group_fields, key)),
                "n": int(len(group)),
                "target": target,
                "distribution": [
                    {"value": str(value), "count": int(count), "share": count / len(group)}
                    for value, count in counts.head(top_n).items()
                ],
            }
        )
    rows.sort(key=lambda item: item["n"], reverse=True)
    return rows


def marginal_distribution(data: pd.DataFrame, variable: str, top_n: int = 10) -> dict:
    counts = data[variable].value_counts()
    total = int(counts.sum())
    return {
        "variable": variable,
        "n": total,
        "distribution": [
            {"value": str(value), "count": int(count), "share": count / total}
            for value, count in counts.head(top_n).items()
        ],
    }


def model_comparisons(data: pd.DataFrame) -> dict:
    comparisons = {}
    for child in ("Polarity", "Value"):
        parent_sets = [(), ("Phase",), ("Dimension",), ("Category",), ("AssistanceType",), ("Phase", "Polarity"), ("Dimension", "Polarity")]
        child_sets = []
        for parents in parent_sets:
            if child in parents:
                continue
            if any(TIERS[parent] >= TIERS[child] for parent in parents):
                continue
            row = {"parents": list(parents)}
            row["bic"] = local_score(data, child, parents, "bic")
            row["aic"] = local_score(data, child, parents, "aic")
            child_sets.append(row)
        child_sets.sort(key=lambda item: item["bic"]["score"], reverse=True)
        comparisons[child] = child_sets
    return comparisons


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="docs/dataset_rows.json")
    parser.add_argument("--output", default="docs/phase_bayesian_network_results.json")
    parser.add_argument("--bootstrap", type=int, default=200)
    parser.add_argument("--max-parents", type=int, default=2)
    args = parser.parse_args()

    source_path = Path(args.input)
    rows = json.loads(source_path.read_text())
    data = expand_events(rows)

    bic_model = learn_structure(data, "bic", args.max_parents)
    aic_model = learn_structure(data, "aic", args.max_parents)
    bic_stability = bootstrap_stability(data, "bic", args.max_parents, args.bootstrap, seed=7)
    aic_stability = bootstrap_stability(data, "aic", args.max_parents, args.bootstrap, seed=11)

    stability_lookup = {
        (item["criterion"], item["source"], item["target"]): item["stability"]
        for item in bic_stability + aic_stability
    }
    for model in (bic_model, aic_model):
        for edge in model["edges"]:
            edge["stability"] = stability_lookup.get((edge["criterion"], edge["source"], edge["target"]), 0)

    results = {
        "metadata": {
            "source": str(source_path),
            "includedCases": int(sum(1 for row in rows if row.get("eligible"))),
            "sourceRows": int(len(rows)),
            "valueMentionEvents": int(len(data)),
            "bootstrapIterations": args.bootstrap,
            "maxParents": args.max_parents,
            "variables": VARIABLES,
            "method": "tier-constrained discrete Bayesian-network structure learning with BIC/AIC local scores",
        },
        "cardinality": {variable: int(data[variable].nunique()) for variable in VARIABLES},
        "marginals": {variable: marginal_distribution(data, variable) for variable in VARIABLES},
        "models": {"bic": bic_model, "aic": aic_model},
        "bootstrap": {"bic": bic_stability, "aic": aic_stability},
        "comparisons": model_comparisons(data),
        "conditionals": {
            "dimensionGivenPhase": distribution(data, ["Phase"], "Dimension", top_n=6),
            "categoryGivenDimension": distribution(data, ["Dimension"], "Category", top_n=8),
            "assistanceGivenCategory": distribution(data, ["Category"], "AssistanceType", minimum_n=10, top_n=6),
            "polarityGivenPhaseDimension": distribution(data, ["Phase", "Dimension"], "Polarity", minimum_n=20, top_n=2),
            "valueGivenPhasePolarity": distribution(data, ["Phase", "Polarity"], "Value", top_n=8),
            "valueGivenPhaseAssistance": distribution(data, ["Phase", "AssistanceType"], "Value", minimum_n=15, top_n=5),
        },
    }

    output_path = Path(args.output)
    output_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"Wrote {output_path} with {len(data)} value-mention events")


if __name__ == "__main__":
    main()
