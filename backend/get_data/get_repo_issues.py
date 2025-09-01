import time
import json
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import requests
from github import Github

from utils.request_github import request_github

logger = logging.getLogger(__name__)
GITHUB_GRAPHQL_ENDPOINT = "https://api.github.com/graphql"
token_list = [
    '',  # 添加github token
]

def fetch_issue_info(gh, repo_full_name, issue_num):
    """
    获取指定issue的详细信息
    """
    issue = request_github(gh, lambda n: gh.get_repo(repo_full_name).get_issue(number=n), (issue_num,))

    try:
        issue_info = {
            'repo': issue.repository.full_name,
            'number': issue.number,
            'title': issue.title,
            'body': issue.body,
            'state': issue.state,
            'user': issue.user.login if issue.user else None,
            'closed_by': issue.closed_by.login if issue.closed_by else None,
            'created_at': issue.created_at.isoformat(),
            'updated_at': issue.updated_at.isoformat(),
            'closed_at': issue.closed_at.isoformat() if issue.closed_at else None,
        }
        # 获取comments
        issue_info['comments_count'] = []
        if issue.comments > 0:
            # comments = issue.get_comments()
            comments = request_github(gh, issue.get_comments, ())
            comments_list = []
            for comment in comments:
                comment_author = comment.user.login if comment.user else None
                comments_list.append(comment_author)
            issue_info['comments_count'] = comments_list
        # 获取labels
        issue_info['labels'] = []
        if issue.labels:
            labels_list = []
            for label in issue.labels:
                labels_list.append(label.name)
            issue_info['labels'] = labels_list
        return issue_info
    except Exception as e:
        logger.error(f"Error fetching issue {issue_num}: {e}")
        return {
            'repo': repo_full_name,
            'issue_number': issue_num,
            'error': str(e)
            }

def fetch_issue_info_graphql(token, repo_full_name, issue_num):
    """
    使用GitHub GraphQL获取指定issue的信息（替代 REST API）
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    repo_owner, repo_name = repo_full_name.split('/')
    query = """
    query ($owner: String!, $name: String!, $issueNumber: Int!, $cursor: String) {
        repository(owner: $owner, name: $name) {
            issue(number: $issueNumber) {
                number
                title
                body
                state
                createdAt
                updatedAt
                closedAt
                author {
                    login
                }
                labels(first: 10) {
                    nodes {
                        name
                    }
                }
                comments(first: 100, after: $cursor) {
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
            }
        }
    }
    """

    variables = {
        "owner": repo_owner,
        "name": repo_name,
        "issueNumber": issue_num,
        "cursor": None  # 用于分页
    }

    response = requests.post(GITHUB_GRAPHQL_ENDPOINT, headers=headers, json={'query': query, 'variables': variables})
    if response.status_code != 200:
        return {"error": f"GraphQL query failed: {response.text}", "issue_number": issue_num}

    data = response.json()
    try:
        issue = data['data']['repository']['issue']
        if issue is None:
            return {"error": "Issue not found", "issue_number": issue_num}

        issue_info = {
            "repo": repo_full_name,
            "number": issue["number"],
            "title": issue["title"],
            "body": issue["body"],
            "state": issue["state"],
            "user": issue["author"]["login"] if issue["author"] else None,
            "closed_by": None,  # GraphQL 暂无
            "created_at": issue["createdAt"],
            "updated_at": issue["updatedAt"],
            "closed_at": issue["closedAt"],
            "comments_count": [
                c["author"]["login"] if c["author"] else None for c in issue["comments"]["nodes"]
            ],
            "labels": [label["name"] for label in issue["labels"]["nodes"]]
        }

        return issue_info
    except Exception as e:
        logger.error(f"Error fetching issue {issue_num}: {e}")
        return {
            'repo': repo_full_name,
            'issue_number': issue_num,
            'error': str(e)
            }
    
def get_repo_prs_n(repo_full_name):
    """
    获取指定仓库的所有PR的number, 用于识别issue编号
    """
    gh = Github(token_list[0])

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

    return pr_num_list

def get_repo_issues(repo_full_name):
    """
    获取指定仓库的所有issue
    """
    gh_list = [Github(token) for token in token_list]
    gh = gh_list[0]  # 使用第一个令牌的GitHub实例

    issues = request_github(
        gh, lambda r: gh.get_repo(r).get_issues(state='all', sort='created', direction='desc'),
        (repo_full_name, )
    ) 
    
    if issues == None:
        logger.warning(f"No issues found for repository: {repo_full_name}")
        return []
    
    issue_num_now = 0
    for issue in issues:
        issue_num_now = issue.number
        break

    issue_num_list = [i + 1 for i in range(issue_num_now)]
    # 去除其中的pr
    pr_num_list = get_repo_prs_n(repo_full_name)
    # owner, name = repo_full_name.split('/')
    # try:
    #     with open(f"data/paddle_prs_n/{owner}_{name}_prs_n.json", "r", encoding="utf-8") as f:
    #         pr_num_list = json.load(f)
    # except FileNotFoundError:
    #     logging.error(f"PR numbers file not found for {owner}_{name}. Using empty list.")
    #     return []
    issue_num_list = [num for num in issue_num_list if num not in pr_num_list]
    
    logger.info(f"Fetching issues for repository: {repo_full_name}, total: {len(issue_num_list)}")
    issue_list = []
    with ThreadPoolExecutor(max_workers=3 * len(gh_list)) as executor:
        # 分配任务到令牌 gh
        future_to_issue = {executor.submit(fetch_issue_info, gh_list[i % len(gh_list)], repo_full_name, issue_num): issue_num for i, issue_num in enumerate(issue_num_list)}
        # future_to_issue = {executor.submit(fetch_issue_info_graphql, token_list[i % len(token_list)], repo_full_name, issue_num): issue_num for i, issue_num in enumerate(issue_num_list)}

        for future in tqdm(as_completed(future_to_issue), total=len(future_to_issue), desc=f"Processing {repo_full_name}"):
            issue_info = future.result()
            if 'error' in issue_info:
                logging.error(f"Error fetching issue {issue_info['issue_number']} for repository {repo_full_name}: {issue_info['error']}")
            issue_list.append(issue_info)
    return issue_list

if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s (PID %(process)d) [%(levelname)s] %(filename)s:%(lineno)d %(message)s",
        level=logging.INFO,
    )
    
    # 获取所有仓库的issue
    with open("data/paddle_repos.json", "r", encoding="utf-8") as f:
        repos = json.load(f)
    # issue_list = []
    for repo in repos:
        # 获取每个仓库的issue信息
        issues = get_repo_issues(repo['full_name'])
        # if issues:
        #     issue_list.extend(issues)
        repo_owner, repo_name = repo['full_name'].split('/')
        with open(f"data/paddle_issues/{repo_owner}_{repo_name}_issues.json", "w", newline="", encoding="utf-8") as f:
            json.dump(issues, f, indent=4, ensure_ascii=False)
    # with open("data/paddle_issues.json", "w", newline="", encoding="utf-8") as f:
    #     json.dump(issue_list, f, indent=4, ensure_ascii=False)