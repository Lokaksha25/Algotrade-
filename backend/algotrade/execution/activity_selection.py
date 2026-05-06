"""
AlgoTrade Engine — Activity Selection
Selects maximum number of non-overlapping trades.

DAA Paradigm: Greedy Algorithm
Brute-force: O(2^n) subset enumeration  |  Greedy: O(n log n) sort + linear scan
Greedy is provably optimal via exchange argument.
"""

from itertools import combinations


def activity_selection_brute(activities: list[dict]) -> list[dict]:
    """
    Brute-force: enumerate all subsets, find largest non-overlapping set.
    Time: O(2^n · n)  — only feasible for n ≤ 25
    
    Each activity: {"id": int, "start": int, "end": int, "value": float}
    """
    n = len(activities)
    best = []

    for r in range(n, 0, -1):
        for combo in combinations(range(n), r):
            selected = [activities[i] for i in combo]
            selected_sorted = sorted(selected, key=lambda a: a["end"])

            # Check non-overlapping
            valid = True
            for i in range(1, len(selected_sorted)):
                if selected_sorted[i]["start"] < selected_sorted[i - 1]["end"]:
                    valid = False
                    break

            if valid and len(selected) > len(best):
                best = selected
                if len(best) == r:
                    return sorted(best, key=lambda a: a["start"])

    return sorted(best, key=lambda a: a["start"])


def activity_selection_greedy(activities: list[dict]) -> list[dict]:
    """
    Greedy Activity Selection — sort by end time, select non-overlapping.
    Time: O(n log n) for sorting + O(n) linear scan = O(n log n)

    Proof of optimality: Exchange argument — swapping any selected activity
    with an unselected one that ends later cannot increase the count.
    """
    if not activities:
        return []

    # Sort by end time (finish time)
    sorted_acts = sorted(activities, key=lambda a: a["end"])

    selected = [sorted_acts[0]]
    last_end = sorted_acts[0]["end"]

    for act in sorted_acts[1:]:
        if act["start"] >= last_end:  # Non-overlapping
            selected.append(act)
            last_end = act["end"]

    return selected


def format_trades_as_activities(signals: list[dict]) -> list[dict]:
    """Convert trade signals to activity format for scheduling."""
    activities = []
    for i, sig in enumerate(signals):
        activities.append({
            "id": i,
            "start": sig.get("buy_idx", sig.get("entry_idx", 0)),
            "end": sig.get("sell_idx", sig.get("exit_idx", 0)),
            "value": sig.get("profit_pct", sig.get("expected_return", 0)),
            "ticker": sig.get("ticker", ""),
        })
    return activities
