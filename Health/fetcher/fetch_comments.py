from datetime import datetime, timedelta, timezone
import time

import requests
from requests.adapters import HTTPAdapter
from tqdm import tqdm
from urllib3.util.retry import Retry


def fetch_total_count_and_comments(node_type, token, owner, repo, days=None):
    """
    node_type: "issues" 或 "pullRequests"
    days: 统计这些天内的数据
    """

    url = "https://api.github.com/graphql"
    headers = {"Authorization": f"Bearer {token}"}

    if days:
        date_since = datetime.now(timezone.utc) - timedelta(days=days)
        since_iso = date_since.isoformat() + "Z"
    else:
        since_iso = None

    # 配置 Session + 重试
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)

    total_count = 0
    comments_count = 0
    has_next_page = True
    cursor = None
    recent_count = 0

    pbar = tqdm(
        desc=f"Fetching {node_type}",
        unit="items",
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
        dynamic_ncols=True,
    )

    while has_next_page:
        query = f"""
        query ($owner: String!, $name: String!, $after: String) {{
          repository(owner: $owner, name: $name) {{
            {node_type}(first: 100, after: $after, orderBy: {{field: CREATED_AT, direction: DESC}}) {{
              totalCount
              pageInfo {{
                hasNextPage
                endCursor
              }}
              nodes {{
                createdAt
                comments(first: 100) {{
                  totalCount
                }}
              }}
            }}
          }}
        }}
        """
        variables = {"owner": owner, "name": repo, "after": cursor}
        try:
            r = session.post(
                url,
                json={"query": query, "variables": variables},
                headers=headers,
                verify=True,
            )
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            wait_time = 2  # 等待2秒再重试
            print(f"\n请求错误，{wait_time}秒后重试: {e}")
            time.sleep(wait_time)
            continue

        data = r.json().get("data", {}).get("repository", {}).get(node_type, {})
        if not data:
            break

        nodes = data.get("nodes", [])

        # 第一次获取总数时更新进度条的 total
        if total_count == 0 and nodes:
            total_count = data.get("totalCount", len(nodes))
            pbar.total = total_count
            pbar.refresh()

        page_info = data.get("pageInfo", {})
        has_next_page = page_info.get("hasNextPage", False)

        for node in nodes:
            if days:
                created = datetime.fromisoformat(
                    node["createdAt"].replace("Z", "+00:00")
                )
                if created < date_since:
                    has_next_page = False
                    break
            recent_count += 1
            comments_count += node["comments"]["totalCount"]
            pbar.update(1)

        cursor = page_info.get("endCursor", None)

    pbar.close()
    return total_count, comments_count


if __name__ == "__main__":
    import os

    from dotenv import load_dotenv

    load_dotenv()

    token = os.getenv("GITHUB_TOKEN")
    owner = os.getenv("GITHUB_OWNER")
    repo = os.getenv("GITHUB_REPO")

    if not token or not owner or not repo:
        raise ValueError("请在 .env 文件中设置 GITHUB_TOKEN, GITHUB_OWNER, GITHUB_REPO")

    print(f"开始收集{owner}/{repo}的comment数量")

    issue_total, issue_comments = fetch_total_count_and_comments(
        "issues", token, owner, repo, 90
    )
    print(f"Issues:{issue_total},Issue Comments:{issue_comments}")

    pr_total, pr_comments = fetch_total_count_and_comments(
        "pullRequests", token, owner, repo, 90
    )
    print(f"PRs:{pr_total},PR Comments:{pr_comments}")

    print(f"Issues:{issue_total},Issue Comments:{issue_comments}")
    print(f"PRs:{pr_total},PR Comments:{pr_comments}")
    print(f"所有评论总数: {issue_comments + pr_comments}")
