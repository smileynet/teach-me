#!/usr/bin/env python3
"""Spike: compare cycle-breaking and foundational scoring strategies.

Runs both strategies on the reference fixture and a synthetic graph,
measures differences, and produces a decision summary.

Usage:
    python tools/spike_ordering_comparison.py
"""

from __future__ import annotations

# Windows consoles default to cp1252; force UTF-8 so ✓/→/emoji glyphs don't crash (#265).
import sys as _sys
if hasattr(_sys.stdout, "reconfigure"):
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(_sys.stderr, "reconfigure"):
    _sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import json
import sys
from pathlib import Path

import networkx as nx

sys.path.insert(0, str(Path(__file__).parent))
from extract_concepts import extract_concepts


# =============================================================================
# Synthetic graph fixture: 20 nodes, ~30 edges, 3-4 cycles
# Represents a medium-sized reference doc (e.g., API with shared concepts)
# =============================================================================

def build_synthetic_graph() -> nx.DiGraph:
    """Build a 20-node graph with weighted edges and 3-4 intentional cycles.

    Nodes represent hypothetical topics in a networking reference doc.
    Weights represent prerequisite strength (0.1=weak, 0.9=strong).
    """
    G = nx.DiGraph()

    topics = [
        "tcp-overview", "udp-overview", "ip-addressing", "dns-resolution",
        "http-basics", "tls-handshake", "certificates", "socket-api",
        "connection-pooling", "load-balancing", "reverse-proxy", "cdn-caching",
        "websockets", "http2-multiplexing", "grpc-streaming", "service-discovery",
        "health-checks", "circuit-breaker", "retry-patterns", "timeout-config",
    ]
    for i, t in enumerate(topics):
        G.add_node(i, heading=t)

    # Strong prerequisites (high weight — core dependency chain)
    strong_edges = [
        (2, 0, 0.9),   # ip-addressing → tcp-overview
        (2, 1, 0.9),   # ip-addressing → udp-overview
        (0, 4, 0.8),   # tcp → http-basics
        (0, 7, 0.8),   # tcp → socket-api
        (4, 5, 0.8),   # http-basics → tls-handshake
        (5, 6, 0.7),   # tls-handshake → certificates
        (7, 8, 0.7),   # socket-api → connection-pooling
        (4, 12, 0.7),  # http-basics → websockets
        (4, 13, 0.7),  # http-basics → http2-multiplexing
        (13, 14, 0.6), # http2 → grpc-streaming
        (2, 3, 0.6),   # ip-addressing → dns-resolution
        (3, 15, 0.6),  # dns → service-discovery
        (15, 16, 0.5), # service-discovery → health-checks
        (8, 9, 0.5),   # connection-pooling → load-balancing
        (9, 10, 0.5),  # load-balancing → reverse-proxy
        (10, 11, 0.4), # reverse-proxy → cdn-caching
        (16, 17, 0.5), # health-checks → circuit-breaker
        (17, 18, 0.4), # circuit-breaker → retry-patterns
        (18, 19, 0.4), # retry-patterns → timeout-config
    ]

    # Medium prerequisites (cross-cutting)
    medium_edges = [
        (0, 12, 0.5),  # tcp → websockets
        (5, 13, 0.4),  # tls → http2 (ALPN)
        (7, 12, 0.4),  # socket-api → websockets
        (9, 15, 0.3),  # load-balancing → service-discovery
        (17, 19, 0.3), # circuit-breaker → timeout-config
        (3, 10, 0.3),  # dns → reverse-proxy
    ]

    # Cycle-creating edges (weaker — these represent "mutual enrichment")
    cycle_edges = [
        (6, 5, 0.2),   # certificates → tls (understanding certs helps understand TLS)
        (12, 0, 0.15), # websockets → tcp (WS deepens TCP understanding)
        (15, 9, 0.2),  # service-discovery → load-balancing (mutual)
        (19, 17, 0.1), # timeout-config → circuit-breaker (configuring timeouts informs CB design)
    ]

    for src, dst, weight in strong_edges + medium_edges + cycle_edges:
        G.add_edge(src, dst, weight=weight, concept=f"{topics[src]}→{topics[dst]}")

    return G


# =============================================================================
# Part A: Cycle-breaking algorithms
# =============================================================================

def mwfas_iterative(G: nx.DiGraph) -> tuple[nx.DiGraph, list[tuple]]:
    """Minimum Weighted Feedback Arc Set — iterative cycle removal.

    Find cycle → remove min-weight edge → repeat.
    Then try re-adding removed edges in decreasing weight order.

    Returns: (DAG, list of removed edges as (u, v, data) tuples)
    """
    H = G.copy()
    removed = []

    while not nx.is_directed_acyclic_graph(H):
        try:
            cycle = nx.find_cycle(H)
        except nx.NetworkXNoCycle:
            break

        # Find min-weight edge in this cycle
        min_edge = min(cycle, key=lambda e: H[e[0]][e[1]].get("weight", 0.5))
        u, v = min_edge[0], min_edge[1]
        edge_data = H[u][v].copy()
        removed.append((u, v, edge_data))
        H.remove_edge(u, v)

    # Try re-adding removed edges (highest weight first) if they don't create cycles
    removed_sorted = sorted(removed, key=lambda e: e[2].get("weight", 0), reverse=True)
    final_removed = []
    for u, v, data in removed_sorted:
        H.add_edge(u, v, **data)
        if not nx.is_directed_acyclic_graph(H):
            H.remove_edge(u, v)
            final_removed.append((u, v, data))
        # else: successfully re-added

    return H, final_removed


def eades_lin_smyth(G: nx.DiGraph) -> tuple[nx.DiGraph, list[tuple]]:
    """Eades-Lin-Smyth greedy heuristic for feedback arc set.

    Iteratively peel sources and sinks, pick max-differential vertex otherwise.
    Determine feedback arcs as edges going "backward" in the resulting ordering.

    Returns: (DAG, list of removed edges as (u, v, data) tuples)
    """
    H = G.copy()
    nodes = set(H.nodes())
    s1 = []  # ordering from left (sources)
    s2 = []  # ordering from right (sinks)

    while nodes:
        # Remove sinks
        changed = True
        while changed:
            changed = False
            for n in list(nodes):
                if H.out_degree(n) == 0 or all(
                    succ not in nodes for succ in H.successors(n)
                ):
                    s2.append(n)
                    nodes.discard(n)
                    changed = True

        # Remove sources
        changed = True
        while changed:
            changed = False
            for n in list(nodes):
                if H.in_degree(n) == 0 or all(
                    pred not in nodes for pred in H.predecessors(n)
                ):
                    s1.append(n)
                    nodes.discard(n)
                    changed = True

        # Pick max differential if stuck
        if nodes:
            # Compute differential among remaining nodes
            best = max(nodes, key=lambda n: sum(
                1 for s in H.successors(n) if s in nodes
            ) - sum(
                1 for p in H.predecessors(n) if p in nodes
            ))
            s1.append(best)
            nodes.discard(best)

    # Final ordering
    ordering = s1 + list(reversed(s2))
    position = {node: i for i, node in enumerate(ordering)}

    # Backward edges = feedback arc set
    removed = []
    dag = G.copy()
    for u, v, data in list(G.edges(data=True)):
        if position.get(u, 0) > position.get(v, 0):
            removed.append((u, v, data))
            dag.remove_edge(u, v)

    return dag, removed


# =============================================================================
# Part B: Foundational scoring
# =============================================================================

def score_in_degree(G: nx.DiGraph) -> dict[int, float]:
    """Normalized in-degree: how many nodes depend on this one."""
    max_in = max((G.in_degree(n) for n in G.nodes()), default=1) or 1
    return {n: G.in_degree(n) / max_in for n in G.nodes()}


def score_pagerank(G: nx.DiGraph) -> dict[int, float]:
    """PageRank with damping=0.85."""
    pr = nx.pagerank(G, alpha=0.85)
    max_pr = max(pr.values()) or 1
    return {n: v / max_pr for n, v in pr.items()}


def score_frequency_position(G: nx.DiGraph, chunks: list[dict] | None = None) -> dict[int, float]:
    """Frequency × (1/position) — our current extract_concepts scoring.

    For graph-only comparison (no chunks), approximate with:
    frequency = (in_degree + out_degree) / total_edges
    position = node index (assuming original document order)
    """
    total_edges = max(G.number_of_edges(), 1)
    scores = {}
    for n in G.nodes():
        freq = (G.in_degree(n) + G.out_degree(n)) / total_edges
        pos_factor = 1.0 / (n + 1)  # node 0 → 1.0, node 19 → 0.05
        scores[n] = freq * pos_factor
    # Normalize
    max_s = max(scores.values()) or 1
    return {n: v / max_s for n, v in scores.items()}


def topological_sort_with_tiebreak(dag: nx.DiGraph, scores: dict[int, float]) -> list[int]:
    """Kahn's algorithm with tie-breaking by score (higher = earlier)."""
    in_degree = {n: dag.in_degree(n) for n in dag.nodes()}
    available = sorted(
        [n for n, d in in_degree.items() if d == 0],
        key=lambda n: scores.get(n, 0),
        reverse=True,
    )
    order = []

    while available:
        node = available.pop(0)
        order.append(node)
        for succ in dag.successors(node):
            in_degree[succ] -= 1
            if in_degree[succ] == 0:
                available.append(succ)
                available.sort(key=lambda n: scores.get(n, 0), reverse=True)

    return order


# =============================================================================
# Analysis
# =============================================================================

def analyze_cycle_breaking(G: nx.DiGraph, name: str) -> dict:
    """Run both cycle-breaking algorithms and compare results."""
    print(f"\n{'='*60}")
    print(f"Part A: Cycle-breaking — {name}")
    print(f"{'='*60}")
    print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    print(f"Is DAG: {nx.is_directed_acyclic_graph(G)}")

    if nx.is_directed_acyclic_graph(G):
        print("  Already a DAG — no cycle-breaking needed.")
        return {"already_dag": True}

    cycles = list(nx.simple_cycles(G))
    print(f"Cycles: {len(cycles)}")

    # SCCs
    sccs = [c for c in nx.strongly_connected_components(G) if len(c) > 1]
    print(f"Non-trivial SCCs: {len(sccs)} (sizes: {[len(c) for c in sccs]})")

    # MWFAS
    dag_mw, removed_mw = mwfas_iterative(G)
    total_weight_mw = sum(d.get("weight", 0.5) for _, _, d in removed_mw)
    print(f"\nMWFAS iterative:")
    print(f"  Edges removed: {len(removed_mw)}")
    print(f"  Total weight removed: {total_weight_mw:.3f}")
    print(f"  Result is DAG: {nx.is_directed_acyclic_graph(dag_mw)}")
    for u, v, d in removed_mw:
        h = G.nodes[u].get("heading", u)
        t = G.nodes[v].get("heading", v)
        print(f"    Cut: {h} → {t} (weight={d.get('weight', '?')})")

    # Eades-Lin-Smyth
    dag_els, removed_els = eades_lin_smyth(G)
    total_weight_els = sum(d.get("weight", 0.5) for _, _, d in removed_els)
    print(f"\nEades-Lin-Smyth:")
    print(f"  Edges removed: {len(removed_els)}")
    print(f"  Total weight removed: {total_weight_els:.3f}")
    print(f"  Result is DAG: {nx.is_directed_acyclic_graph(dag_els)}")
    for u, v, d in removed_els:
        h = G.nodes[u].get("heading", u)
        t = G.nodes[v].get("heading", v)
        print(f"    Cut: {h} → {t} (weight={d.get('weight', '?')})")

    # Compare
    print(f"\nComparison:")
    print(f"  MWFAS: {len(removed_mw)} edges, total weight {total_weight_mw:.3f}")
    print(f"  ELS:   {len(removed_els)} edges, total weight {total_weight_els:.3f}")
    if total_weight_mw < total_weight_els:
        print(f"  → MWFAS preserves more weight (removes less: Δ={total_weight_els - total_weight_mw:.3f})")
    elif total_weight_els < total_weight_mw:
        print(f"  → ELS preserves more weight (removes less: Δ={total_weight_mw - total_weight_els:.3f})")
    else:
        print(f"  → Same total weight removed")

    # Do the resulting orderings differ?
    order_mw = list(nx.topological_sort(dag_mw))
    order_els = list(nx.topological_sort(dag_els))
    agreement = sum(1 for a, b in zip(order_mw, order_els) if a == b) / max(len(order_mw), 1)
    print(f"  Ordering agreement (position-by-position): {agreement:.0%}")

    return {
        "mwfas_removed": len(removed_mw),
        "mwfas_weight": total_weight_mw,
        "els_removed": len(removed_els),
        "els_weight": total_weight_els,
        "ordering_agreement": agreement,
    }


def analyze_scoring(G: nx.DiGraph, name: str) -> dict:
    """Run all three scoring methods and compare tie-breaking behavior."""
    print(f"\n{'='*60}")
    print(f"Part B: Foundational scoring — {name}")
    print(f"{'='*60}")

    # Ensure DAG for topological sort
    if not nx.is_directed_acyclic_graph(G):
        G, _ = mwfas_iterative(G)

    scores_id = score_in_degree(G)
    scores_pr = score_pagerank(G)
    scores_fp = score_frequency_position(G)

    # Show top-5 by each method
    print("\nTop-5 most foundational by each method:")
    top_id = sorted(scores_id.items(), key=lambda x: x[1], reverse=True)[:5]
    top_pr = sorted(scores_pr.items(), key=lambda x: x[1], reverse=True)[:5]
    top_fp = sorted(scores_fp.items(), key=lambda x: x[1], reverse=True)[:5]

    print(f"  In-degree:  {[G.nodes[n].get('heading', n) for n, _ in top_id]}")
    print(f"  PageRank:   {[G.nodes[n].get('heading', n) for n, _ in top_pr]}")
    print(f"  Freq×Pos:   {[G.nodes[n].get('heading', n) for n, _ in top_fp]}")

    # Generate orderings with each tie-breaker
    order_id = topological_sort_with_tiebreak(G, scores_id)
    order_pr = topological_sort_with_tiebreak(G, scores_pr)
    order_fp = topological_sort_with_tiebreak(G, scores_fp)

    # Agreement
    agree_id_pr = sum(1 for a, b in zip(order_id, order_pr) if a == b) / max(len(order_id), 1)
    agree_id_fp = sum(1 for a, b in zip(order_id, order_fp) if a == b) / max(len(order_id), 1)
    agree_pr_fp = sum(1 for a, b in zip(order_pr, order_fp) if a == b) / max(len(order_pr), 1)

    print(f"\nOrdering agreement (position-by-position):")
    print(f"  In-degree vs PageRank:    {agree_id_pr:.0%}")
    print(f"  In-degree vs Freq×Pos:    {agree_id_fp:.0%}")
    print(f"  PageRank vs Freq×Pos:     {agree_pr_fp:.0%}")

    # Kendall tau (rank correlation — better for partial order comparison)
    from scipy.stats import kendalltau
    rank_id = {n: i for i, n in enumerate(order_id)}
    rank_pr = {n: i for i, n in enumerate(order_pr)}
    rank_fp = {n: i for i, n in enumerate(order_fp)}
    nodes = list(G.nodes())

    tau_id_pr, _ = kendalltau([rank_id[n] for n in nodes], [rank_pr[n] for n in nodes])
    tau_id_fp, _ = kendalltau([rank_id[n] for n in nodes], [rank_fp[n] for n in nodes])
    tau_pr_fp, _ = kendalltau([rank_pr[n] for n in nodes], [rank_fp[n] for n in nodes])

    print(f"\nKendall tau rank correlation:")
    print(f"  In-degree vs PageRank:    τ={tau_id_pr:.3f}")
    print(f"  In-degree vs Freq×Pos:    τ={tau_id_fp:.3f}")
    print(f"  PageRank vs Freq×Pos:     τ={tau_pr_fp:.3f}")

    # Show full orderings
    print(f"\nFull orderings:")
    print(f"  In-degree:  {[G.nodes[n].get('heading', n) for n in order_id]}")
    print(f"  PageRank:   {[G.nodes[n].get('heading', n) for n in order_pr]}")
    print(f"  Freq×Pos:   {[G.nodes[n].get('heading', n) for n in order_fp]}")

    return {
        "agree_id_pr": agree_id_pr,
        "agree_id_fp": agree_id_fp,
        "agree_pr_fp": agree_pr_fp,
        "tau_id_pr": tau_id_pr,
        "tau_id_fp": tau_id_fp,
        "tau_pr_fp": tau_pr_fp,
    }


# =============================================================================
# Main
# =============================================================================

def main():
    print("=" * 60)
    print("SPIKE: Ordering Strategy Comparison")
    print("=" * 60)

    # --- Load real graph from reference fixture ---
    fixture_path = Path(__file__).parent.parent / "tests" / "fixtures" / "chunks_reference.json"
    chunks = json.loads(fixture_path.read_text())
    real_result = extract_concepts(chunks, top_n=8)
    real_graph = real_result.graph

    # --- Build synthetic graph ---
    synthetic_graph = build_synthetic_graph()

    # --- Part A: Cycle-breaking ---
    results_a_real = analyze_cycle_breaking(real_graph, "Reference fixture (socket API)")
    results_a_synth = analyze_cycle_breaking(synthetic_graph, "Synthetic (20-node networking)")

    # --- Part B: Foundational scoring ---
    results_b_real = analyze_scoring(real_graph, "Reference fixture (socket API)")
    results_b_synth = analyze_scoring(synthetic_graph, "Synthetic (20-node networking)")

    # --- SCC analysis ---
    print(f"\n{'='*60}")
    print("SCC Module Threshold Analysis")
    print(f"{'='*60}")
    for name, G in [("Reference", real_graph), ("Synthetic", synthetic_graph)]:
        sccs = [c for c in nx.strongly_connected_components(G) if len(c) > 1]
        print(f"\n{name}:")
        print(f"  Non-trivial SCCs: {len(sccs)}")
        for i, scc in enumerate(sccs):
            nodes_str = [G.nodes[n].get("heading", str(n)) for n in scc]
            print(f"    SCC {i+1} (size {len(scc)}): {nodes_str}")
            if len(scc) == 2:
                print(f"      → Recommendation: soft_prereqs (cut weaker edge)")
            else:
                print(f"      → Recommendation: module grouping (no forced internal order)")

    # --- Summary ---
    print(f"\n{'='*60}")
    print("SUMMARY & DECISION")
    print(f"{'='*60}")

    print("\nPart A — Cycle-breaking:")
    if not results_a_real.get("already_dag") and not results_a_synth.get("already_dag"):
        mw_better = (results_a_synth.get("mwfas_weight", 0) < results_a_synth.get("els_weight", 0))
        if mw_better:
            print("  MWFAS preserves more edge weight (removes weaker edges).")
            print("  → RECOMMENDATION: Use MWFAS iterative for cycle-breaking.")
        else:
            print("  ELS removes same or less weight.")
            print("  → RECOMMENDATION: Use Eades-Lin-Smyth (simpler, same quality).")
    elif results_a_real.get("already_dag"):
        print("  Reference fixture is already a DAG. Synthetic comparison determines choice.")

    print("\nPart B — Foundational scoring:")
    avg_tau = (abs(results_b_synth.get("tau_id_pr", 0)) +
               abs(results_b_synth.get("tau_id_fp", 0)) +
               abs(results_b_synth.get("tau_pr_fp", 0))) / 3
    if avg_tau > 0.8:
        print(f"  High agreement (avg τ={avg_tau:.2f}) — methods largely agree.")
        print("  → RECOMMENDATION: Use in-degree (simplest, O(n), nearly equivalent).")
    elif avg_tau > 0.5:
        print(f"  Moderate agreement (avg τ={avg_tau:.2f}).")
        print("  → RECOMMENDATION: Blend in-degree (0.6) + freq×position (0.4).")
    else:
        print(f"  Low agreement (avg τ={avg_tau:.2f}) — methods diverge significantly.")
        print("  → RECOMMENDATION: Needs manual review of disagreement cases.")


if __name__ == "__main__":
    main()
