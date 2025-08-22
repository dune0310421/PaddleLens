import time
# import requests
import json
from tqdm import tqdm
import logging
from github import Github

from utils.request_github import request_github

logger = logging.getLogger(__name__)
token_list = [
    '', # 添加github token
]

def get_org_repos(gh, org_name):
    """
    获取指定组织的所有仓库
    """
    org = request_github(gh, gh.get_organization, (org_name,))
    if not org:
        logger.error(f"Organization {org_name} not found.")
        return []

    repos = org.get_repos()  # 获取组织的所有仓库
    repo_list = []

    logger.info(f"Fetching repositories for organization: {org_name}, total: {repos.totalCount}")
    for repo in tqdm(repos):
        repo_info = {
            "full_name": repo.full_name,
            "private": repo.private,
            "description": repo.description,
            "fork": repo.fork,
            "created_at": repo.created_at.isoformat(),
            "updated_at": repo.updated_at.isoformat(),
            "archived": repo.archived,
            "stargazers_count": repo.stargazers_count,
            "watchers_count": repo.watchers_count,
            "forks_count": repo.forks_count,
            "size": repo.size,
            "language": repo.language,
            "topics": repo.topics,
        }
        repo_list.append(repo_info)

    return repo_list

if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s (PID %(process)d) [%(levelname)s] %(filename)s:%(lineno)d %(message)s",
        level=logging.INFO,
    )

    gh = Github(token_list[0])

    # 获取paddle相关所有repo
    repos = get_org_repos(gh, "PaddlePaddle")
    repos.extend(get_org_repos(gh, "PFCCLab"))
    # repos.extend(get_org_repos(gh, "baidu"))
    with open("data/paddle_repos.json", "w", newline="", encoding="utf-8") as f:
        json.dump(repos, f, indent=4, ensure_ascii=False)
    