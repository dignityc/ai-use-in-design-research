#!/usr/bin/env python3
"""Create state-level phase association analysis with scikit-learn.

This analysis treats each coded value mention as a transaction containing
observed categorical states such as Phase=Discover, Category=Concept
Exploration, AssistanceType=Design generation, and Outcome=Enhanced:Efficiency.

Outputs:
- SVD coordinates for state nodes from a binary transaction matrix.
- Phase-to-state association edges based on observed-vs-expected strength.
- Nearest neighbors for each phase in the SVD state space.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.decomposition import PCA
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MultiLabelBinarizer


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

VARIABLE_LABELS = {
    "Phase": "Phase",
    "Discipline": "Discipline",
    "Dimension": "Dimension",
    "Category": "Category",
    "Assistance": "AI Assistance",
    "Outcome": "Value Outcome",
}

PHASES = ["Discover", "Define", "Develop", "Deliver"]


def clean(value: object) -> str:
    return str(value or "").strip()


def normalize_value(value: object) -> str:
    value = clean(value)
    return VALUE_NORMALIZATION.get(value, value)


def normalize_category(value: object) -> str:
    value = clean(value)
    return CATEGORY_NORMALIZATION.get(value, value)


def state_id(variable: str, value: str) -> str:
    return f"{variable}={value}"


def split_state(identifier: str) -> tuple[str, str]:
    variable, value = identifier.split("=", 1)
    return variable, value


def expand_transactions(rows: list[dict]) -> list[list[str]]:
    transactions: list[list[str]] = []
    for row in rows:
        if not row.get("eligible"):
            continue

        base = []
        for variable, value in (
            ("Phase", clean(row.get("phase"))),
            ("Discipline", clean(row.get("discipline"))),
            ("Dimension", clean(row.get("dimension"))),
            ("Category", normalize_category(row.get("category"))),
            ("Assistance", clean(row.get("assistanceType"))),
        ):
            if value:
                base.append(state_id(variable, value))

        for field in ("enhanced1", "enhanced2"):
            value = normalize_value(row.get(field))
            if value:
                transactions.append(base + [state_id("Outcome", f"Enhanced: {value}")])

        for field in ("impaired1", "impaired2"):
            value = normalize_value(row.get(field))
            if value:
                transactions.append(base + [state_id("Outcome", f"Impaired: {value}")])

    return transactions


def node_color(variable: str) -> str:
    return {
        "Phase": "#2754c5",
        "Discipline": "#7c3aed",
        "Dimension": "#087c7a",
        "Category": "#a75c00",
        "Assistance": "#475467",
        "Outcome": "#b42318",
    }.get(variable, "#667085")


def compute_npmi(observed: int, phase_count: int, target_count: int, total: int) -> float:
    if observed == 0:
        return 0.0
    pxy = observed / total
    px = phase_count / total
    py = target_count / total
    pmi = math.log(pxy / (px * py))
    return pmi / -math.log(pxy)


def association_edges(transactions: list[list[str]], min_observed: int, top_per_phase: int) -> list[dict]:
    total = len(transactions)
    state_counts = Counter(state for transaction in transactions for state in transaction)
    co_counts: Counter[tuple[str, str]] = Counter()

    phase_ids = [state_id("Phase", phase) for phase in PHASES]
    phase_set = set(phase_ids)
    for transaction in transactions:
        states = set(transaction)
        phase = next((state for state in states if state in phase_set), None)
        if not phase:
            continue
        for target in states:
            if target == phase or target.startswith("Phase="):
                continue
            co_counts[(phase, target)] += 1

    by_phase: defaultdict[str, list[dict]] = defaultdict(list)
    for (phase, target), observed in co_counts.items():
        if observed < min_observed:
            continue
        phase_count = state_counts[phase]
        target_count = state_counts[target]
        expected = phase_count * target_count / total
        if expected <= 0:
            continue
        residual = (observed - expected) / math.sqrt(expected)
        if residual <= 0:
            continue
        npmi = compute_npmi(observed, phase_count, target_count, total)
        odds_ratio = (observed / phase_count) / (target_count / total)
        variable, value = split_state(target)
        by_phase[phase].append(
            {
                "source": phase,
                "target": target,
                "sourceLabel": split_state(phase)[1],
                "targetLabel": value,
                "targetVariable": variable,
                "observed": observed,
                "expected": expected,
                "residual": residual,
                "npmi": npmi,
                "oddsRatio": odds_ratio,
                "phaseShare": observed / phase_count,
                "targetShare": observed / target_count,
            }
        )

    edges = []
    for phase, phase_edges in by_phase.items():
        phase_edges.sort(key=lambda edge: (edge["residual"], edge["npmi"], edge["observed"]), reverse=True)
        edges.extend(phase_edges[:top_per_phase])
    return edges


def quadrant_points(transactions: list[list[str]], min_observed: int) -> dict[str, list[dict]]:
    total = len(transactions)
    state_counts = Counter(state for transaction in transactions for state in transaction)
    co_counts: Counter[tuple[str, str]] = Counter()
    phase_ids = [state_id("Phase", phase) for phase in PHASES]
    phase_set = set(phase_ids)

    for transaction in transactions:
        states = set(transaction)
        phase = next((state for state in states if state in phase_set), None)
        outcome = next((state for state in states if state.startswith("Outcome=")), None)
        if not phase or not outcome:
            continue

        outcome_value = split_state(outcome)[1]
        polarity = "Enhanced" if outcome_value.startswith("Enhanced:") else "Impaired"
        for target in states:
            if target == phase or target.startswith("Phase="):
                continue
            co_counts[(phase, target, polarity)] += 1

    by_phase: dict[str, list[dict]] = {}
    for phase_name in PHASES:
        phase = state_id("Phase", phase_name)
        candidates = sorted({target for p, target, _ in co_counts if p == phase})
        points = []
        phase_count = state_counts[phase]
        for target in candidates:
            enhanced = co_counts[(phase, target, "Enhanced")]
            impaired = co_counts[(phase, target, "Impaired")]
            observed_total = enhanced + impaired
            if observed_total < min_observed:
                continue
            target_count = state_counts[target]
            expected = phase_count * target_count / total
            residual_total = (observed_total - expected) / math.sqrt(expected) if expected else 0
            if residual_total <= 0:
                continue
            enhanced_strength = enhanced / expected if expected else 0
            impaired_strength = impaired / expected if expected else 0
            variable, value = split_state(target)
            points.append(
                {
                    "id": f"{phase}->{target}",
                    "phase": phase_name,
                    "state": target,
                    "variable": variable,
                    "label": value,
                    "observed": observed_total,
                    "enhancedObserved": enhanced,
                    "impairedObserved": impaired,
                    "expected": expected,
                    "residual": residual_total,
                    "enhancedStrength": enhanced_strength,
                    "impairedStrength": impaired_strength,
                    "netStrength": enhanced_strength - impaired_strength,
                    "shareEnhanced": enhanced / observed_total if observed_total else 0,
                }
            )
        points.sort(key=lambda item: (item["residual"], item["observed"]), reverse=True)
        by_phase[phase_name] = points[:22]
    return by_phase


def scale_coordinates(coordinates: np.ndarray) -> np.ndarray:
    scaled = coordinates.copy()
    for column in range(scaled.shape[1]):
        values = scaled[:, column]
        min_value = values.min()
        max_value = values.max()
        if math.isclose(min_value, max_value):
            scaled[:, column] = 0.5
        else:
            scaled[:, column] = (values - min_value) / (max_value - min_value)
    scaled[:, 0] = 60 + scaled[:, 0] * 880
    scaled[:, 1] = 60 + (1 - scaled[:, 1]) * 560
    return scaled


def component_loading_summary(
    state_names: list[str],
    state_counts: Counter[str],
    feature_vectors: np.ndarray,
    max_components: int = 4,
    top_n: int = 10,
) -> list[dict]:
    summaries = []
    for component_index in range(min(max_components, feature_vectors.shape[1])):
        loadings = feature_vectors[:, component_index]
        positive_indices = np.argsort(loadings)[::-1][:top_n]
        negative_indices = np.argsort(loadings)[:top_n]

        def item(index: int) -> dict:
            state = state_names[index]
            variable, value = split_state(state)
            return {
                "id": state,
                "variable": variable,
                "label": value,
                "loading": float(loadings[index]),
                "absLoading": float(abs(loadings[index])),
                "count": int(state_counts[state]),
                "color": node_color(variable),
            }

        summaries.append(
            {
                "component": component_index + 1,
                "positive": [item(index) for index in positive_indices],
                "negative": [item(index) for index in negative_indices],
            }
        )
    return summaries


def factor_map_nodes(
    state_names: list[str],
    state_counts: Counter[str],
    coordinates: np.ndarray,
    raw_coordinates: np.ndarray,
    total: int,
) -> list[dict]:
    nodes = []
    for i, state in enumerate(state_names):
        variable, value = split_state(state)
        if variable not in {"Phase", "Discipline", "Dimension", "Category", "Assistance", "Outcome"}:
            continue
        nodes.append(
            {
                "id": state,
                "variable": variable,
                "variableLabel": VARIABLE_LABELS.get(variable, variable),
                "label": value,
                "count": int(state_counts[state]),
                "share": state_counts[state] / total,
                "x": float(coordinates[i, 0]),
                "y": float(coordinates[i, 1]),
                "component1": float(raw_coordinates[i, 0]),
                "component2": float(raw_coordinates[i, 1]),
                "color": node_color(variable),
                "isPhase": variable == "Phase",
            }
        )
    return nodes


def create_results(rows: list[dict], min_observed: int, top_per_phase: int) -> dict:
    transactions = expand_transactions(rows)
    mlb = MultiLabelBinarizer()
    matrix = mlb.fit_transform(transactions)
    state_names = list(mlb.classes_)

    components = min(8, matrix.shape[1] - 1, matrix.shape[0] - 1)
    svd = TruncatedSVD(n_components=components, random_state=7)
    svd.fit(matrix)
    feature_vectors = svd.components_.T * svd.singular_values_
    coordinates = scale_coordinates(feature_vectors[:, :2])

    pca_components = min(6, matrix.shape[1] - 1, matrix.shape[0] - 1)
    pca = PCA(n_components=pca_components, random_state=7)
    pca.fit(matrix.astype(float))
    pca_feature_vectors = pca.components_.T * np.sqrt(pca.explained_variance_)
    pca_coordinates = scale_coordinates(pca_feature_vectors[:, :2])

    state_counts = Counter(state for transaction in transactions for state in transaction)
    index = {state: i for i, state in enumerate(state_names)}

    nodes = []
    for state in state_names:
        variable, value = split_state(state)
        if variable not in {"Phase", "Discipline", "Dimension", "Category", "Assistance", "Outcome"}:
            continue
        i = index[state]
        nodes.append(
            {
                "id": state,
                "variable": variable,
                "variableLabel": VARIABLE_LABELS.get(variable, variable),
                "label": value,
                "count": state_counts[state],
                "share": state_counts[state] / len(transactions),
                "x": float(coordinates[i, 0]),
                "y": float(coordinates[i, 1]),
                "component1": float(feature_vectors[i, 0]),
                "component2": float(feature_vectors[i, 1]),
                "color": node_color(variable),
                "isPhase": variable == "Phase",
            }
        )

    edges = association_edges(transactions, min_observed=min_observed, top_per_phase=top_per_phase)

    phase_neighbors = {}
    sim = cosine_similarity(feature_vectors)
    for phase in PHASES:
        phase_state = state_id("Phase", phase)
        phase_idx = index[phase_state]
        neighbors = []
        for state in state_names:
            if state == phase_state or state.startswith("Phase="):
                continue
            variable, value = split_state(state)
            neighbors.append(
                {
                    "id": state,
                    "variable": variable,
                    "label": value,
                    "similarity": float(sim[phase_idx, index[state]]),
                    "count": state_counts[state],
                }
            )
        neighbors.sort(key=lambda item: item["similarity"], reverse=True)
        phase_neighbors[phase] = neighbors[:12]

    phase_edge_summary = {}
    for phase in PHASES:
        phase_state = state_id("Phase", phase)
        phase_edges = [edge for edge in edges if edge["source"] == phase_state]
        phase_edge_summary[phase] = phase_edges[:12]

    return {
        "metadata": {
            "includedCases": int(sum(1 for row in rows if row.get("eligible"))),
            "valueMentionEvents": len(transactions),
            "stateNodes": len(nodes),
            "method": "MultiLabelBinarizer one-hot transaction matrix + TruncatedSVD state embedding + observed-vs-expected phase associations",
            "minObserved": min_observed,
            "topPerPhase": top_per_phase,
            "explainedVarianceRatio": [float(value) for value in svd.explained_variance_ratio_],
        },
        "nodes": nodes,
        "edges": edges,
        "componentLoadings": component_loading_summary(state_names, state_counts, feature_vectors),
        "factorMap": {
            "method": "PCA on centered one-hot transaction matrix",
            "explainedVarianceRatio": [float(value) for value in pca.explained_variance_ratio_],
            "nodes": factor_map_nodes(
                state_names,
                state_counts,
                pca_coordinates,
                pca_feature_vectors,
                len(transactions),
            ),
            "componentLoadings": component_loading_summary(
                state_names,
                state_counts,
                pca.components_.T,
                max_components=min(4, pca_components),
            ),
        },
        "phaseNeighbors": phase_neighbors,
        "phaseEdgeSummary": phase_edge_summary,
        "quadrantPoints": quadrant_points(transactions, min_observed=min_observed),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="docs/dataset_rows.json")
    parser.add_argument("--output", default="docs/phase_state_level_analysis.json")
    parser.add_argument("--min-observed", type=int, default=5)
    parser.add_argument("--top-per-phase", type=int, default=12)
    args = parser.parse_args()

    rows = json.loads(Path(args.input).read_text())
    results = create_results(rows, args.min_observed, args.top_per_phase)
    Path(args.output).write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(
        f"Wrote {args.output}: {results['metadata']['stateNodes']} state nodes, "
        f"{len(results['edges'])} phase association edges"
    )


if __name__ == "__main__":
    main()
