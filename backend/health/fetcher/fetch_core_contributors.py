from datetime import datetime, timedelta, timezone
import json
import os
from config import GITHUB_TOKEN

import requests


def fetch_total_core_contributors(owner):
    url = "https://api.github.com/graphql"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

    query = """
    query ($org: String!) {
      organization(login: $org) {
        membersWithRole {
          totalCount
        }
      }
    }
    """

    variables = {"org": owner}
    r = requests.post(
        url, headers=headers, json={"query": query, "variables": variables}
    )
    r.raise_for_status()
    resp_json = r.json()
    org_data = resp_json.get("data", {}).get("organization") if resp_json else None
    if org_data is None:
        print(f"'{owner}' 不是组织用户")
        return 1
    else:
        total_members = org_data["membersWithRole"]["totalCount"]
        return total_members

    total_members = r.json()["data"]["organization"]["membersWithRole"]["totalCount"]
    return total_members


if __name__ == "__main__":
    import os

    from dotenv import load_dotenv

    load_dotenv()

    owner = os.getenv("GITHUB_OWNER")
    repo = os.getenv("GITHUB_REPO")
    token = os.getenv("GITHUB_TOKEN")
    total = fetch_total_core_contributors(token, owner)
    print(f"Core contributors:{total}")
