import time
import json
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import requests
from github import Github

from utils.request_github import request_github
from utils.content_processor import get_pr_type

logger = logging.getLogger(__name__)
GITHUB_GRAPHQL_ENDPOINT = "https://api.github.com/graphql"
token_list = [
    '',  # 添加github token
]

def fetch_pr_info(gh, repo_full_name, pr_num):
    """
    获取PR的详细信息：使用特定的 gh 获取
    """
    pr = request_github(gh, lambda n: gh.get_repo(repo_full_name).get_pull(n), (pr_num,))

    try:
        pr_info = {
            'repo': pr.base.repo.full_name,
            'number': pr.number,
            'title': pr.title,
            'body': pr.body,
            'issue_number': pr.issue_url.split('/')[-1] if pr.issue_url else None,
            'state': pr.state,
            'merged': pr.merged,
            'user': pr.user.login if pr.user else None,
            'merged_by': pr.merged_by.login if pr.merged_by else None,
            'created_at': pr.created_at.isoformat(),
            'closed_at': pr.closed_at.isoformat() if pr.closed_at else None,
            'additions': pr.additions,
            'deletions': pr.deletions,
            'changed_files': pr.changed_files,
        }
        # 获取commits sha
        # commits = pr.get_commits()
        commits = request_github(gh, pr.get_commits, ())
        pr_info['commits'] = [commit.sha for commit in commits]
        # 获取comments
        pr_info['comment_by'] = []
        if pr.comments > 0:
            # comments = pr.get_issue_comments()
            comments = request_github(gh, pr.get_issue_comments, ())
            comments_list = []
            for comment in comments:
                comment_author = comment.user.login if comment.user else None
                comment_time = comment.created_at.isoformat() if comment.created_at else None
                comments_list.append((comment_author, comment_time))
            pr_info['comment_by'] = comments_list
        # 获取review comments
        pr_info['review_by'] = []
        if pr.review_comments > 0:
            # review_comments = pr.get_review_comments()
            review_comments = request_github(gh, pr.get_review_comments, ())
            review_comments_list = []
            for comment in review_comments:
                comment_author = comment.user.login if comment.user else None
                comment_time = comment.created_at.isoformat() if comment.created_at else None
                review_comments_list.append((comment_author, comment_time))
            pr_info['review_by'] = review_comments_list
        # 获取files
        pr_files = pr.get_files()
        pr_info['files'] = []
        if pr_files:
            for file in pr_files:
                file_info = {
                    'filename': file.filename,
                    'status': file.status,
                    'additions': file.additions,
                    'deletions': file.deletions,
                    'changes': file.changes,
                }
                pr_info['files'].append(file_info)
        # 获取类型
        pr_info['type'] = get_pr_type(pr.title, pr.body)
        return pr_info
    except Exception as e:
        logger.error(f"Error fetching PR {pr.number} for repository {pr.base.repo.full_name}: {e}")
        return {
            'repo': repo_full_name,
            'number': pr.number,
            'error': str(e)
        }

def fetch_pr_info_graphql(token, repo_full_name, pr_num):
    """
    使用GitHub GraphQL获取指定pr的信息（替代 REST API）
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    repo_owner, repo_name = repo_full_name.split('/')
    query = """
    query ($owner: String!, $name: String!, $prNumber: Int!, $cursor: String) {
        repository(owner: $owner, name: $name) {
            pullRequest(number: $prNumber) {
                number
                title
                body
                state
                merged
                createdAt
                closedAt
                additions
                deletions
                changedFiles
                author {
                    login
                }
                mergedBy {
                    login
                }
                commits(first: 100, after: $commitsCursor) {
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                    nodes {
                        commit {
                            oid
                        }
                    }
                }
                comments(first: 100, after: $commentsCursor) {
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                    nodes {
                        author {
                            login
                        }
                    }
                }
                reviewThreads(first: 100, after: $reviewsCursor) {
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                    nodes {
                        comments(first: 100) {
                            nodes {
                                author {
                                    login
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """

    variables = {
        "owner": repo_owner,
        "name": repo_name,
        "prNumber": pr_num,
        "cursor": None  # 用于分页
    }

    response = requests.post(GITHUB_GRAPHQL_ENDPOINT, headers=headers, json={'query': query, 'variables': variables})
    if response.status_code != 200:
        return {"error": f"GraphQL query failed: {response.text}", "pr_number": pr_num}

    data = response.json()
    try:
        pr = data['data']['repository']['pullRequest']
        if pr is None:
            return {"error": "Pr not found", "pr_number": pr_num}

        pr_info = {
            "repo": repo_full_name,
            "number": pr['number'],
            "title": pr['title'],
            "body": pr['body'],
            "state": pr['state'],
            "merged": pr['merged'],
            "user": pr['author']['login'] if pr['author'] else None,
            "merged_by": pr['mergedBy']['login'] if pr['mergedBy'] else None,
            "created_at": pr['createdAt'],
            "closed_at": pr['closedAt'],
            "additions": pr['additions'],
            "deletions": pr['deletions'],
            "changed_files": pr['changedFiles'],
            "commits": [c['commit']['oid'] for c in pr['commits']['nodes']],
            "comment_by": [c['author']['login'] for c in pr['comments']['nodes'] if c['author']],
            "review_by": list({rc['author']['login']
                               for rt in pr['reviewThreads']['nodes']
                               for rc in rt['comments']['nodes']
                               if rc['author']}),
        }

        return pr_info
    except Exception as e:
        logger.error(f"Error fetching PR {pr.number} for repository {pr.base.repo.full_name}: {e}")
        return {
            'repo': repo_full_name,
            'number': pr.number,
            'error': str(e)
        }

def get_repo_prs(repo_full_name):
    """
    获取指定仓库的所有PR
    """
    gh_list = [Github(token) for token in token_list]
    gh = gh_list[0]  # 使用第一个令牌的GitHub实例

    prs = request_github(
        gh, lambda r: gh.get_repo(r).get_pulls(state='all', sort='created', direction='desc'),
        (repo_full_name, )
    )
    if prs == None:
        logger.warning(f"No PRs found for repository: {repo_full_name}")
        return []
    
    pr_num_list = []
    for pr in tqdm(prs):
        pr_num_list.append(pr.number)

    # repo_owner, repo_name = repo_full_name.split('/')
    # with open(f"data/paddle_prs_n/{repo_owner}_{repo_name}_prs_n.json", "w", newline="", encoding="utf-8") as f:
    #     json.dump(pr_num_list, f, indent=4, ensure_ascii=False)
    # try:
    #     with open(f"data/paddle_prs_n/{owner}_{name}_prs_n.json", "r", encoding="utf-8") as f:
    #         pr_num_list = json.load(f)
    # except FileNotFoundError:
    #     logging.error(f"PR numbers file not found for {owner}_{name}. Using empty list.")
    #     return []
    
    
    logger.info(f"Fetching PRs for repository: {repo_full_name}, total: {len(pr_num_list)}")
    pr_list = []
    
    # 用 ThreadPoolExecutor 并行化处理 PR
    with ThreadPoolExecutor(max_workers=3 * len(gh_list)) as executor:
        # 分配任务到令牌 gh
        future_to_pr = {executor.submit(fetch_pr_info, gh_list[i % len(gh_list)], repo_full_name, pr_num): pr_num for i, pr_num in enumerate(pr_num_list)}
        # future_to_pr = {executor.submit(fetch_pr_info_graphql, token_list[i % len(token_list)], repo_full_name, pr_num): pr_num for i, pr_num in enumerate(pr_num_list)}

        for future in tqdm(as_completed(future_to_pr), total=len(future_to_pr), desc=f"Processing {repo_full_name}"):
            result = future.result()  # 获取线程结束后的结果
            if 'error' in result:
                logging.error(f"Error fetching PR {result['pr_number']} for repository {repo_full_name}: {result['error']}")
            pr_list.append(result)

    return pr_list

if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s (PID %(process)d) [%(levelname)s] %(filename)s:%(lineno)d %(message)s",
        level=logging.INFO,
    )

    # 获取所有仓库的pr
    with open("data/paddle_repos.json", "r", encoding="utf-8") as f:
        repos = json.load(f)
    # pr_list = []
    for repo in repos:
        # 获取每个仓库的PR信息
        prs = get_repo_prs(repo['full_name'])
        # if prs:
        #     pr_list.extend(prs)
        repo_owner, repo_name = repo['full_name'].split('/')
        with open(f"data/paddle_prs/{repo_owner}_{repo_name}_prs.json", "w", newline="", encoding="utf-8") as f:
            json.dump(prs, f, indent=4, ensure_ascii=False)
    # with open("data/paddle_prs.json", "w", newline="", encoding="utf-8") as f:
    #     json.dump(pr_list, f, indent=4, ensure_ascii=False)