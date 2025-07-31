# import requests
import json
from datetime import datetime
import csv
import os
from tqdm import tqdm
import logging
from github import Github

from get_data.get_user_info import get_user_info, get_user_repos
# from get_data.get_repo_commits import get_repo_commits

logger = logging.getLogger(__name__)
NOWDATE = datetime(2025, 6, 30)

def get_user_commits(username, repo_full_name):
    """
    获取指定用户在指定仓库的commit信息
    """
    # logger.info(f"Fetching commits for {username} in repository {repo_full_name}")
    repo_owner, repo_name = repo_full_name.split('/')
    commit_list = []
    # 获取paddle相关仓库的commit信息，本地读取
    try:
        with open(f"data/paddle_commits/{repo_owner}_{repo_name}_commits.json", 'r', encoding='utf-8') as f:
            commits = json.load(f)
    except Exception as e:
        logger.error(f"Error fetching commits for {repo_full_name}: {e}")
        return commit_list
    
    for commit in commits:
        if commit['author'] == username:
            commit_list.append(commit)
    return commit_list

def get_user_prs(username, repo_full_name):
    """
    获取指定用户在指定仓库的pr信息
    """
    # logger.info(f"Fetching prs for {username} in repository {repo_full_name}")
    repo_owner, repo_name = repo_full_name.split('/')
    pr_list = []
    try:
        with open(f"data/paddle_prs/{repo_owner}_{repo_name}_prs.json", 'r', encoding='utf-8') as f:
            prs = json.load(f)
    except Exception as e:
        logger.error(f"Error fetching prs for {repo_full_name}: {e}")
        return pr_list
    for pr in prs:
        if 'user' in pr and pr['user'] == username:
            pr_list.append(pr)
    return pr_list

def get_user_issues(username, repo_full_name):
    """
    获取指定用户在指定仓库的issue信息
    """
    # logger.info(f"Fetching issues for {username} in repository {repo_full_name}")
    repo_owner, repo_name = repo_full_name.split('/')
    issue_list = []
    try:
        with open(f"data/paddle_issues/{repo_owner}_{repo_name}_issues.json", 'r', encoding='utf-8') as f:
            issues = json.load(f)
    except Exception as e:
        logger.error(f"Error fetching issues for {repo_full_name}: {e}")
        return issue_list
    for issue in issues:
        if 'user' in issue and issue['user'] == username: # 可能会有deleted issue，没有user字段
            issue_list.append(issue)
    return issue_list

def get_user_merge_permission(username, repo_full_name):
    """
    获取指定用户的merge权限仓库
    """
    flag = False
    try:
        repo_owner, repo_name = repo_full_name.split('/')
        with open(f"data/paddle_prs/{repo_owner}_{repo_name}_prs.json", 'r', encoding='utf-8') as f:
            prs = json.load(f)
    except Exception as e:
        logger.error(f"Error fetching prs for {repo_full_name}: {e}")
        return flag
    for pr in prs:
        if 'merged_by' not in pr or pr['merged_by'] == None:
            continue
        else:
            if pr['merged_by'] == username:
                flag = True
                break
    return flag

def get_user_reviews(username, repo_full_name):
    """
    获取指定用户在指定仓库的review信息
    """
    # logger.info(f"Fetching reviews for {username} in repository {repo_full_name}")
    repo_owner, repo_name = repo_full_name.split('/')
    review_pr_list = []
    try:
        with open(f"data/paddle_prs/{repo_owner}_{repo_name}_prs.json", 'r', encoding='utf-8') as f:
            prs = json.load(f)
    except Exception as e:
        logger.error(f"Error fetching prs for {repo_full_name}: {e}")
        return review_pr_list
    for pr in prs:
        if 'review_by' not in pr or pr['review_by'] == None:
            continue
        if username in pr['review_by']:
            review_pr_list.append(pr)
    return review_pr_list

def get_user_comments(username, repo_full_name):
    """
    获取指定用户在指定仓库的评论信息
    """
    # logger.info(f"Fetching comments for {username} in repository {repo_full_name}")
    repo_owner, repo_name = repo_full_name.split('/')

    comment_list = []
    # pr评论
    try:
        with open(f"data/paddle_prs/{repo_owner}_{repo_name}_prs.json", 'r', encoding='utf-8') as f:
            prs = json.load(f)
        for pr in prs:
            if 'comment_by' in pr and pr['comment_by']:
                if username in pr['comment_by']:
                    comment_list.append(pr)
    except Exception as e:
        logger.error(f"Error fetching PR comments for {repo_full_name}: {e}")

    # issue评论
    try:
        with open(f"data/paddle_issues/{repo_owner}_{repo_name}_issues.json", 'r', encoding='utf-8') as f:
            issues = json.load(f)
        for issue in issues:
            if 'comment_by' in issue and issue['comment_by']:
                if username in issue['comment_by']:
                    comment_list.append(issue)
    except Exception as e:
        logger.error(f"Error fetching issue comments for {repo_full_name}: {e}")

    return comment_list

def get_user_data(gh, username):
    """
    获取指定用户的基本信息和仓库信息
    """
    # logger.info(f"Fetching info for {username}")
    # 创建存储用户信息的目录
    if not os.path.exists(f"data/developer/{username}"):
        os.makedirs(f"data/developer/{username}")

    # 获取用户基本信息
    info = get_user_info(gh, username)
    with open(f"data/developer/{username}/{username}_info.json", 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=4)

    # 获取用户的仓库信息
    repos = get_user_repos(gh, username)
    filename = f"data/developer/{username}/{username}_repos.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(repos, f, ensure_ascii=False, indent=4)

    # 获取用户commit信息
    with open(f"data/paddle_repos.json", 'r', encoding='utf-8') as f:
        repos = json.load(f)
    # with open(f"data/developer/{username}/{username}_repos.json", 'r', encoding='utf-8') as f:
    #     repos = json.load(f)
    commits = []
    for repo in repos:
        cmts = get_user_commits(username, repo["full_name"], 1) # 获取paddle相关仓库的commit信息
        commits.extend(cmts)
    filename = f"data/developer/{username}/{username}_commits.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(commits, f, ensure_ascii=False, indent=4)

    # 获取用户pr信息
    with open(f"data/paddle_repos.json", 'r', encoding='utf-8') as f:
        repos = json.load(f)
    prs = []
    for repo in repos:
        prs_tmp = get_user_prs(username, repo["full_name"])
        prs.extend(prs_tmp)
    filename = f"data/developer/{username}/{username}_prs.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(prs, f, ensure_ascii=False, indent=4) 

    # 获取用户的issue信息
    with open(f"data/paddle_repos.json", 'r', encoding='utf-8') as f:
        repos = json.load(f)
    issues = []
    for repo in tqdm(repos):
        issues_tmp = get_user_issues(username, repo["full_name"])
        issues.extend(issues_tmp)
    filename = f"data/developer/{username}/{username}_issues.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(issues, f, ensure_ascii=False, indent=4)

    # 获取用户的review信息
    with open(f"data/paddle_repos.json", 'r', encoding='utf-8') as f:
        repos = json.load(f)
    review_prs = []
    for repo in repos:
        reviews_tmp = get_user_reviews(username, repo["full_name"])
        review_prs.extend(reviews_tmp)
    with open(f"data/developer/{username}/{username}_review_prs.json", 'w', encoding='utf-8') as f:
        json.dump(review_prs, f, ensure_ascii=False, indent=4)

    # 获取用户的评论信息
    with open(f"data/paddle_repos.json", 'r', encoding='utf-8') as f:
        repos = json.load(f)
    comment_list = []
    for repo in repos:
        comments_tmp = get_user_comments(username, repo["full_name"])
        comment_list.extend(comments_tmp)
    with open(f"data/developer/{username}/{username}_comments.json", 'w', encoding='utf-8') as f:
        json.dump(comment_list, f, ensure_ascii=False, indent=4)

    # 获取用户merge权限
    with open(f"data/paddle_repos.json", 'r', encoding='utf-8') as f:
        repos = json.load(f)
    merge_repos = []
    for repo in repos:
        flag = get_user_merge_permission(username, repo["full_name"])
        if flag:
            merge_repos.append(repo["full_name"])
    # print(f"{username} has merge permission in {len(merge_repos)} repositories: {merge_repos}")
    with open(f"data/developer/{username}/{username}_can_merge.json", 'w', encoding='utf-8') as f:
        json.dump(merge_repos, f, ensure_ascii=False, indent=4)

def user_info(token, username):
    """
    获取指定用户的信息，包括仓库信息、commit信息、pr信息、issue信息、review信息和评论等，并输出基本信息
    """
    # 获取用户信息，存储在data/developer/{username}目录下用于后续度量
    try:
        gh = Github(token)
    except Exception as e:
        logger.error(f"Error connecting to GitHub: {e}")
        return
    get_user_data(gh, username)

    with open(f"data/developer/{username}/{username}_info.json", 'r', encoding='utf-8') as f:
        info = json.load(f)
    info['public_repos_cnt'] = info.pop('public_repos')
    for key in ["created_at", "updated_at"]:
        if key in info and info[key]:
            info[key] = info[key][:10]

    # 获取用户不同身份类型的repo
    info['personal_repos_cnt'] = 0
    info['forked_repos_cnt'] = 0
    # info['paddle_repos_cnt'] = 0
    with open(f"data/developer/{username}/{username}_repos.json", 'r', encoding='utf-8') as f:
        repos = json.load(f)
    for repo in repos:
        if repo['parent'] is None:
            info['personal_repos_cnt'] += 1
        else:
            info['forked_repos_cnt'] += 1
            # repo_owner = repo['full_name'].split('/')[0]
            # if repo_owner == 'PaddlePaddle' or repo_owner == 'PFCCLab':
            #     info['paddle_repos_cnt'] += 1

    with open(f"data/developer/{username}/{username}_can_merge.json", 'r', encoding='utf-8') as f:
        merge_repos = json.load(f)
    info['paddle_repos_can_merge'] = merge_repos
    info['paddle_repos_can_merge_cnt'] = len(merge_repos)
    
    return info


if __name__ == "__main__":

    logging.basicConfig(
        format="%(asctime)s (PID %(process)d) [%(levelname)s] %(filename)s:%(lineno)d %(message)s",
        level=logging.INFO,
    )

    token = ''
    # username = 'dune0310421'
    username = 'Aurelius84'

    info = user_info(token, username)
    print(f"User {username} info: {info}")

