import os
import json
import math
import logging
import joblib
import pandas as pd
from tqdm import tqdm
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

from utils.cmt_msg_processor import process_commit_messages, BertEmbedding

logger = logging.getLogger(__name__)

def plot_consistency(username, repo_commitment):
    """
    绘制责任心柱状图
    """
    # 绘制top5柱状图，若少于5个项目，则用0填充少的部分
    top_repos = sorted(repo_commitment.items(), key=lambda x: x[1], reverse=True)[:5]
    top_repos_dict = dict(top_repos)
    if len(top_repos_dict) < 5:
        for i in range(5 - len(top_repos_dict)):
            top_repos_dict[f"Proj_{i+1}"] = 0
    sns.set_theme(style="white")
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x=list(top_repos_dict.values()), y=list(top_repos_dict.keys()), hue=list(top_repos_dict.keys()), palette="Set2", legend=False, ax=ax)
    ax.set_title(f"{username}'s Commitment in Projects", fontsize=16)
    ax.set_xlabel("Max Continuous Commit Months", fontsize=12)
    ax.tick_params(axis='y', labelsize=10)
    sns.despine(left=True, bottom=True)
    ax.xaxis.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f'data/developer/{username}/{username}_consistency.png', dpi=150)

def plot_activeness(username, repo_activeness):
    """
    绘制活跃度柱状图
    """
    # 绘制top5活跃度柱状图，若少于5个项目，则用0填充少的部分
    top_repos = sorted(repo_activeness.items(), key=lambda x: x[1], reverse=True)[:5]
    top_repos_dict = dict(top_repos)
    if len(top_repos_dict) < 5:
        for i in range(5 - len(top_repos_dict)):
            top_repos_dict[f"Proj_{i+1}"] = 0.0
    sns.set_theme(style="white")
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x=list(top_repos_dict.values()), y=list(top_repos_dict.keys()), hue=list(top_repos_dict.keys()), palette="Set2", legend=False, ax=ax)
    ax.set_title(f"{username}'s Activeness in Projects", fontsize=16)
    ax.set_xlabel("Average Active Months Ratio in a Period (6 Months)", fontsize=12)
    ax.tick_params(axis='y', labelsize=10)
    sns.despine(left=True, bottom=True)
    ax.xaxis.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f'data/developer/{username}/{username}_activeness.png', dpi=150)

def plot_communication(username, labels):
    """
    绘制沟通能力饼图
    """
    label_map = {
        0: 'no what and why',
        1: 'only why',
        2: 'only what',
        3: 'what and why'
    }
    sizes = [labels.count(i) for i in label_map.keys()]
    sorted_indices = sorted(range(len(sizes)), key=lambda i: sizes[i], reverse=True)
    sizes = [sizes[i] for i in sorted_indices]
    label_names = [label_map[i] for i in sorted_indices]
    sns.set_theme(style="white")
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = sns.color_palette("Set2", len(label_names))
    wedges, texts, autotexts = ax.pie(sizes, labels=label_names, autopct='%1.1f%%', startangle=140, colors=colors)
    ax.set_title(f"{username}'s Communication Skill in Commit Messages", fontsize=16)
    for i, text in enumerate(texts):
        text.set_text(f"{label_names[i]}: {sizes[i]}")
    plt.setp(autotexts, size=12, color="white")
    plt.setp(texts, size=12)
    plt.tight_layout()
    plt.savefig(f'data/developer/{username}/{username}_communication.png', dpi=150)

def get_features(commits):
    """ 
    提取commit message特征，构造预测数据集
    """
    # 提取消息文本
    messages = [commit['message'] for commit in commits]
    files = []
    for commit in commits:
        files_now = [file['filename'] for file in commit.get('files', [])]
        files.append(files_now)

    # 预处理文本（格式还原、占位符替换等）
    p_messages = process_commit_messages(messages, files)

    # 构造 DataFrame
    df = pd.DataFrame(p_messages)
    df.columns = ['new_message1']

    # 用特殊 token 替换原始 id/tokens
    df['new_message1'] = df['new_message1'].apply(lambda x: x.replace('<enter>', '$enter').replace('<tab>', '$tab') \
        .replace('<url>', '$url').replace('<version>', '$versionNumber').replace('<pr_link>', '$pullRequestLink>') \
        .replace('<issue_link >', '$issueLink').replace('<otherCommit_link>', '$otherCommitLink') \
        .replace("<method_name>", "$methodName").replace("<file_name>", "$fileName").replace("<iden>", "$token"))

    # 提取BERT特征
    features = BertEmbedding(df)

    return features

# 责任心
def commitment(username):
    """
    责任心：用户在每个项目中的最大连续贡献月份数 + 一段时间内的贡献月份比例。
    """
    with open(f'data/developer/{username}/{username}_commits.json', 'r', encoding='utf-8') as f:
        commits = json.load(f)
        
    # 获取每个项目的贡献年月
    project_months = {}
    for c in commits:
        repo = c['repo']
        commit_date = datetime.fromisoformat(c['created_at'].replace('Z', '+00:00'))
        ym = (commit_date.year, commit_date.month)
        if repo not in project_months:
            project_months[repo] = set()
        project_months[repo].add(ym)

    # 计算每个项目的最大连续月份
    repo_consistency = {}
    for repo, ym_pairs in project_months.items():
        sorted_ym = sorted(ym_pairs) # 按年月排序
        max_m = 1
        current_m = 1
        for i in range(1, len(sorted_ym)):
            y1, m1 = sorted_ym[i - 1]
            y2, m2 = sorted_ym[i]
            # 月份差计算
            diff = (y2 - y1) * 12 + (m2 - m1)
            if diff == 1:
                current_m += 1
                max_m = max(max_m, current_m)
            else:
                current_m = 1
        repo_consistency[repo] = max_m

    plot_consistency(username, repo_consistency)

    # 计算每个项目的半年内贡献月份的均值
    repo_activeness = {}
    for repo, ym_pairs in project_months.items():
        sorted_ym = sorted(ym_pairs)
        if not sorted_ym:
            repo_activeness[repo] = 0.0
            continue
        start_year, start_month = min(sorted_ym)
        end_year, end_month = max(sorted_ym)
        total_months = (end_year * 12 + end_month) - (start_year * 12 + start_month) + 1
        # 构造"某月是否有提交"的list
        month_flags = [0] * total_months
        for i in sorted_ym:
            y, m = i
            index = (y - start_year) * 12 + (m - start_month)
            month_flags[index] = 1    
        #滑动窗口统计活跃度
        window_size = 6
        if total_months < window_size:
            repo_activeness[repo] = sum(month_flags) / window_size
            continue
        window_sum = sum(month_flags[:window_size]) # 初始窗口
        windows = [window_sum]
        for i in range(window_size, total_months):
            window_sum = window_sum - month_flags[i - window_size] + month_flags[i]
            windows.append(window_sum)
        # Step 4: 平均值
        avg_active_months = (sum(windows) / len(windows)) / window_size
        repo_activeness[repo] = avg_active_months

    plot_activeness(username, repo_activeness)

    return repo_consistency, repo_activeness

# 时间管理能力
def time_management(username):
    """
    时间管理：一段时间窗口内同时活跃于最多项目
    """
    with open(f'data/developer/{username}/{username}_commits.json', 'r', encoding='utf-8') as f:
        commits = json.load(f)

    # 获取每个月的活跃项目
    month_projects = {}
    for c in commits:
        repo = c['repo']
        commit_date = datetime.fromisoformat(c['created_at'].replace('Z', '+00:00'))
        ym = (commit_date.year, commit_date.month)
        if ym not in month_projects:
            month_projects[ym] = set()
        month_projects[ym].add(repo)
    month_projects = dict(sorted(month_projects.items()))  # 按年月排序
    # 填补缺失的月份
    start_year, start_month = next(iter(month_projects.keys()))
    end_year, end_month = next(iter(reversed(month_projects.keys())))
    total_months = (end_year * 12 + end_month) - (start_year * 12 + start_month) + 1
    for i in range(total_months):
        year = start_year + (start_month + i - 1) // 12
        month = (start_month + i - 1) % 12 + 1
        if (year, month) not in month_projects:
            month_projects[(year, month)] = set()
    # 再次排序以确保顺序正确
    month_projects_lst = list(dict(sorted(month_projects.items())).values())

    # 计算每个时间窗口内活跃项目数
    window_size = 2
    active_projects = []
    max_active = (0, set())  # (月份索引, 活跃项目集合)
    if len(month_projects) < window_size:
        # 如果项目数少于窗口大小，则直接使用所有项目的并集
        active_projects = set.union(*month_projects_lst)
        max_active = (0, active_projects)
    else:
        active_projects = month_projects_lst[:window_size]  # 初始窗口
        max_active = (0, set.union(*active_projects))
        for i in range(window_size, len(month_projects_lst)):
            # 滑动窗口
            active_projects.pop(0)
            active_projects.append(month_projects_lst[i])
            # 计算当前窗口的活跃项目
            current_active = set.union(*active_projects)
            if len(current_active) > len(max_active[1]):
                max_active = (i - window_size + 1, current_active)
    # 将索引转换为实际的年月
    max_active_month_start = list(month_projects.keys())[max_active[0]]
    max_active_month_end = list(month_projects.keys())[max_active[0] + window_size - 1]
    # 获取这些项目中的commit
    commit_active = [c for c in commits if c['repo'] in max_active[1]]

    return {
        "max_active_month_start": max_active_month_start,
        "max_active_month_end": max_active_month_end,
        "active_projects": max_active[1],
        "commit_count": len(commit_active)
    }

# 沟通能力
def communication_skill(username):
    """
    沟通能力：commit message的质量
    """
    with open(f'data/developer/{username}/{username}_commits.json', 'r', encoding='utf-8') as f:
        commits = json.load(f)

    # 构造预测数据集
    features = get_features(commits)
    # 预测commit message的类型
    why_model = joblib.load('data/5_10_1_8_OrWhyClassifier_why_LR.joblib')
    what_model = joblib.load('data/5_10_2_22_OrWhyClassifier_what_LR.joblib')
    whats = what_model.predict(features)
    whys = why_model.predict(features)
    commit_labels = []
    for what,why in zip(whats,whys):
        if what == 1 and why == 1:  # what and why
            commit_labels.append(3)
        elif what == 1 and why == 0:  # only what
            commit_labels.append(2)
        elif what == 0 and why == 1:  # only why
            commit_labels.append(1)
        else:
            commit_labels.append(0)  # not why and not what
    # df['predict_labels'] = commit_labels # 获取预测标签

    #计算分数
    score = 0
    for label in commit_labels:
        if label == 3:
            score += 1
        elif label == 1 or label ==2:
            score += 0.5
    score = score / len(commit_labels)

    # 绘制饼图
    plot_communication(username, commit_labels)

    return score


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s (PID %(process)d) [%(levelname)s] %(filename)s:%(lineno)d %(message)s",
        level=logging.INFO,
    )

    username = 'Aurelius84'

    # repo_commitment = commitment(username)
    # time_management = time_management(username)
    # print(f"Time Management for {username}: {time_management['max_active_month_start']} - {time_management['max_active_month_end']}, Active Projects: {len(time_management['active_projects'])}, Commit Count: {time_management['commit_count']}")

    communication_score = communication_skill(username)
    print(f"Communication Skill Score for {username}: {communication_score}")

