from datetime import datetime, timedelta, timezone
import json

import requests


def fetch_request_issue(token, owner, repo, label, state=None, days=None):
    """
    state: None, 'open', 'closed'
    label: 该仓库中代表功能需求的label名称
    """
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}",
    }
    url = "https://api.github.com/search/issues"

    q_str = f"repo:{owner}/{repo} is:issue label:{label}"
    if state:
        q_str += f" state:{state}"

    if days:
        date_since = datetime.now(timezone.utc) - timedelta(days=days)
        q_str += f" created:>={date_since.date()}"

    params = {
        "q": q_str,
        "per_page": 100,
        "page": 1,
    }

    r = requests.get(url, headers=headers, params=params)
    r.raise_for_status()
    data = r.json()
    return data.get("total_count", 0)


if __name__ == "__main__":
    import os

    from dotenv import load_dotenv

    load_dotenv()

    token = os.getenv("GITHUB_TOKEN")
    owner = os.getenv("GITHUB_OWNER")
    repo = os.getenv("GITHUB_REPO")
    label = os.getenv("REQUIREMENT_LABEL")

    if not token or not owner or not repo:
        raise ValueError("请在 .env 文件中设置 GITHUB_TOKEN, GITHUB_OWNER, GITHUB_REPO")

    all = fetch_request_issue(token, owner, repo, label)
    closed = fetch_request_issue(token, owner, repo, label, state="closed")
    opened = fetch_request_issue(token, owner, repo, label, state="open")
    print(f"all:{all},closed:{closed},open:{opened},closed+open:{closed+opened}")

    all = fetch_request_issue(token, owner, repo, label, days=90)
    closed = fetch_request_issue(token, owner, repo, label, state="closed", days=90)
    opened = fetch_request_issue(token, owner, repo, label, state="open", days=90)
    print(f"all:{all},closed:{closed},open:{opened},closed+open:{closed+opened}")
