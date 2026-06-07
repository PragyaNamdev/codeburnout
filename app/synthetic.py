"""
CodeBurnout — Synthetic Data Engine
Generates realistic GitHub activity data for demo mode and API fallback.
Ensures the dashboard is never empty or broken.
"""

import random
from datetime import date, datetime, timedelta, timezone


ARCHETYPES = {
    "night_owl": {
        "hour_weights": [4,4,5,4,3,2,1,1,2,3,4,4,5,5,4,4,4,5,6,7,8,9,9,7],
        "daily_options": [0,0,1,2,3,4,6,8],
        "daily_weights": [25,15,15,15,12,10,5,3],
        "weekend_factor": 0.6,
        "label": "Night Owl",
    },
    "overworked": {
        "hour_weights": [2,2,2,2,1,1,2,4,6,7,8,8,7,7,7,7,6,6,6,7,8,8,7,5],
        "daily_options": [0,2,4,6,8,10,14,18],
        "daily_weights": [8,12,18,20,18,12,8,4],
        "weekend_factor": 0.85,
        "label": "Overworked",
    },
    "weekend_warrior": {
        "hour_weights": [1,1,1,1,1,1,2,3,5,6,7,7,6,6,6,6,5,4,4,4,3,2,2,1],
        "daily_options": [0,1,2,3,5],
        "daily_weights": [40,25,20,10,5],
        "weekend_factor": 2.5,
        "label": "Weekend Warrior",
    },
    "balanced": {
        "hour_weights": [1,1,1,1,1,1,1,2,5,8,9,9,8,8,8,8,7,6,5,4,3,2,2,1],
        "daily_options": [0,1,2,3,4],
        "daily_weights": [30,28,25,12,5],
        "weekend_factor": 0.3,
        "label": "Balanced",
    },
}

POSITIVE_MESSAGES = [
    "feat: add user authentication module",
    "feat: implement dashboard analytics",
    "refactor: clean up API layer for clarity",
    "feat: complete search functionality",
    "release: version 2.1.0",
    "improve: optimize database query performance",
    "feat: add dark mode toggle",
    "docs: update README with setup guide",
    "feat: implement notification system",
    "build: upgrade all dependencies",
    "feat: add CSV export functionality",
    "refactor: modularize core components",
    "feat: integrate payment gateway",
    "improve: enhance mobile responsiveness",
    "feat: implement real-time updates",
    "chore: setup CI/CD pipeline",
    "feat: add user profile page",
    "improve: reduce bundle size by 40%",
    "feat: complete onboarding flow",
    "refactor: extract shared utilities",
]

NEGATIVE_MESSAGES = [
    "fix: resolve critical production bug",
    "hotfix: patch broken authentication",
    "revert: undo breaking change from yesterday",
    "fix: why is this still not working",
    "temp: hacky fix to unblock deployment",
    "fix: resolve race condition in API",
    "debug: adding logs to find the issue",
    "fix: broken tests after refactor",
    "hotfix: emergency patch for login crash",
    "fix: revert broken migration script",
    "fix: resolve memory leak in event loop",
    "wip: still debugging this mess",
    "fix: another attempt at fixing this",
]

REPOS = [
    "portfolio-site", "api-server", "ml-experiments",
    "side-project", "personal-blog", "dotfiles",
    "open-source-contrib", "data-pipeline", "mobile-app",
]


def generate_synthetic_commits(username: str = "demo_user", days: int = 90) -> list:
    """
    Generate realistic commit data mimicking real developer archetypes.
    Returns a list of commit dicts compatible with the real analyzer output.
    """
    seed = abs(hash(username)) % 99991
    random.seed(seed)
    archetype_key = random.choice(list(ARCHETYPES.keys()))
    arch = ARCHETYPES[archetype_key]
    commits = []
    today = date.today()
    user_repos = random.sample(REPOS, k=min(5, len(REPOS)))

    for day_offset in range(days):
        current_date = today - timedelta(days=day_offset)
        weekday = current_date.weekday()
        is_weekend = weekday >= 5

        base_count = random.choices(
            arch["daily_options"],
            weights=arch["daily_weights"]
        )[0]

        if is_weekend:
            factor = arch["weekend_factor"]
            count = int(round(base_count * factor))
        else:
            count = base_count

        for _ in range(count):
            hour = random.choices(
                list(range(24)),
                weights=arch["hour_weights"]
            )[0]
            minute = random.randint(0, 59)
            second = random.randint(0, 59)

            is_late = hour >= 22 or hour < 4
            use_negative = (
                is_late and archetype_key in ("night_owl", "overworked")
                and random.random() < 0.55
            ) or (random.random() < 0.18)

            message = random.choice(NEGATIVE_MESSAGES if use_negative else POSITIVE_MESSAGES)
            repo = random.choice(user_repos)

            ts = datetime(
                current_date.year, current_date.month, current_date.day,
                hour, minute, second, tzinfo=timezone.utc
            )
            commits.append({
                "repo": repo,
                "message": message,
                "timestamp": ts,
                "hour": hour,
                "day_of_week": weekday,
                "date": current_date,
                "week": ts.isocalendar()[1],
                "synthetic": True,
            })

    commits.sort(key=lambda x: x["timestamp"], reverse=True)
    return commits, archetype_key


def synthetic_profile(username: str) -> dict:
    """
    Generate a realistic-looking GitHub profile for demo/fallback mode.
    """
    seed = abs(hash(username)) % 99991
    random.seed(seed)

    names = [
        "Alex Chen", "Jordan Smith", "Sam Rivera", "Taylor Kim",
        "Morgan Lee", "Casey Wang", "Riley Johnson", "Drew Patel",
        "Avery Zhang", "Quinn Nakamura",
    ]
    bios = [
        "Full-stack developer · Open source enthusiast · Coffee addict",
        "Building things for the web · Always learning",
        "Software engineer · Passionate about clean code",
        "Developer by day, debugger by night",
        "Code, ship, repeat · Previously @bigtech",
    ]
    locations = [
        "San Francisco, CA", "Berlin, Germany", "Bengaluru, India",
        "Toronto, Canada", "Remote 🌍", "London, UK", "Amsterdam, NL",
    ]

    return {
        "login": username,
        "name": random.choice(names),
        "avatar_url": f"https://api.dicebear.com/7.x/avataaars/svg?seed={username}&backgroundColor=b6e3f4",
        "bio": random.choice(bios),
        "public_repos": random.randint(14, 92),
        "followers": random.randint(45, 1200),
        "following": random.randint(20, 300),
        "location": random.choice(locations),
        "created_at": "2019-06-12T00:00:00Z",
        "synthetic": True,
    }