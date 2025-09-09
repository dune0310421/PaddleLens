from datetime import datetime, timedelta, timezone

import requests


def fetch_total_releases(token, owner, repo, days=None):
    all_releases = []
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}",
    }
    url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    params = {
        "per_page": 100,
        "page": 1,
    }
    while True:
        r = requests.get(url, headers=headers, params=params)
        r.raise_for_status()
        data = r.json()

        if not data:
            break

        all_releases.extend(data)
        params["page"] += 1

    total_count = len(all_releases)

    recent_count = 0

    if days:
        since_date = datetime.now(timezone.utc) - timedelta(days=days)
        for release in all_releases:
            created = datetime.fromisoformat(
                release["created_at"].replace("Z", "+00:00")
            )
            if created >= since_date:
                recent_count += 1

    return total_count, recent_count


if __name__ == "__main__":
    import os

    from dotenv import load_dotenv

    load_dotenv()

    owner = os.getenv("GITHUB_OWNER")
    repo = os.getenv("GITHUB_REPO")
    token = os.getenv("GITHUB_TOKEN")
    total_count, recent_count = fetch_total_releases(token, owner, repo, 90)
    print(f"total_count:{total_count}, recent_count:{recent_count}")
