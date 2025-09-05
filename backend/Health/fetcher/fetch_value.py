import os

import requests


def fetch_repo_stats(token, owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}",
    }
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    data = r.json()

    stars = data.get("stargazers_count", 0)
    forks = data.get("forks_count", 0)
    watchs = data.get("subscribers_count", 0)

    return stars, forks, watchs


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    token = os.getenv("GITHUB_TOKEN")
    owner = os.getenv("GITHUB_OWNER")
    repo = os.getenv("GITHUB_REPO")

    stars, forks, watchers = fetch_repo_stats(token, owner, repo)
    print(f"{owner}/{repo} - Stars: {stars}, Forks: {forks}, Watchs: {watchers}")
