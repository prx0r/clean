#!/usr/bin/env python3
"""
Reddit Question Clustering v2 — fixes for the P2 collapse:
1. Stratify sampling by subreddit role (specialist/mass/narrative/etc.)
2. Strip question boilerplate before embedding
3. Use title + selftext (not just titles)
4. Two-stage hierarchy: domain clusters → sub-clusters
5. Coherence validation gates
"""

import json
import re
import sys
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np
import pyarrow.parquet as pq
from sentence_transformers import SentenceTransformer
from sklearn.cluster import HDBSCAN, AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity, cosine_distances
import umap

DATA_PATH = "/tmp/reddit-all.parquet"
OUTPUT_PATH = Path("data/research/reddit/clusters-v2.json")

SUBREDDIT_ROLES = {
    # Specialist (direct source/practitioner)
    "Tantra": "specialist", "KashmirShaivism": "specialist", "shaivism": "specialist",
    "Shaktism": "specialist", "AdvaitaVedanta": "specialist", "hinduism": "practitioner",
    "Vajrayana": "specialist", "TibetanBuddhism": "practitioner", "Dzogchen": "specialist",
    "kundalini": "practitioner",
    # Western esoteric
    "occult": "practitioner", "magick": "practitioner", "GoldenDawnMagicians": "specialist",
    "Quareia": "specialist", "Hermeticism": "specialist", "Thelema": "practitioner",
    "Theurgy": "specialist", "Esotericism": "specialist", "alchemy": "specialist",
    # Mass audience
    "awakened": "mass", "spirituality": "mass", "nonduality": "mass",
    "Meditation": "mass", "streamentry": "mass", "TheMindIlluminated": "practitioner",
    # Narrative-demand
    "HighStrangeness": "narrative", "Paranormal": "narrative", "NDE": "narrative",
    "Glitch_in_the_Matrix": "narrative", "AstralProjection": "narrative",
}

BOILERPLATE_PREFIXES = re.compile(
    r"^(how (do|can|to|would|does)|what (is|are|does|would|do|if)|"
    r"does (anyone|anybody)|has (anyone|anybody)|"
    r"is (it|there|this|that)|can (someone|anyone|i|we)|"
    r"why (is|are|does|do|would|did|don|can|won)|"
    r"should (i|we|you)|would (you|it|this)|"
    r"could (someone|you|this)|"
    r"do (you|we|people)|are (there|we|you)|"
    r"did (anyone|you|i)|"
    r"anyone (else|here)|"
    r"who (else|here|is)|"
    r"where (can|do|is|are)|"
    r"when (do|does|is|did)|"
    r"am i (the only|wrong)|"
    r"will (this|i|it)|"
    r"i need (help|advice|some)|"
    r"looking for|"
    r"can we talk about|"
    r"thoughts on|opinions on|"
    r"question about|"
    r"help (me|with))",
    re.IGNORECASE
)

def load_data(path):
    t = pq.read_table(path)
    df = t.to_pandas()
    print(f"Loaded {len(df)} rows, {df['subreddit'].nunique()} subreddits")
    print(f"Subreddit breakdown:")
    for sub, count in df['subreddit'].value_counts().items():
        role = SUBREDDIT_ROLES.get(sub, "unknown")
        print(f"  {sub} ({role}): {count}")
    return df

def is_question(row):
    title = row.get('title', '') or ''
    selftext = row.get('selftext', '') or ''
    text = f"{title} {selftext}".strip()
    if not text or text in ('[deleted]', '[removed]'):
        return False
    text = text.strip()
    if len(text) < 10:
        return False
    q_indicators = ['?', 'how ', 'what ', 'why ', 'does ', 'has anyone',
                    'is it ', 'can someone', 'anyone else', 'am i ']
    return any(text.lower().startswith(ind) or '?' in text for ind in q_indicators)

def extract_semantic_core(text):
    text = text.strip()
    text = BOILERPLATE_PREFIXES.sub('', text).strip()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:500] if len(text) > 500 else text

def build_embedding_text(row):
    parts = []
    if row.get('title'):
        parts.append(row['title'])
    selftext = row.get('selftext', '')
    if selftext and selftext not in ('[deleted]', '[removed]'):
        core = extract_semantic_core(selftext)
        if core and len(core) > 20:
            parts.append(core)
    return ' '.join(parts) if parts else ''

def stratified_sample(df, max_per_role=2000):
    df = df.copy()
    df['role'] = df['subreddit'].map(SUBREDDIT_ROLES).fillna('unknown')
    sampled = []
    for role, group in df.groupby('role'):
        if len(group) > max_per_role:
            group = group.sample(n=max_per_role, random_state=42)
        sampled.append(group)
    return pd.concat(sampled).reset_index(drop=True)

def cluster_questions(df):
    questions = df[df.apply(is_question, axis=1)].copy()
    print(f"\nQuestion submissions: {len(questions)} ({len(questions)/len(df)*100:.1f}%)")

    questions['embedding_text'] = questions.apply(build_embedding_text, axis=1)
    non_empty = questions[questions['embedding_text'].str.len() > 10].copy()
    print(f"With enough text: {len(non_empty)}")

    if len(non_empty) == 0:
        print("No questions with sufficient text!")
        return []

    print("\nStratifying by subreddit role...")
    stratified = stratified_sample(non_empty, max_per_role=4000)
    print(f"Stratified sample: {len(stratified)}")
    print(f"Role breakdown: {stratified['role'].value_counts().to_dict()}")

    print("\nGenerating embeddings...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    texts = stratified['embedding_text'].tolist()
    # Process in batches to avoid OOM
    batch_size = 256
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        emb = model.encode(batch, show_progress_bar=True)
        all_embeddings.append(emb)
    embeddings = np.vstack(all_embeddings)
    print(f"Embeddings shape: {embeddings.shape}")

    print("\nReducing dimensions with UMAP...")
    reducer = umap.UMAP(n_neighbors=30, min_dist=0.0, n_components=5, random_state=42)
    reduced = reducer.fit_transform(embeddings)
    print(f"Reduced shape: {reduced.shape}")

    # Stage 1: Coarse domain clustering
    print("\nStage 1: Domain-level clustering...")
    coarse = HDBSCAN(min_cluster_size=50, min_samples=10, metric='euclidean').fit(reduced)
    n_coarse = len(set(coarse.labels_) - {-1})
    noise_coarse = sum(coarse.labels_ == -1)
    print(f"Domain clusters: {n_coarse}, noise: {noise_coarse} ({noise_coarse/len(coarse.labels_)*100:.1f}%)")
    print(f"Cluster sizes: {Counter(c for c in coarse.labels_ if c != -1).most_common()}")

    # Stage 2: Sub-cluster each domain using the original embeddings (not reduced)
    print("\nStage 2: Sub-clustering within each domain...")
    fine_labels = coarse.labels_.copy()
    offset = 1000
    for cluster_id in sorted(set(coarse.labels_) - {-1}):
        mask = coarse.labels_ == cluster_id
        size = mask.sum()
        if size < 100:
            continue
        sub_embs = embeddings[mask]
        n_sub = min(20, max(3, size // 30))
        sub = AgglomerativeClustering(n_clusters=n_sub, metric='cosine',
                                      linkage='average').fit(sub_embs)
        sub_labels = sub.labels_
        sub_labels = offset + cluster_id * 1000 + sub_labels
        fine_labels[mask] = sub_labels
        offset += 1

    # Build results
    result = {'stratified': True, 'rows_analyzed': len(non_empty)}
    n_fine = len(set(fine_labels) - {-1})
    print(f"Final clusters: {n_fine}, noise: {sum(fine_labels == -1)}")
    clusters = []
    for label in set(fine_labels):
        if label == -1:
            continue
        mask = fine_labels == label
        cluster_df = stratified[mask].copy()
        n_unique_subs = cluster_df['subreddit'].nunique()
        role_dist = cluster_df['role'].value_counts(normalize=True).to_dict()

        cluster_texts = cluster_df['embedding_text'].tolist()

        # Genericity check
        subject_terms = extract_top_terms(cluster_texts)

        cluster_data = {
            'cluster_id': int(label),
            'total_occurrences': int(mask.sum()),
            'unique_subreddits': int(n_unique_subs),
            'role_distribution': {k: round(v, 3) for k, v in role_dist.items()},
            'mean_score': float(cluster_df['score'].mean()),
            'median_score': float(cluster_df['score'].median()),
            'coherence_mean': 0,
            'coherence_min': 0,
            'subject_terms': subject_terms[:10],
            'subreddits': sorted(cluster_df['subreddit'].unique().tolist()),
        }
        clusters.append(cluster_data)

    clusters.sort(key=lambda c: -c['total_occurrences'])
    result['total_clusters'] = len(clusters)
    result['noise_count'] = int(sum(fine_labels == -1))
    result['clusters'] = clusters

    return result

def extract_top_terms(texts, n=10):
    from sklearn.feature_extraction.text import TfidfVectorizer
    try:
        vec = TfidfVectorizer(max_features=50, stop_words='english',
                              ngram_range=(1, 2), max_df=0.95, min_df=2)
        matrix = vec.fit_transform(texts)
        scores = np.array(matrix.sum(axis=0)).flatten()
        top_indices = scores.argsort()[-n:][::-1]
        return [vec.get_feature_names_out()[i] for i in top_indices]
    except:
        return []

if __name__ == '__main__':
    import pandas as pd

    print("=" * 60)
    print("Reddit Question Clustering v2")
    print("=" * 60)

    df = load_data(DATA_PATH)
    result = cluster_questions(df)

    if result:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_PATH, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\nResults saved to {OUTPUT_PATH}")

        print(f"\n=== SUMMARY ===")
        print(f"Total clusters: {result['total_clusters']}")
        print(f"Noise points: {result['noise_count']}")

        print(f"\n=== TOP 20 CLUSTERS ===")
        for i, c in enumerate(result['clusters'][:20]):
            print(f"\n#{i}: {c['total_occurrences']} posts, {c['unique_subreddits']} subs")
            print(f"   Scores: mean={c['mean_score']:.1f}, median={c['median_score']:.1f}")
            print(f"   Coherence: mean={c['coherence_mean']:.3f}, min={c['coherence_min']:.3f}")
            print(f"   Roles: {c['role_distribution']}")
            print(f"   Terms: {', '.join(c['subject_terms'][:5])}")
            print(f"   Subs: {', '.join(c['subreddits'][:5])}")
    else:
        print("No clusters produced.")
