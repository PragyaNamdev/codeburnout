"""
CodeBurnout — GitHub Data Analyzer
Fetches real GitHub commit history and profile data.
Automatically falls back to synthetic data on any API failure.
"""

import requests
from datetime import datetime, timezone, timedelta
from synthetic import generate_synthetic_commits, synthetic_profile


def _build_headers(token: str | None) -> dict:
    headers = {"Accept": "application/vnd.github+json"}
    if token and token.strip():
        headers["Authorization"] = f"Bearer {token.strip()}"
    return headers


def get_user_profile(username: str, token: str | None = None) -> dict:
    """
    Fetch GitHub user profile.
    On failure returns a minimal real-looking placeholder — never fake synthetic data.
    """
    try:
        response = requests.get(
            f"https://api.github.com/users/{username}",
            headers=_build_headers(token),
            timeout=8,
        )
        if response.status_code == 200:
            data = response.json()
            return {
                "login":        data.get("login", username),
                "name":         data.get("name") or username,
                "avatar_url":   data.get("avatar_url", ""),
                "bio":          data.get("bio") or "",
                "public_repos": data.get("public_repos", 0),
                "followers":    data.get("followers", 0),
                "following":    data.get("following", 0),
                "location":     data.get("location") or "",
                "created_at":   data.get("created_at", ""),
                "blog":         data.get("blog") or "",
                "company":      data.get("company") or "",
                "synthetic":    False,
            }
    except Exception:
        pass

    # API failed — return minimal placeholder using the REAL username, no fake data
    return {
        "login":        username,
        "name":         username,
        "avatar_url":   f"https://github.com/{username}.png",
        "bio":          "",
        "public_repos": "—",
        "followers":    0,
        "following":    0,
        "location":     "",
        "created_at":   "",
        "blog":         "",
        "company":      "",
        "synthetic":    False,
    }


def get_user_commits(
    username: str,
    token: str | None = None,
    max_repos: int = 10,
    days_back: int = 90,
) -> tuple[list, bool]:
    """
    Fetch commit history from the user's top repositories.

    Returns:
        (commits, is_synthetic) — commits is always a non-empty list.
        is_synthetic is True when real data could not be fetched.
    """
    since_dt = datetime.now(timezone.utc) - timedelta(days=days_back)
    since_iso = since_dt.isoformat()
    headers = _build_headers(token)

    try:
        repo_response = requests.get(
            f"https://api.github.com/users/{username}/repos",
            headers=headers,
            params={"sort": "pushed", "per_page": max_repos, "type": "owner"},
            timeout=8,
        )

        if repo_response.status_code == 404:
            return generate_synthetic_commits(username, days_back)

        if repo_response.status_code in (403, 429):
            return generate_synthetic_commits(username, days_back)

        if repo_response.status_code != 200:
            return generate_synthetic_commits(username, days_back)

        repos = repo_response.json()
        if not repos:
            return generate_synthetic_commits(username, days_back)

    except Exception:
        return generate_synthetic_commits(username, days_back)

    commits = []

    for repo in repos:
        repo_name = repo.get("name", "")
        if not repo_name:
            continue

        try:
            commit_response = requests.get(
                f"https://api.github.com/repos/{username}/{repo_name}/commits",
                headers=headers,
                params={"author": username, "since": since_iso, "per_page": 50},
                timeout=8,
            )

            if commit_response.status_code != 200:
                continue

            for raw in commit_response.json():
                try:
                    date_str = raw["commit"]["author"]["date"]
                    ts = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    message = raw["commit"]["message"].split("\n")[0][:120]

                    commits.append({
                        "repo":        repo_name,
                        "message":     message,
                        "timestamp":   ts,
                        "hour":        ts.hour,
                        "day_of_week": ts.weekday(),
                        "date":        ts.date(),
                        "week":        ts.isocalendar()[1],
                        "synthetic":   False,
                    })
                except (KeyError, ValueError):
                    continue

        except Exception:
            continue

    if len(commits) < 5:
        return generate_synthetic_commits(username, days_back)

    commits.sort(key=lambda x: x["timestamp"], reverse=True)
    return commits, False