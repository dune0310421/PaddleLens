from datetime import datetime, timedelta, timezone
import json
import os
import subprocess
import tempfile
import time


def clone_repo(owner, repo):
    repo_url = f"git@github.com:{owner}/{repo}.git"
    with tempfile.TemporaryDirectory() as tmpdir:
        target_dir = os.path.join(tmpdir, f"{owner}_{repo}")
        subprocess.run(["git", "clone", repo_url, target_dir], check=True)

        # 构造 git log 命令
        cmd = [
            "git",
            "log",
            "--pretty=format:%H|%ad|%an|%cn|%f",
            "--date=iso",
        ]

        # 执行命令，指定 UTF-8 编码，忽略非法字符
        result = subprocess.run(
            cmd,
            cwd=target_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            check=True,
        )

        # 解析输出并构建 JSON
        commits = []
        for line in result.stdout.splitlines():
            sha, created_at, author, committer, message = line.split("|", 4)
            commits.append(
                {
                    "repo": f"{owner}/{repo}",
                    "sha": sha,
                    "created_at": created_at,
                    "author": author,
                    "committer": committer,
                    "message": message,
                }
            )

        # 保存到文件
        file_name = f"./commit_jsons/{owner}/{repo}_commits.json"
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(commits, f, ensure_ascii=False, indent=2)


def fetch_commit_count(owner, repo, days=None):

    file_name = f"./commit_jsons/{owner}/{repo}_commits.json"
    with open(file_name, "r", encoding="utf-8") as f:
        commits = json.load(f)

    if days:
        date_since = datetime.now(timezone.utc) - timedelta(days=days)

        recent_commits = [
            c
            for c in commits
            if datetime.strptime(c["created_at"], "%Y-%m-%d %H:%M:%S %z") >= date_since
        ]
        return len(recent_commits)

    else:
        return len(commits)


def fetch_total_contributors(owner, repo, days=None):
    file_name = f"./commit_jsons/{owner}/{repo}_commits.json"
    with open(file_name, "r", encoding="utf-8") as f:
        commits = json.load(f)
        all_authors = set()
        recent_authors = set()
    if days:
        date_since = datetime.now(timezone.utc) - timedelta(days=days)
    else:
        date_since = None

    for c in commits:
        author = c["author"]
        all_authors.add(author)
        created_at = datetime.strptime(c["created_at"], "%Y-%m-%d %H:%M:%S %z")
        if created_at >= date_since:
            recent_authors.add(author)

    return len(all_authors), len(recent_authors)


def fetch_active_contributor(owner, repo, days):
    file_name = f"./commit_jsons/{owner}/{repo}_commits.json"
    date_since = datetime.now(timezone.utc) - timedelta(days=days)
    with open(file_name, "r", encoding="utf-8") as f:
        commits = json.load(f)

    all_authors_before = set()
    all_authors_recent = set()

    for c in commits:
        author = c["author"]
        created_at = datetime.fromisoformat(c["created_at"].replace(" +0000", "+00:00"))

        if created_at >= date_since:
            all_authors_recent.add(author)
        else:
            all_authors_before.add(author)

    # 近三个月才开始贡献的人
    new_contributors = all_authors_recent - all_authors_before

    # 三个月前做过贡献，但近三个月没有贡献的人
    # inactive_contributors = all_authors_before - all_authors_recent

    # 持续在贡献的人
    retention_contributors = all_authors_before & all_authors_recent

    return len(new_contributors), len(retention_contributors), len(all_authors_before)


if __name__ == "__main__":
    import os

    from dotenv import load_dotenv

    load_dotenv()
    owner = os.getenv("GITHUB_OWNER")
    repo = os.getenv("GITHUB_REPO")

    clone_repo(owner, repo)
    total = fetch_commit_count(owner, repo)
    recent = fetch_commit_count(owner, repo, 90)

    print(f"总commit:{total},近期commit:{recent}")

    total, recent = fetch_total_contributors(owner, repo, 90)
    print(f"总contributors:{total},近期contributors:{recent}")
