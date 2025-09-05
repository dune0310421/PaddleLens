from datetime import datetime, timedelta, timezone
import os

import requests


def fetch_selected_pr_or_issue_count(type, token, owner, repo, state=None, days=None):
    """
    type: "pr" "issue"
    state: "open" "closed" "merged", None->all
    """
    headers = {"Authorization": f"token {token}"}

    # 总数
    query_total = f"repo:{owner}/{repo} is:{type}"

    if state:
        query_total += f" is:{state}"

    url_total = f"https://api.github.com/search/issues?q={query_total}"
    r_total = requests.get(url_total, headers=headers)
    r_total.raise_for_status()
    total_count = r_total.json().get("total_count", 0)

    # 近 days 天
    if days:
        date_since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime(
            "%Y-%m-%d"
        )
        query_recent = query_total + f" created:>={date_since}"

        url_recent = f"https://api.github.com/search/issues?q={query_recent}"
        r_recent = requests.get(url_recent, headers=headers)
        r_recent.raise_for_status()
        recent_count = r_recent.json().get("total_count", 0)
    else:
        recent_count = 0

    return total_count, recent_count


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    token = os.getenv("GITHUB_TOKEN")
    owner = os.getenv("GITHUB_OWNER")
    repo = os.getenv("GITHUB_REPO")

    total_merged, recent_merged = fetch_selected_pr_or_issue_count(
        "pr", token, owner, repo, "merged", days=90
    )
    total_all, recent_all = fetch_selected_pr_or_issue_count(
        "pr", token, owner, repo, state=None, days=90
    )
    print(f"{owner}/{repo} 全期: {total_merged}/{total_all}={total_merged/total_all}")
    print(
        f"{owner}/{repo} 近三个月 {recent_merged}/{recent_all}={recent_merged/recent_all}"
    )

    total_closed, recent_closed = fetch_selected_pr_or_issue_count(
        "issue", token, owner, repo, "closed", 90
    )
    total_all, recent_all = fetch_selected_pr_or_issue_count(
        "issue", token, owner, repo, None, 90
    )

    print(f"{total_closed}/{total_all}={total_closed/total_all}")
    print(f"{recent_closed}/{recent_all}={recent_closed/recent_all}")
