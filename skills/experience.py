import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
NOWDATE = datetime(2025, 6, 30)
YEAROFFSET = 1

def get_repo_contrib(username):
    """
    获取用户贡献情况
    """
    df_contrib = pd.DataFrame(columns=['commits', 'prs', 'issues', 'comments', 'reviews'])

    with open(f"data/developer/{username}/{username}_commits.json", 'r', encoding='utf-8') as f:
        commits = json.load(f)
    for commit in commits:
        repo = commit['repo']
        if repo not in df_contrib.index:
            df_contrib.loc[repo] = [0, 0, 0, 0, 0]
        df_contrib.loc[repo, 'commits'] += 1

    with open(f"data/developer/{username}/{username}_prs.json", 'r', encoding='utf-8') as f:
        prs = json.load(f)
    for pr in prs:
        repo = pr['repo']
        if repo not in df_contrib.index:
            df_contrib.loc[repo] = [0, 0, 0, 0, 0]
        df_contrib.loc[repo, 'prs'] += 1

    with open(f"data/developer/{username}/{username}_issues.json", 'r', encoding='utf-8') as f:
        issues = json.load(f)
    for issue in issues:
        repo = issue['repo']
        if repo not in df_contrib.index:
            df_contrib.loc[repo] = [0, 0, 0, 0, 0]
        df_contrib.loc[repo, 'issues'] += 1
    
    with open(f"data/developer/{username}/{username}_comments.json", 'r', encoding='utf-8') as f:
        comments = json.load(f)
    for comment in comments:
        repo = comment['repo']
        if repo not in df_contrib.index:
            df_contrib.loc[repo] = [0, 0, 0, 0, 0]
        # cnt = comment.get('comment_by', []).count(username)
        cnt = sum(1 for c in comment.get('comment_by', []) if c[0] == username)
        df_contrib.loc[repo, 'comments'] += cnt

    with open(f"data/developer/{username}/{username}_review_prs.json", 'r', encoding='utf-8') as f:
        reviews = json.load(f)
    for review in reviews:
        repo = review['repo']
        if repo not in df_contrib.index:
            df_contrib.loc[repo] = [0, 0, 0, 0, 0]
        # cnt = review.get('review_by', []).count(username)
        cnt = sum(1 for r in review.get('review_by', []) if r[0] == username)
        df_contrib.loc[repo, 'reviews'] += cnt

    return df_contrib

def plot_repo_contrib(df_repo_contrib):
    """
    绘图
    """
    sns.set_theme(style="white")
    colors = {
        'commits': "#81C784",
        'prs': "#4FC3F7",
        'issues': "#F06292",
        'comments': "#FFB74D",
        'reviews': "#A790F9",
    }
    fig, ax = plt.subplots(figsize=(10, 6))
    df_repo_contrib = df_repo_contrib.sort_values(by=list(df_repo_contrib.columns), ascending=True)
    df_repo_contrib.plot(kind='barh',stacked=True,color=[colors[k] for k in df_repo_contrib.columns],ax=ax,edgecolor='none')
    ax.set_title(f"{username}'s Contributions by Repository (Top 5)", fontsize=14, pad=15)
    ax.set_xlabel("Number of Contributions", fontsize=12)
    sns.despine(left=True, bottom=True)
    ax.xaxis.grid(True, linestyle='--', alpha=0.7)
    ax.legend(bbox_to_anchor=(0.5, -0.15), loc='upper center', ncol=5, fontsize=10)
    plt.tight_layout()
    fig_path = os.path.join(f"data/developer/{username}/{username}_repo_contributions.png")
    plt.savefig(fig_path, dpi=150)

def get_recent_contrib(username):
    """
    获取用户最近一年的贡献
    """
    with open(f"data/developer/{username}/{username}_commits.json", 'r', encoding='utf-8') as f:
        commits = json.load(f)
    with open(f"data/developer/{username}/{username}_prs.json", 'r', encoding='utf-8') as f:
        prs = json.load(f)
    with open(f"data/developer/{username}/{username}_issues.json", 'r', encoding='utf-8') as f:
        issues = json.load(f)
    with open(f"data/developer/{username}/{username}_comments.json", 'r', encoding='utf-8') as f:
        comment_items = json.load(f)
    with open(f"data/developer/{username}/{username}_review_prs.json", 'r', encoding='utf-8') as f:
        review_prs = json.load(f)
    
    # 获取最近一年的贡献，按月统计
    index = pd.date_range(start=NOWDATE - pd.DateOffset(years=YEAROFFSET), end=NOWDATE, freq='ME')
    contrib_recently = pd.DataFrame(0, index=index, columns=['commits', 'prs', 'issues', 'comments', 'reviews'])
    for item in commits:
        date = item['created_at'][:7]
        if date in contrib_recently.index:
            contrib_recently.loc[date, 'commits'] += 1
    for item in prs:
        date = item['created_at'][:7]
        if date in contrib_recently.index:
            contrib_recently.loc[date, 'prs'] += 1
    for item in issues:
        date = item['created_at'][:7]
        if date in contrib_recently.index:
            contrib_recently.loc[date, 'issues'] += 1
    for item in comment_items:
        for comment in item.get('comment_by', []):
            if comment[0] == username:
                date = comment[1][:7]
                if date in contrib_recently.index:
                    contrib_recently.loc[date, 'comments'] += 1
    for item in review_prs:
        for review in item.get('review_by', []):
            if review[0] == username:
                date = review[1][:7]
                if date in contrib_recently.index:
                    contrib_recently.loc[date, 'reviews'] += 1

    contrib_recently.fillna(0, inplace=True)  # 填充缺失值为0

    return contrib_recently

def plot_recent_contrib(df_contrib):
    """
    绘制最近一年的贡献图
    """
    sns.set_theme(style="white")
    colors = {
        'commits': "#81C784",
        'prs': "#4FC3F7",
        'issues': "#F06292",
        'comments': "#FFB74D",
        'reviews': "#A790F9",
    }
    fig, ax = plt.subplots(figsize=(10, 6))
    df_contrib.plot(kind='line', color=[colors[col] for col in df_contrib.columns], ax=ax)
    ax.set_title(f"{username}'s Recent Contributions (Last Year)", fontsize=14, pad=15)
    ax.set_ylabel("Number of Contributions", fontsize=12)
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.legend(bbox_to_anchor=(0.5, -0.15), loc='upper center', ncol=5, fontsize=10)
    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    fig_path = os.path.join(f"data/developer/{username}/{username}_recent_contributions.png")
    plt.savefig(fig_path, dpi=150)

def experience(username):
    """
    用户的开发经验
    """

    # 统计贡献总数
    df_contrib = get_repo_contrib(username)
    total_experience = {
        'paddle_repos': len(df_contrib),
        'commits': int(df_contrib['commits'].sum()),
        'prs': int(df_contrib['prs'].sum()),
        'issues': int(df_contrib['issues'].sum()),
        'comments': int(df_contrib['comments'].sum()),
        'reviews': int(df_contrib['reviews'].sum()),
    }

    # 按贡献总数排序，获取前5个repo；如果少于5个repo，补齐
    df_top5 = df_contrib.sort_values(by=['commits', 'prs', 'issues', 'comments', 'reviews'], ascending=False).head(5)
    if len(df_top5) < 5:
        for _ in range(5 - len(df_top5)):
            df_top5 = df_top5.append(pd.Series([0, 0, 0, 0, 0], index=df_top5.columns), ignore_index=True)  
    plot_repo_contrib(df_top5)

    # 统计commit、pr、issue随时间的变化
    df_recent_contrib = get_recent_contrib(username)
    plot_recent_contrib(df_recent_contrib)

    # 统计具有merge权限的repo
    with open(f"data/developer/{username}/{username}_can_merge.json", 'r', encoding='utf-8') as f:
        repos_can_merge = json.load(f)
    total_experience['repos_can_merge_cnt'] = len(repos_can_merge)
    total_experience['repos_can_merge'] = repos_can_merge

    return total_experience


if __name__ == "__main__":

    logging.basicConfig(
        format="%(asctime)s (PID %(process)d) [%(levelname)s] %(filename)s:%(lineno)d %(message)s",
        level=logging.INFO,
    )

    token = ''
    # username = 'dune0310421'
    username = 'Aurelius84'

    # df_recent_contrib = get_recent_contrib(username)
    # plot_recent_contrib(df_recent_contrib)

    results = experience(username)
    print(f"experience of developer {username}: {results}")
    with open(f"data/developer/{username}/{username}_experience.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
