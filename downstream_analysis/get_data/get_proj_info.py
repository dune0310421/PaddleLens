import time
import requests
import json
from datetime import datetime
import csv
import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

import logging
from typing import *
from github import Github
from github import RateLimitExceededException, UnknownObjectException

T = TypeVar("T")
logger = logging.getLogger(__name__)
token_list = [
    '',  # 添加github token
]

def request_github(
        gh: Github, gh_func: Callable[..., T], params: Tuple = (), default: Any = None
) -> Optional[T]:
    """
    This is a wrapper to ensure that any rate-consuming interactions with GitHub
      have proper exception handling.
    """
    for _ in range(0, 3):  # Max retry 3 times
        try:
            data = gh_func(*params)
            return data
        except RateLimitExceededException as ex:
            logger.info("{}: {}".format(type(ex), ex))
            sleep_time = gh.rate_limiting_resettime - time.time() + 10
            logger.info("Rate limit reached, wait for {} seconds...".format(sleep_time))
            time.sleep(max(1.0, sleep_time))
        except UnknownObjectException as ex:
            logger.error("{}: {}".format(type(ex), ex))
            break
        except Exception as ex:
            logger.error("{}: {}".format(type(ex), ex))
            time.sleep(5)
    return default

def fetch_repo_info(gh, repo_owner, repo_name):
    """ 
    获取指定仓库的信息

    gh: GitHub API
    repo_owner: 仓库所有者
    repo_name: 仓库名称
    """
    try:
        repo = gh.get_repo(f"{repo_owner}/{repo_name}")
        info = [
            repo_owner,
            repo_name,
            repo.owner.type,
            repo.fork,
            repo.homepage,
            repo.size,
            repo.stargazers_count,
            repo.language,
            repo.forks_count,
            ",".join(repo.get_topics()),
            repo.created_at.isoformat()
        ]
        return info
    except Exception as e:
        logger.error(f"Error fetching info for {repo_owner}/{repo_name}: {e}")
        return [repo_owner, repo_name]

def fetch_readme(gh, repo_owner, repo_name):
    """
    获取指定仓库的README内容
    gh: GitHub API
    repo_owner: 仓库所有者
    repo_name: 仓库名称
    """
    try:
        repo = gh.get_repo(f"{repo_owner}/{repo_name}")
        readme = repo.get_readme()
        readme_content = readme.decoded_content.decode("utf-8")
        return readme_content
    except Exception as e:
        logger.error(f"Error fetching README for {repo_owner}/{repo_name}: {e}")
        return ""

def get_repo_info(repos):
    """
    获取多个仓库的基本信息，使用多线程

    repos: list of (repo_owner, repo_name)
    """
    gh_list = [Github(token) for token in token_list]
    results = []

    with ThreadPoolExecutor(max_workers=3 * len(gh_list)) as executor:
        future_to_repo = {
            executor.submit(fetch_repo_info, gh_list[i % len(gh_list)], repo_owner, repo_name): (repo_owner, repo_name)
            for i, (repo_owner, repo_name) in enumerate(repos)
        }

        for future in tqdm(as_completed(future_to_repo), total=len(future_to_repo), desc="Fetching repo info"):
            try:
                info = future.result()
                results.append(info)
            except Exception as e:
                repo_owner, repo_name = future_to_repo[future]
                logger.error(f"Unhandled error for {repo_owner}/{repo_name}: {e}")
                results.append([repo_owner, repo_name, f"Unhandled error: {e}"])

    return results

def get_readme_content(repos):
    """
    获取多个仓库的README内容，使用多线程

    repos: list of (repo_owner, repo_name)
    """
    gh_list = [Github(token) for token in token_list]
    results = []

    with ThreadPoolExecutor(max_workers=3 * len(gh_list)) as executor:
        future_to_repo = {
            executor.submit(fetch_readme, gh_list[i % len(gh_list)], repo_owner, repo_name): (repo_owner, repo_name)
            for i, (repo_owner, repo_name) in enumerate(repos)
        }

        for future in tqdm(as_completed(future_to_repo), total=len(future_to_repo), desc="Fetching README content"):
            try:
                readme_content = future.result()
                results.append((f"{future_to_repo[future][0]}/{future_to_repo[future][1]}", readme_content))
            except Exception as e:
                repo_owner, repo_name = future_to_repo[future]
                logger.error(f"Unhandled error for {repo_owner}/{repo_name}: {e}")
                results.append((f"{repo_owner}/{repo_name}", f"Unhandled error: {e}"))

    return results


if __name__ == "__main__":

    logging.basicConfig(
        format="%(asctime)s (PID %(process)d) [%(levelname)s] %(filename)s:%(lineno)d %(message)s",
        level=logging.INFO,
    )

    REPO = 'paddle'

    # 获取仓库信息
    input_file = f'../data/{REPO}_downstream.csv'
    output_file = f'../data/{REPO}_downstream_info.csv'
    repos = []
    with open(input_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                repo_owner, repo_name = row[0], row[1]
                repos.append((repo_owner, repo_name))
    repos.pop(0)  # 移除表头
    repos_info = get_repo_info(repos)
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['repo_owner', 'repo_name', 'owner_type', 'fork', 'homepage', 'size', 'stars_cnt', 'language', 'forks_count', 'topics', 'created_at'])
        writer.writerows(repos_info)
    # os.remove(input_file)


    # # 获取README内容
    # input_file = f'data/{REPO}_downstream_popular.csv'
    # output_file = f'data/{REPO}_downstream_popular_readme.json'
    # # input_file = f'data/test.csv'
    # # output_file = 'data/test_readme.json'
    # with open(input_file, 'r') as f:
    #     reader = csv.reader(f)
    #     repos = []
    #     for row in reader:
    #         if len(row) >= 2:
    #             repo_owner, repo_name = row[0], row[1]
    #             repos.append((repo_owner, repo_name))
    # repos.pop(0)  # 移除表头
    # repos_readme = get_readme_content(repos)
    # readme_dict = {repo: content for repo, content in repos_readme}
    # with open(output_file, 'w', encoding='utf-8') as f:
    #     json.dump(readme_dict, f, ensure_ascii=False, indent=2)

