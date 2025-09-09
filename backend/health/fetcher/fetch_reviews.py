from datetime import datetime, timedelta, timezone
import time

import requests
from requests.adapters import HTTPAdapter
from tqdm import tqdm
from urllib3.util.retry import Retry


def fetch_total_reviews(token, owner, repo, days=None):
    """
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

    total_pr_count = 0
    reviews_count = 0
    has_next_page = True
    cursor = None
    recent_pr_count = 0

    pbar = tqdm(
        desc=f"Fetching PR Review",
        unit="items",
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
        dynamic_ncols=True,
    )

    while has_next_page:
        # pr_filter = f', since: "{since_iso}"' if since_iso else ""

        query = f"""
        query ($owner: String!, $name: String!, $after: String) {{
          repository(owner: $owner, name: $name) {{
            pullRequests(first: 100, after: $after, orderBy: {{field: CREATED_AT, direction: DESC}}) {{
              totalCount
              pageInfo {{
                hasNextPage
                endCursor
              }}
              nodes {{
                createdAt
                reviews(first: 100) {{
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

        data = r.json().get("data", {}).get("repository", {}).get("pullRequests", {})
        if not data:
            break

        nodes = data.get("nodes", [])

        # 第一次获取总数时更新进度条的 total
        if total_pr_count == 0 and nodes:
            total_pr_count = data.get("totalCount", len(nodes))
            pbar.total = total_pr_count
            pbar.refresh()

        page_info = data.get("pageInfo", {})
        has_next_page = page_info.get("hasNextPage", False)

        for pr in nodes:
            if days:
                created = datetime.fromisoformat(pr["createdAt"].replace("Z", "+00:00"))
                if created < date_since:
                    has_next_page = False
                    break
            recent_pr_count += 1
            reviews_count += pr["reviews"]["totalCount"]
            pbar.update(1)

        cursor = page_info.get("endCursor", None)

    pbar.close()
    return recent_pr_count, reviews_count


if __name__ == "__main__":
    import os

    from dotenv import load_dotenv

    load_dotenv()

    token = os.getenv("GITHUB_TOKEN")
    owner = os.getenv("GITHUB_OWNER")
    repo = os.getenv("GITHUB_REPO")

    if not token or not owner or not repo:
        raise ValueError("请在 .env 文件中设置 GITHUB_TOKEN, GITHUB_OWNER, GITHUB_REPO")

    print(f"开始收集{owner}/{repo}的review数量")

    total_pr_count, reviews_count = fetch_total_reviews(token, owner, repo)
    print(f"total_pr_count:{total_pr_count},reviews_count:{reviews_count}")
