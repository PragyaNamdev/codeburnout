"""
CodeBurnout - Plotly Visualizations (dark SaaS theme)
"""

import plotly.graph_objects as go

BG   = "rgba(0,0,0,0)"
FONT = dict(family="'DM Mono', monospace", color="#94a3b8")
GRID = "rgba(255,255,255,0.04)"


def _layout(title="", h=None):
    base = dict(
        title=dict(text=title, font=dict(size=13, color="#64748b"), x=0, pad=dict(l=2)),
        paper_bgcolor=BG, plot_bgcolor=BG, font=FONT,
        margin=dict(t=44, b=32, l=32, r=16),
        xaxis=dict(gridcolor=GRID, zerolinecolor=GRID, linecolor=GRID),
        yaxis=dict(gridcolor=GRID, zerolinecolor=GRID, linecolor=GRID),
    )
    if h: base["height"] = h
    return base


def gauge(score: int, level: str) -> go.Figure:
    c = {"Healthy":"#22c55e","Warning":"#f59e0b","High Risk":"#ef4444"}.get(level,"#6366f1")
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"font":{"size":42,"color":c,"family":"DM Mono, monospace"},"suffix":""},
        title={"text": "Burnout Risk Score<br><span style='font-size:11px;color:#475569'>0 = Healthy · 100 = Critical</span>",
               "font":{"size":13,"color":"#64748b"}},
        gauge={
            "axis":{"range":[0,100],"tickwidth":1,"tickcolor":"#1e293b",
                    "tickfont":{"color":"#475569","size":10}},
            "bar":{"color":c,"thickness":0.22},
            "bgcolor":"rgba(0,0,0,0)", "borderwidth":0,
            "steps":[
                {"range":[0,40],  "color":"rgba(34,197,94,0.08)"},
                {"range":[40,70], "color":"rgba(245,158,11,0.08)"},
                {"range":[70,100],"color":"rgba(239,68,68,0.08)"},
            ],
            "threshold":{"line":{"color":c,"width":3},"thickness":0.82,"value":score},
        }
    ))
    fig.update_layout(paper_bgcolor=BG, font=FONT, height=260,
                      margin=dict(t=60,b=20,l=30,r=30))
    return fig


def hour_chart(hour_dist: dict) -> go.Figure:
    hours  = list(hour_dist.keys())
    counts = list(hour_dist.values())
    colors = ["#ef4444" if (h>=22 or h<4) else
              "#f97316" if 4<=h<7 else
              "#22c55e" if 9<=h<18 else "#334155"
              for h in hours]
    fig = go.Figure(go.Bar(
        x=[f"{h:02d}:00" for h in hours], y=counts,
        marker_color=colors, marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>Commits: %{y}<extra></extra>"
    ))
    fig.update_layout(**_layout("⏰ Commit Activity by Hour"), bargap=0.18)
    return fig


def day_chart(day_dist: dict) -> go.Figure:
    colors = ["#f97316" if d in ("Sat","Sun") else "#6366f1"
              for d in day_dist.keys()]
    fig = go.Figure(go.Bar(
        x=list(day_dist.keys()), y=list(day_dist.values()),
        marker_color=colors, marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>Commits: %{y}<extra></extra>"
    ))
    fig.update_layout(**_layout("📅 Commits by Day of Week"), bargap=0.22)
    return fig


def trend_chart(week_dist: dict) -> go.Figure:
    if not week_dist: return go.Figure()
    weeks  = sorted(week_dist.keys())
    counts = [week_dist[w] for w in weeks]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(len(weeks))), y=counts, mode="lines+markers",
        line=dict(color="#6366f1", width=2.5, shape="spline"),
        marker=dict(size=5, color="#818cf8"),
        fill="tozeroy", fillcolor="rgba(99,102,241,0.08)",
        hovertemplate="Week %{x}<br>Commits: %{y}<extra></extra>"
    ))
    fig.update_layout(
        **_layout("📈 Weekly Commit Trend"),
        xaxis=dict(title="", tickvals=list(range(len(weeks))),
                   ticktext=[f"W{i+1}" for i in range(len(weeks))],
                   gridcolor=GRID),
        yaxis=dict(title="Commits", gridcolor=GRID),
    )
    return fig


def donut_chart(f: dict) -> go.Figure:
    ln = f.get("late_night_pct",0)
    em = f.get("early_morn_pct",0)
    wh = f.get("work_hours_pct",0)
    ot = max(0, 100-ln-em-wh)
    fig = go.Figure(go.Pie(
        labels=["Late Night (10PM–4AM)","Early Morning (4–7AM)",
                "Work Hours (9AM–6PM)","Other Hours"],
        values=[ln, em, wh, ot], hole=0.58,
        marker=dict(colors=["#ef4444","#f97316","#22c55e","#334155"],
                    line=dict(color="#080c14", width=2)),
        textinfo="percent", textfont=dict(size=11),
        hovertemplate="<b>%{label}</b><br>%{value:.1f}%<extra></extra>"
    ))
    fig.update_layout(**_layout("🌙 Day vs Night Coding Ratio"),
                      showlegend=True, height=300,
                      margin=dict(t=44,b=10,l=10,r=10),
                      legend=dict(font=dict(size=10,color="#64748b"),
                                  orientation="v", x=1, y=0.5))
    return fig


def radar_chart(f1: dict, f2: dict, u1: str, u2: str) -> go.Figure:
    cats = ["Late Night","Weekend","Neg Sentiment","Overload","Poor Rest","Instability"]
    def v(f):
        return [f.get("late_night_pct",0),
                f.get("weekend_pct",0),
                f.get("neg_commit_pct",0),
                min(f.get("avg_commits_per_day",0)*8,100),
                100-f.get("rest_ratio",0),
                min(f.get("freq_stability",0)*6,100)]
    v1 = v(f1)+[v(f1)[0]]; v2 = v(f2)+[v(f2)[0]]; c = cats+[cats[0]]
    fig = go.Figure()
    for vals, name, col in [(v1,u1,"#6366f1"),(v2,u2,"#f97316")]:
        fig.add_trace(go.Scatterpolar(
            r=vals, theta=c, fill="toself", name=name,
            line=dict(color=col, width=2),
            fillcolor=col.replace("f1","f1").replace("#","rgba(").replace("f1","f1,0.15)") if "6366" in col
                      else f"rgba(249,115,22,0.15)"
        ))
    fig.update_layout(
        polar=dict(bgcolor="rgba(0,0,0,0)",
                   angularaxis=dict(color="#334155", gridcolor=GRID),
                   radialaxis=dict(visible=True,range=[0,100],
                                   color="#334155",gridcolor=GRID)),
        paper_bgcolor=BG, font=FONT, height=360,
        legend=dict(orientation="h",y=-0.12,font=dict(color="#94a3b8")),
        margin=dict(t=30,b=50,l=40,r=40),
    )
    return fig