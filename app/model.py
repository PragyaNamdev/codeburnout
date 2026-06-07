"""
CodeBurnout — Scoring Engine
Rule-based burnout scoring, AI insight generation, and burnout forecast.
No ML training required — signals are weighted from peer-reviewed burnout research.
"""


# ── Burnout Risk Scorer ────────────────────────────────────────────────────────

def calculate_burnout_score(f: dict) -> dict:
    """
    Compute burnout risk score (0–100) and categorize risk level.

    Returns a dict with score, level, color, emoji, advice,
    reasons (list of (title, detail) tuples), and positives.
    """
    score = 0
    reasons: list[tuple[str, str]] = []
    positives: list[tuple[str, str]] = []

    ln    = f.get("late_night_pct", 0)
    em    = f.get("early_morning_pct", 0)
    wk    = f.get("weekend_pct", 0)
    neg   = f.get("neg_commit_pct", 0)
    apd   = f.get("avg_commits_per_day", 0)
    mpd   = f.get("max_commits_in_a_day", 0)
    rr    = f.get("rest_ratio", 100)
    fstab = f.get("freq_stability", 0)
    sd    = f.get("sentiment_declining", False)
    spk   = f.get("spike_days_count", 0)
    gap   = f.get("longest_gap_days", 0)

    # ── Late-night activity (max 28 pts) ──────────────────────────────────────
    if ln >= 40:
        score += 28
        reasons.append(("🌙 Extreme late-night coding", f"{ln}% of commits after 10 PM"))
    elif ln >= 25:
        score += 18
        reasons.append(("🌙 Heavy night-time pattern", f"{ln}% of commits after 10 PM"))
    elif ln >= 12:
        score += 8
        reasons.append(("🌙 Moderate late-night activity", f"{ln}% after 10 PM"))
    else:
        positives.append(("✅ Healthy coding hours", "Mostly active during daytime"))

    # ── Early morning sessions (max 10 pts) ───────────────────────────────────
    if em >= 15:
        score += 10
        reasons.append(("🌅 Sleep disruption detected", f"{em}% of commits at 4–7 AM"))
    elif em >= 8:
        score += 5
        reasons.append(("🌅 Early morning sessions", f"{em}% commits at 4–7 AM"))

    # ── Weekend overwork (max 18 pts) ─────────────────────────────────────────
    if wk >= 55:
        score += 18
        reasons.append(("📅 No work-life boundary", f"{wk}% of commits on weekends"))
    elif wk >= 35:
        score += 11
        reasons.append(("📅 High weekend activity", f"{wk}% commits on weekends"))
    elif wk >= 18:
        score += 5
        reasons.append(("📅 Moderate weekend coding", f"{wk}% on weekends"))
    else:
        positives.append(("✅ Strong work-life balance", "Weekends mostly kept clear"))

    # ── Negative commit sentiment (max 15 pts) ────────────────────────────────
    if neg >= 50:
        score += 15
        reasons.append(("😤 High frustration in commits", f"{neg}% messages signal stress"))
    elif neg >= 30:
        score += 9
        reasons.append(("😤 Elevated stress signaling", f"{neg}% negative commit messages"))
    elif neg >= 15:
        score += 4
        reasons.append(("😤 Mild negativity detected", f"{neg}% messages carry negative tone"))
    else:
        positives.append(("✅ Positive commit language", "Messages are mostly constructive"))

    # ── Sentiment trend (max 10 pts) ──────────────────────────────────────────
    if sd:
        score += 10
        reasons.append(("📉 Declining motivation trend", "Recent messages more negative than baseline"))
    else:
        positives.append(("✅ Stable sentiment trend", "Commit mood is not worsening"))

    # ── Output pace / overwork (max 14 pts) ───────────────────────────────────
    if apd >= 12:
        score += 14
        reasons.append(("⚡ Extreme output pace", f"Averaging {apd} commits/day"))
    elif apd >= 6:
        score += 7
        reasons.append(("⚡ High output pace", f"Averaging {apd} commits/day"))
    else:
        positives.append(("✅ Sustainable output pace", f"{apd} commits/day average"))

    if mpd >= 25:
        score += 5
        reasons.append(("⚡ Crunch day detected", f"Peak of {mpd} commits in a single day"))

    if spk >= 4:
        score += 5
        reasons.append(("📈 Multiple intensity spikes", f"{spk} high-output days detected"))

    # ── Rest day deficit (max 10 pts) ─────────────────────────────────────────
    if rr < 10:
        score += 10
        reasons.append(("😴 Critical rest deficit", f"Only {rr}% of days without commits"))
    elif rr < 25:
        score += 5
        reasons.append(("😴 Low rest ratio", f"{rr}% rest day ratio"))
    else:
        positives.append(("✅ Adequate rest days", f"{rr}% of days were commit-free"))

    # ── Frequency instability (max 5 pts) ─────────────────────────────────────
    if fstab >= 8:
        score += 5
        reasons.append(("🎢 Highly unstable workload", "Extreme swings in daily commit volume"))
    elif fstab >= 4:
        score += 2
        reasons.append(("🎢 Variable commit pace", "Noticeable fluctuation in daily output"))

    # ── Long gap bonus (reduces urgency) ──────────────────────────────────────
    if gap >= 14:
        positives.append(("🌿 Extended rest period found", f"{gap} consecutive days without commits"))

    score = min(score, 100)

    if score >= 71:
        level, color, emoji = "High Risk", "#EF4444", "🔴"
        advice = "Serious burnout signals present. Urgent: take a real break and protect your sleep."
    elif score >= 41:
        level, color, emoji = "Warning", "#F59E0B", "🟡"
        advice = "Burnout patterns emerging. Set clear work boundaries and prioritize rest."
    else:
        level, color, emoji = "Healthy", "#10B981", "🟢"
        advice = "Your developer health looks solid. Maintain this sustainable rhythm."

    return {
        "score":     score,
        "level":     level,
        "color":     color,
        "emoji":     emoji,
        "advice":    advice,
        "reasons":   reasons,
        "positives": positives,
    }


# ── Insight Engine ────────────────────────────────────────────────────────────

def generate_insights(f: dict, result: dict) -> list[str]:
    """
    Generate a list of human-language AI insight strings from features.
    Each insight is a full, meaningful sentence targeted to the developer.
    """
    insights: list[str] = []

    ln    = f.get("late_night_pct", 0)
    wk    = f.get("weekend_pct", 0)
    rr    = f.get("rest_ratio", 100)
    neg   = f.get("neg_commit_pct", 0)
    apd   = f.get("avg_commits_per_day", 0)
    fstab = f.get("freq_stability", 0)
    sd    = f.get("sentiment_declining", False)
    wh    = f.get("work_hours_pct", 0)
    trend = f.get("activity_trend_pct", 0)
    gap   = f.get("longest_gap_days", 0)
    strk  = f.get("current_streak", 0)

    # Late-night pattern
    if ln >= 30:
        insights.append(
            f"🌙 You are highly active during late-night hours — {ln}% of your commits happen after 10 PM. "
            "Research consistently shows that chronic late-night coding is one of the strongest early indicators of developer burnout."
        )
    elif ln >= 15:
        insights.append(
            f"🌙 Night-owl tendencies detected — {ln}% of commits fall after 10 PM. "
            "Occasional late sessions are fine, but making this a nightly pattern degrades decision quality and creativity over time."
        )
    else:
        insights.append(
            f"☀️ You code primarily during healthy hours — {wh}% of activity falls within standard work hours. "
            "This is a strong sustainability signal and one of the best habits a developer can have."
        )

    # Weekend activity
    if wk >= 40:
        insights.append(
            f"📅 Weekend work is dominating your schedule at {wk}% of all commits. "
            "When weekends stop being recovery time, burnout escalates significantly — usually within 3–6 weeks."
        )
    elif wk >= 20:
        insights.append(
            f"📅 You are active on {wk}% of weekends. "
            "Some weekend work is common among passionate developers, but watch for upward creep in this metric."
        )
    else:
        insights.append(
            f"📅 Your weekends are largely commit-free ({wk}%). "
            "This is an excellent work-life boundary that protects long-term productivity and mental health."
        )

    # Rest days
    if rr < 15:
        insights.append(
            f"😴 Rest day deficit detected — only {rr}% of your tracked period had zero commits. "
            "Recovery time is not laziness; it is when memory consolidation, creative thinking, and motivation are restored."
        )
    elif rr >= 40:
        insights.append(
            f"🌿 You maintain a healthy rest rhythm with {rr}% downtime days. "
            "Deliberate recovery is built into your workflow — this is rare and directly supports sustained high performance."
        )

    # Frequency stability
    if fstab >= 6:
        insights.append(
            "🎢 Your workload pattern is highly unstable — oscillating between intense crunch and complete silence. "
            "This kind of feast-or-famine pattern is mentally exhausting even when total output looks acceptable."
        )
    elif fstab >= 3:
        insights.append(
            "🎢 Your commit frequency fluctuates moderately. "
            "Aiming for a steadier daily pace — even if lower — tends to produce better outcomes than variable intensity."
        )
    else:
        insights.append(
            "📊 Your commit frequency is remarkably consistent day-over-day. "
            "This kind of steady cadence is a hallmark of sustainable, high-performing engineering practice."
        )

    # Sentiment trend
    if sd:
        insights.append(
            "📉 Your recent commit messages carry more negative language than your historical baseline. "
            "This linguistic shift — more 'fix', 'broken', 'hack', 'revert' — is a subtle but reliable early burnout signal."
        )
    else:
        insights.append(
            "💬 Your commit message sentiment is stable or improving. "
            "The language developers use in commits is a surprisingly accurate wellbeing signal — yours is trending positively."
        )

    # Negative commits
    if neg >= 40:
        insights.append(
            f"😤 {neg}% of your commits carry frustration markers such as 'fix', 'broken', 'revert', or 'hack'. "
            "A high bug-fix ratio often signals accumulating technical debt — which itself compounds cognitive load and stress."
        )

    # Activity trend
    if trend <= -25:
        insights.append(
            f"📉 Your activity dropped {abs(trend):.0f}% in the last 2 weeks versus the prior period. "
            "This could be healthy recovery — or early disengagement. Monitor whether the trend continues."
        )
    elif trend >= 40:
        insights.append(
            f"📈 You accelerated {trend:.0f}% in the last 2 weeks. "
            "Rapid acceleration often precedes a burnout crash. Pace is a feature, not a limitation."
        )

    # Streak
    if strk >= 14:
        insights.append(
            f"🔥 You are on a {strk}-day commit streak. Impressive consistency — "
            "but make sure streak-chasing is not overriding your genuine need for rest."
        )

    # Overall assessment
    if result["score"] <= 30:
        insights.append(
            "🏆 Overall: You are among the healthiest developer profiles we have analyzed. "
            "Your habits — timing, frequency, rest, and commit sentiment — align well with what research shows about sustainable high performance."
        )
    elif result["score"] >= 70:
        insights.append(
            "⚠️ Overall: Multiple compounding burnout signals are present simultaneously. "
            "This is not just fatigue — chronic patterns like these measurably degrade code quality, decision-making, creativity, and long-term career health."
        )

    return insights


# ── Burnout Forecast ──────────────────────────────────────────────────────────

def generate_forecast(f: dict, result: dict) -> dict:
    """
    Predict when burnout risk will peak if current patterns continue.
    Returns days estimate, severity label, forecast message, and action.
    """
    score = result["score"]
    trend = f.get("activity_trend_pct", 0)
    ln    = f.get("late_night_pct", 0)

    if score >= 71:
        days = "7–10 days" if (trend >= 20 or ln >= 40) else "10–15 days"
        severity = "critical"
        message = (
            f"⚠️ At the current trajectory, full burnout may manifest in **{days}**. "
            "Immediate intervention is recommended."
        )
        action = (
            "Take at least 3 consecutive rest days now. "
            "Set a hard stop time of 9 PM for all coding. "
            "Talk to your manager or a trusted peer about workload."
        )

    elif score >= 41:
        days = "15–20 days" if trend >= 30 else "20–30 days"
        severity = "medium"
        message = (
            f"📊 Burnout risk escalates to high in **{days}** if patterns don't change."
        )
        action = (
            "Establish a daily coding stop time. "
            "Protect at least 1.5 full rest days per week. "
            "Review your current task load and defer non-critical work."
        )

    else:
        days = "60+ days"
        severity = "low"
        message = "🟢 No burnout risk forecast for the next **60+ days** at current patterns."
        action = (
            "Maintain current pace and rest habits. "
            "Watch for any sudden increase in late-night or weekend activity."
        )

    return {
        "days":     days,
        "severity": severity,
        "message":  message,
        "action":   action,
    }


# ── Developer Health Score ────────────────────────────────────────────────────

def developer_health_score(burnout_score: int) -> dict:
    """
    Compute an overall developer health score (inverse of burnout score).
    Returns score, letter grade, and descriptive label.
    """
    health = 100 - burnout_score

    if health >= 75:
        grade, label = "A", "Excellent"
    elif health >= 60:
        grade, label = "B", "Good"
    elif health >= 45:
        grade, label = "C", "Fair"
    elif health >= 30:
        grade, label = "D", "Poor"
    else:
        grade, label = "F", "Critical"

    return {"score": health, "grade": grade, "label": label}


# ── AI Recommendations ────────────────────────────────────────────────────────

def generate_recommendations(f: dict, result: dict) -> list[dict]:
    """
    Generate a prioritized list of actionable developer health recommendations.
    Each item has: priority (High/Medium/Low), icon, title, description.
    """
    recs: list[dict] = []
    ln   = f.get("late_night_pct", 0)
    wk   = f.get("weekend_pct", 0)
    rr   = f.get("rest_ratio", 100)
    apd  = f.get("avg_commits_per_day", 0)
    sd   = f.get("sentiment_declining", False)

    if ln >= 20:
        recs.append({
            "priority": "High",
            "icon": "🌙",
            "title": "Enforce a coding curfew",
            "description": f"Set 9 PM as a hard stop for all coding. Your late-night rate of {ln}% is actively degrading sleep quality and decision-making.",
        })

    if wk >= 30:
        recs.append({
            "priority": "High",
            "icon": "🛑",
            "title": "Protect your weekends",
            "description": f"Designate at least one full weekend day as no-code time. At {wk}% weekend activity, you are losing critical recovery time.",
        })

    if rr < 25:
        recs.append({
            "priority": "High" if rr < 10 else "Medium",
            "icon": "🌿",
            "title": "Schedule deliberate rest days",
            "description": f"Only {rr}% of your days were commit-free. Aim for at least 2 full rest days per week — not catch-up days, actual recovery days.",
        })

    if apd >= 8:
        recs.append({
            "priority": "Medium",
            "icon": "📊",
            "title": "Set a daily commit limit",
            "description": f"Averaging {apd} commits/day suggests possible task fragmentation or compulsive committing. Batch related changes together.",
        })

    if sd:
        recs.append({
            "priority": "Medium",
            "icon": "💬",
            "title": "Address the frustration source",
            "description": "Your commit messages are trending more negative over time. This often signals technical debt accumulation or unclear requirements — both worth addressing directly.",
        })

    if result["score"] >= 60:
        recs.append({
            "priority": "High",
            "icon": "🤝",
            "title": "Talk to someone",
            "description": "At this risk level, having a direct conversation with your manager, tech lead, or trusted peer about workload is one of the highest-impact actions you can take.",
        })

    if result["score"] <= 30:
        recs.append({
            "priority": "Low",
            "icon": "📈",
            "title": "Document your healthy habits",
            "description": "Your patterns are genuinely sustainable. Write down what is working — your future self (and teammates) will thank you.",
        })

    if not recs:
        recs.append({
            "priority": "Low",
            "icon": "✅",
            "title": "Maintain current patterns",
            "description": "No significant issues detected. Keep monitoring your habits and watch for gradual shifts in timing or pace.",
        })

    return recs