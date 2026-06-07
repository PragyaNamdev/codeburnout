"""
CodeBurnout — Feature Engineering
Extracts all burnout-relevant behavioral signals from raw commit data.
"""

import statistics
from collections import Counter, defaultdict
from datetime import date, timedelta


# ── Sentiment word sets ────────────────────────────────────────────────────────

NEGATIVE_WORDS = {
    "fix", "bug", "error", "fail", "crash", "broken", "revert", "wrong",
    "issue", "problem", "critical", "hotfix", "urgent", "hack", "temp",
    "bad", "disaster", "oops", "sorry", "conflict", "force", "stupid",
    "mess", "wip", "tired", "debug", "patch", "workaround", "undo",
}

POSITIVE_WORDS = {
    "add", "feat", "feature", "improve", "update", "refactor", "clean",
    "optimize", "enhance", "complete", "done", "release", "launch",
    "implement", "create", "build", "success", "merge", "nice", "great",
    "initial", "setup", "deploy", "ship", "finish", "resolve", "upgrade",
}


def _sentiment_score(message: str) -> float:
    """
    Rule-based sentiment score in range [-1.0, +1.0].
    Positive = constructive commit, Negative = stress/frustration.
    """
    words = set(message.lower().split())
    neg_count = len(words & NEGATIVE_WORDS)
    pos_count = len(words & POSITIVE_WORDS)
    total = neg_count + pos_count
    if total == 0:
        return 0.0
    return round((pos_count - neg_count) / total, 3)


def extract_features(commits: list) -> dict:
    """
    Extract a comprehensive feature dict from a list of commit records.
    All values are safe to use directly in scoring and visualizations.
    """
    if not commits:
        return {}

    total = len(commits)
    dates = [c["date"] for c in commits]
    unique_days = sorted(set(dates))
    date_counts = Counter(dates)

    # ── Timing categories ─────────────────────────────────────────────────────
    late_night   = [c for c in commits if c["hour"] >= 22 or c["hour"] < 4]
    early_morning = [c for c in commits if 4 <= c["hour"] < 7]
    work_hours   = [c for c in commits if 9 <= c["hour"] < 18]
    weekend_commits = [c for c in commits if c["day_of_week"] >= 5]

    late_night_pct   = round(len(late_night)    / total * 100, 1)
    early_morning_pct = round(len(early_morning) / total * 100, 1)
    work_hours_pct   = round(len(work_hours)     / total * 100, 1)
    weekend_pct      = round(len(weekend_commits)/ total * 100, 1)

    # ── Frequency statistics ──────────────────────────────────────────────────
    avg_per_day = round(total / max(len(unique_days), 1), 2)
    max_per_day = max(date_counts.values())
    daily_values = list(date_counts.values())
    freq_stability = round(
        statistics.stdev(daily_values) if len(daily_values) > 1 else 0.0, 2
    )

    # Spike days: days with more than 2.5x average and at least 5 commits
    spike_days = [
        d for d, cnt in date_counts.items()
        if cnt >= max(avg_per_day * 2.5, 5)
    ]

    # ── Rest day analysis ─────────────────────────────────────────────────────
    if len(unique_days) >= 2:
        span_days: set = set()
        cursor = unique_days[0]
        while cursor <= unique_days[-1]:
            span_days.add(cursor)
            cursor += timedelta(days=1)

        rest_count = len(span_days - set(unique_days))
        total_span = (unique_days[-1] - unique_days[0]).days + 1
        rest_ratio = round(rest_count / max(total_span, 1) * 100, 1)

        gaps = []
        prev = unique_days[0]
        for d in unique_days[1:]:
            gap = (d - prev).days - 1
            if gap > 0:
                gaps.append(gap)
            prev = d
        longest_gap = max(gaps) if gaps else 0
    else:
        rest_ratio = 50.0
        longest_gap = 0

    # ── Sentiment analysis ────────────────────────────────────────────────────
    sentiments = [_sentiment_score(c["message"]) for c in commits]
    avg_sentiment = round(sum(sentiments) / total, 3)
    neg_commit_pct = round(
        sum(1 for s in sentiments if s < 0) / total * 100, 1
    )

    half = max(total // 2, 1)
    recent_sentiment = round(sum(sentiments[:half])  / half, 3)
    older_sentiment  = round(sum(sentiments[half:])  / max(total - half, 1), 3)
    sentiment_declining = recent_sentiment < older_sentiment - 0.05

    # ── Distribution maps ─────────────────────────────────────────────────────
    hour_distribution = {h: 0 for h in range(24)}
    for c in commits:
        hour_distribution[c["hour"]] += 1

    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    day_distribution = {name: 0 for name in day_names}
    for c in commits:
        day_distribution[day_names[c["day_of_week"]]] += 1

    week_distribution: dict = defaultdict(int)
    for c in commits:
        week_distribution[c["week"]] += 1

    # ── Short-term activity trend ─────────────────────────────────────────────
    today = date.today()
    last_2w  = sum(1 for c in commits if (today - c["date"]).days <= 14)
    prior_2w = sum(1 for c in commits if 14 < (today - c["date"]).days <= 28)
    activity_trend_pct = round(
        (last_2w - prior_2w) / max(prior_2w, 1) * 100, 1
    )

    # ── Productivity streak ───────────────────────────────────────────────────
    active_set = set(unique_days)
    current_streak = 0
    best_streak = 0
    running = 0

    for offset in range((today - unique_days[0]).days + 2):
        check = today - timedelta(days=offset)
        if check in active_set:
            running += 1
            if offset == 0 or current_streak == 0:
                current_streak = running
            best_streak = max(best_streak, running)
        else:
            if offset == 0:
                current_streak = 0
            running = 0

    # ── Repository breakdown ──────────────────────────────────────────────────
    repo_counts = Counter(c["repo"] for c in commits)
    top_repos = dict(repo_counts.most_common(6))

    return {
        "total_commits":       total,
        "unique_active_days":  len(unique_days),
        "avg_commits_per_day": avg_per_day,
        "max_commits_in_a_day": max_per_day,
        "freq_stability":      freq_stability,
        "late_night_pct":      late_night_pct,
        "early_morning_pct":   early_morning_pct,
        "work_hours_pct":      work_hours_pct,
        "weekend_pct":         weekend_pct,
        "rest_ratio":          rest_ratio,
        "longest_gap_days":    longest_gap,
        "spike_days_count":    len(spike_days),
        "avg_sentiment":       avg_sentiment,
        "recent_sentiment":    recent_sentiment,
        "older_sentiment":     older_sentiment,
        "sentiment_declining": sentiment_declining,
        "neg_commit_pct":      neg_commit_pct,
        "hour_distribution":   hour_distribution,
        "day_distribution":    day_distribution,
        "week_distribution":   dict(week_distribution),
        "activity_trend_pct":  activity_trend_pct,
        "last_2w_commits":     last_2w,
        "prior_2w_commits":    prior_2w,
        "current_streak":      current_streak,
        "best_streak":         best_streak,
        "top_repos":           top_repos,
    }