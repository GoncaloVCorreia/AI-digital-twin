import os, json, requests
from collections import Counter
from typing import Optional, Dict, Any, List
def get_user_repo_summary(username: str, token: Optional[str] = None) -> Dict[str, Any]:
    """
    Return summary for a GitHub user:
      - repo_count (public)
      - repos: [{name, description, language, html_url}]
      - top_languages: [{language, count, percent}]
    """
    s = requests.Session()
    s.headers.update({"Accept": "application/vnd.github+json"})
    if token:
        s.headers.update({"Authorization": f"Bearer {token}"})

    # 1) Verify user exists
    u = s.get(f"https://api.github.com/users/{username}", timeout=15)
    if u.status_code == 404:
        raise ValueError(f"GitHub user '{username}' not found")
    u.raise_for_status()

    # 2) Fetch all public repos (paginate)
    repos: List[Dict[str, Any]] = []
    page = 1
    while True:
        r = s.get(
            f"https://api.github.com/users/{username}/repos",
            params={"per_page": 100, "page": page, "type": "public", "sort": "updated"},
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        if not data:
            break
        for repo in data:
            repos.append({
                "name": repo["name"],
                "description": repo.get("description") or "",
                "language": repo.get("language"),
                "html_url": repo["html_url"],
                "stars": repo.get("stargazers_count", 0),
                "updated_at": repo.get("updated_at"),
            })
        if "next" not in (r.links or {}):
            break
        page += 1

    # 2b) Deduplicate by html_url (defensive)
    seen = set()
    deduped: List[Dict[str, Any]] = []
    for r in repos:
        if r["html_url"] in seen:
            continue
        seen.add(r["html_url"])
        deduped.append(r)

    # Stable sort: stars desc, then name asc
    deduped.sort(key=lambda x: (-x["stars"], x["name"].lower()))

    # 3) Top languages by primary language across repos
    lang_counts = Counter(r["language"] for r in deduped if r["language"])
    total = sum(lang_counts.values()) or 1
    top_languages = [
        {"language": lang, "count": cnt, "percent": round(100 * cnt / total, 2)}
        for lang, cnt in lang_counts.most_common()
    ]

    # keep only requested fields in repos
    repos_min = [
        {k: r[k] for k in ("name", "description", "language", "html_url")}
        for r in deduped
    ]

    return {
        "user": username,
        "repo_count": len(repos_min),
        "repos": repos_min,
        "top_languages": top_languages,
    }