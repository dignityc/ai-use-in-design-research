#!/usr/bin/env python3
"""Cluster coded AI-use items into interpretable archetypes.

Each included row is treated as one AI-use item. The feature profile is built
from categorical coding fields only:
- Discipline, Phase, Dimension, Category, Assistance
- Enhanced value states
- Impaired value states

The script uses a binary item-feature matrix, TruncatedSVD for a compact
clustering space, KMeans to discover item-level archetype clusters, and
t-SNE by default for the 2D visual layout.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_score
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

FEATURE_COLORS = {
    "Discipline": "#7c3aed",
    "Phase": "#2754c5",
    "Dimension": "#087c7a",
    "Category": "#a75c00",
    "Assistance": "#475467",
    "Enhanced": "#1f8a4c",
    "Impaired": "#b42318",
}


def clean(value: object) -> str:
    return str(value or "").strip()


def normalize_value(value: object) -> str:
    value = clean(value)
    return VALUE_NORMALIZATION.get(value, value)


def normalize_category(value: object) -> str:
    value = clean(value)
    return CATEGORY_NORMALIZATION.get(value, value)


def feature_id(kind: str, value: str) -> str:
    return f"{kind}={value}"


def split_feature(feature: str) -> tuple[str, str]:
    kind, value = feature.split("=", 1)
    return kind, value


def item_features(row: dict) -> list[str]:
    features: list[str] = []
    for kind, value in (
        ("Discipline", clean(row.get("discipline"))),
        ("Phase", clean(row.get("phase"))),
        ("Dimension", clean(row.get("dimension"))),
        ("Category", normalize_category(row.get("category"))),
        ("Assistance", clean(row.get("assistanceType"))),
    ):
        if value:
            features.append(feature_id(kind, value))

    for field in ("enhanced1", "enhanced2"):
        value = normalize_value(row.get(field))
        if value:
            features.append(feature_id("Enhanced", value))

    for field in ("impaired1", "impaired2"):
        value = normalize_value(row.get(field))
        if value:
            features.append(feature_id("Impaired", value))
    return features


def scale_coordinates(values: np.ndarray) -> np.ndarray:
    scaled = values.copy()
    for col in range(scaled.shape[1]):
        min_value = scaled[:, col].min()
        max_value = scaled[:, col].max()
        if np.isclose(min_value, max_value):
            scaled[:, col] = 0.5
        else:
            scaled[:, col] = (scaled[:, col] - min_value) / (max_value - min_value)
    scaled[:, 0] = 60 + scaled[:, 0] * 860
    scaled[:, 1] = 70 + (1 - scaled[:, 1]) * 540
    return scaled


def top_counts(items: list[dict], key: str, top_n: int = 6) -> list[dict]:
    counter = Counter(clean(item.get(key)) for item in items if clean(item.get(key)))
    total = sum(counter.values()) or 1
    return [
        {"value": value, "count": count, "share": count / total}
        for value, count in counter.most_common(top_n)
    ]


def value_counts(items: list[dict], fields: tuple[str, str], top_n: int = 6) -> list[dict]:
    counter: Counter[str] = Counter()
    for item in items:
        for field in fields:
            value = normalize_value(item.get(field))
            if value:
                counter[value] += 1
    total = sum(counter.values()) or 1
    return [
        {"value": value, "count": count, "share": count / total}
        for value, count in counter.most_common(top_n)
    ]


def top_features_for_cluster(matrix: np.ndarray, feature_names: list[str], member_indices: list[int], top_n: int = 12) -> list[dict]:
    if not member_indices:
        return []
    cluster_mean = matrix[member_indices].mean(axis=0)
    overall_mean = matrix.mean(axis=0)
    lift = np.divide(cluster_mean, overall_mean, out=np.zeros_like(cluster_mean), where=overall_mean > 0)
    scores = cluster_mean * lift
    order = np.argsort(scores)[::-1]
    result = []
    for idx in order:
        if cluster_mean[idx] <= 0:
            continue
        kind, value = split_feature(feature_names[idx])
        result.append(
            {
                "feature": feature_names[idx],
                "kind": kind,
                "value": value,
                "withinShare": float(cluster_mean[idx]),
                "overallShare": float(overall_mean[idx]),
                "lift": float(lift[idx]),
                "color": FEATURE_COLORS.get(kind, "#667085"),
            }
        )
        if len(result) >= top_n:
            break
    return result


def archetype_name(profile: dict) -> str:
    phase = profile["phase"][0]["value"] if profile["phase"] else ""
    category = profile["category"][0]["value"] if profile["category"] else ""
    assistance = profile["assistance"][0]["value"] if profile["assistance"] else ""
    if "Domain" in category:
        return f"{phase} knowledge scouting"
    if "Need Research" in category:
        return f"{phase} user-needs synthesis"
    if "Research" in category:
        return f"{phase} research augmentation"
    if "Concept" in category or "Prototype" in category:
        return f"{phase} concept generation"
    if "Critique" in category or "Assessment" in category:
        return f"{phase} critique decision support"
    if "Documentation" in category or "Planning" in category:
        return f"{phase} coordination/documentation"
    if "Testing" in category or "Evaluation" in category:
        return f"{phase} outcome prediction"
    return f"{phase} {assistance or category or 'AI-use'} archetype"


def representative_path(profile: dict) -> list[str]:
    phase = profile["phase"][0]["value"] if profile["phase"] else "Mixed phase"
    category = profile["category"][0]["value"] if profile["category"] else "Mixed category"
    assistance = profile["assistance"][0]["value"] if profile["assistance"] else "Mixed AI role"
    enhanced = profile["enhanced"][0]["value"] if profile["enhanced"] else "No dominant enhanced value"
    impaired = profile["impaired"][0]["value"] if profile["impaired"] else "No dominant impaired value"
    return [phase, category, assistance, f"Enhanced: {enhanced}", f"Impaired: {impaired}"]


def choose_k(embedding: np.ndarray, requested_k: int | None) -> tuple[int, list[dict]]:
    candidates = range(3, min(8, len(embedding) - 1) + 1)
    scores = []
    for k in candidates:
        labels = KMeans(n_clusters=k, n_init=50, random_state=17).fit_predict(embedding)
        score = silhouette_score(embedding, labels)
        scores.append({"k": k, "silhouette": float(score)})
    if requested_k:
        return requested_k, scores
    best = max(scores, key=lambda item: item["silhouette"])
    return int(best["k"]), scores


def visual_coordinates(embedding: np.ndarray, visualization: str) -> tuple[np.ndarray, dict]:
    if visualization == "svd":
        return embedding[:, :2], {"visualization": "SVD", "perplexity": None}

    perplexity = min(24, max(8, (len(embedding) - 1) // 8))
    tsne = TSNE(
        n_components=2,
        perplexity=perplexity,
        learning_rate="auto",
        init="pca",
        random_state=17,
        metric="euclidean",
    )
    return tsne.fit_transform(embedding), {"visualization": "t-SNE", "perplexity": perplexity}


def create_results(rows: list[dict], requested_k: int | None, visualization: str) -> dict:
    items = []
    feature_lists = []
    for row in rows:
        if not row.get("eligible"):
            continue
        features = item_features(row)
        if not features:
            continue
        item = {
            "rowNumber": row.get("rowNumber"),
            "discipline": clean(row.get("discipline")),
            "phase": clean(row.get("phase")),
            "dimension": clean(row.get("dimension")),
            "category": normalize_category(row.get("category")),
            "assistance": clean(row.get("assistanceType")),
            "practice": clean(row.get("practice")),
            "enhanced": [normalize_value(row.get(field)) for field in ("enhanced1", "enhanced2") if normalize_value(row.get(field))],
            "impaired": [normalize_value(row.get(field)) for field in ("impaired1", "impaired2") if normalize_value(row.get(field))],
            "features": features,
        }
        items.append(item)
        feature_lists.append(features)

    mlb = MultiLabelBinarizer()
    matrix = mlb.fit_transform(feature_lists).astype(float)
    feature_names = list(mlb.classes_)
    n_components = min(12, matrix.shape[1] - 1, matrix.shape[0] - 1)
    svd = TruncatedSVD(n_components=n_components, random_state=17)
    embedding = svd.fit_transform(matrix)
    cluster_space = embedding[:, : min(8, embedding.shape[1])]
    k, k_scores = choose_k(cluster_space, requested_k)
    model = KMeans(n_clusters=k, n_init=80, random_state=17)
    labels = model.fit_predict(cluster_space)
    visual_space, visual_meta = visual_coordinates(cluster_space, visualization)
    coordinates = scale_coordinates(visual_space)

    for idx, item in enumerate(items):
        item["cluster"] = int(labels[idx])
        item["x"] = float(coordinates[idx, 0])
        item["y"] = float(coordinates[idx, 1])

    clusters = []
    for cluster_id in range(k):
        member_indices = [idx for idx, label in enumerate(labels) if label == cluster_id]
        members = [items[idx] for idx in member_indices]
        profile = {
            "discipline": top_counts(members, "discipline"),
            "phase": top_counts(members, "phase"),
            "dimension": top_counts(members, "dimension"),
            "category": top_counts(members, "category"),
            "assistance": top_counts(members, "assistance"),
            "enhanced": value_counts(members, ("enhanced1", "enhanced2")) if False else [],
            "impaired": value_counts(members, ("impaired1", "impaired2")) if False else [],
        }
        enhanced_counter: Counter[str] = Counter()
        impaired_counter: Counter[str] = Counter()
        for member in members:
            enhanced_counter.update(member["enhanced"])
            impaired_counter.update(member["impaired"])
        enhanced_total = sum(enhanced_counter.values()) or 1
        impaired_total = sum(impaired_counter.values()) or 1
        profile["enhanced"] = [
            {"value": value, "count": count, "share": count / enhanced_total}
            for value, count in enhanced_counter.most_common(6)
        ]
        profile["impaired"] = [
            {"value": value, "count": count, "share": count / impaired_total}
            for value, count in impaired_counter.most_common(6)
        ]
        top_features = top_features_for_cluster(matrix, feature_names, member_indices)
        cluster = {
            "id": cluster_id,
            "size": len(members),
            "share": len(members) / len(items),
            "name": archetype_name(profile),
            "profile": profile,
            "topFeatures": top_features,
            "representativePath": representative_path(profile),
            "items": [
                {
                    "rowNumber": member["rowNumber"],
                    "discipline": member["discipline"],
                    "phase": member["phase"],
                    "category": member["category"],
                    "assistance": member["assistance"],
                    "enhanced": member["enhanced"],
                    "impaired": member["impaired"],
                    "practice": member["practice"],
                }
                for member in members[:10]
            ],
        }
        clusters.append(cluster)

    clusters.sort(key=lambda cluster: cluster["size"], reverse=True)
    old_to_rank = {cluster["id"]: rank for rank, cluster in enumerate(clusters)}
    for rank, cluster in enumerate(clusters):
        cluster["rank"] = rank
        cluster["label"] = f"A{rank + 1}"
    for item in items:
        item["clusterRank"] = old_to_rank[item["cluster"]]
        item["clusterLabel"] = f"A{item['clusterRank'] + 1}"

    segment_counts: defaultdict[str, Counter[int]] = defaultdict(Counter)
    for item in items:
        key = f"{item['discipline']} × {item['phase']}"
        segment_counts[key][item["clusterRank"]] += 1
    segment_matrix = []
    for key, counter in sorted(segment_counts.items()):
        total = sum(counter.values())
        segment_matrix.append(
            {
                "segment": key,
                "total": total,
                "clusters": [
                    {"cluster": rank, "label": f"A{rank + 1}", "count": counter.get(rank, 0), "share": counter.get(rank, 0) / total}
                    for rank in range(k)
                ],
            }
        )

    return {
        "metadata": {
            "includedItems": len(items),
            "featureCount": len(feature_names),
            "clusterCount": k,
            "method": "Multi-label categorical item matrix + TruncatedSVD clustering space + KMeans clustering",
            "visualization": visual_meta["visualization"],
            "visualizationInput": "First 8 TruncatedSVD components",
            "tsnePerplexity": visual_meta["perplexity"],
            "explainedVarianceRatio": [float(value) for value in svd.explained_variance_ratio_],
            "kScores": k_scores,
        },
        "clusters": clusters,
        "items": items,
        "segmentMatrix": segment_matrix,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="docs/dataset_rows.json")
    parser.add_argument("--output", default="docs/ai_use_archetype_clusters.json")
    parser.add_argument("--clusters", type=int, default=None)
    parser.add_argument("--visualization", choices=("tsne", "svd"), default="tsne")
    args = parser.parse_args()

    rows = json.loads(Path(args.input).read_text())
    results = create_results(rows, args.clusters, args.visualization)
    Path(args.output).write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(
        f"Wrote {args.output}: {results['metadata']['includedItems']} items, "
        f"{results['metadata']['clusterCount']} archetype clusters"
    )


if __name__ == "__main__":
    main()
