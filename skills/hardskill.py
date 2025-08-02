import os
import json
import math
import logging
from tqdm import tqdm
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

from get_data.get_repo_readme import get_readmes
from utils.extension_to_language import extension_to_language
from utils.content_processor import get_domain, get_pr_type
from utils.repo_util import project_weights, module_weights

logger = logging.getLogger(__name__)

def user_pr_types(username):
    """ 
    获取用户的PR类型
    """
    if os.path.exists(f"cache/developer/{username}/{username}_pr_types.json"):
        with open(f"cache/developer/{username}/{username}_pr_types.json", 'r', encoding='utf-8') as f:
            pr_types = json.load(f)
    else:
        with open(f"data/developer/{username}/{username}_prs.json", 'r', encoding='utf-8') as f:
            prs = json.load(f)
        pr_types = {}
        for pr in tqdm(prs):
            if pr['merged'] == False:
                continue
            repo_full_name = pr['repo']
            pr_type = get_pr_type(pr['title'], pr['body'])
            if repo_full_name not in pr_types:
                pr_types[repo_full_name] = {}
            pr_types[repo_full_name][pr['number']] = pr_type
        if not os.path.exists(f"cache/developer/{username}"):
            os.makedirs(f"cache/developer/{username}")
        with open(f"cache/developer/{username}/{username}_pr_types.json", 'w', encoding='utf-8') as f:
            json.dump(pr_types, f, ensure_ascii=False, indent=4)
    
    return pr_types

def plot_pr_types(username, pr_type_origin, pr_type_weights):
    """
    绘制PR类型的条形图，画在同一张图中
    """
    sns.set_theme(style="white")
    fig, axs = plt.subplots(2, 1, figsize=(12, 10))  # 创建两个子图
    ax1, ax2 = axs

    sns.barplot(
        x=list(pr_type_origin.keys()),
        y=list(pr_type_origin.values()),
        hue=list(pr_type_weights.keys()),
        ax=ax1,
        palette="Set2",
        legend=False
    )
    ax1.set_title(f"{username}'s PR Count by Type", fontsize=16)
    ax1.set_xlabel("PR Type", fontsize=10)
    ax1.set_ylabel("Count", fontsize=14)
    sns.despine(left=True, bottom=True, ax=ax1)
    ax1.yaxis.grid(True, linestyle='--', alpha=0.7)

    sns.barplot(
        x=list(pr_type_weights.keys()),
        y=list(pr_type_weights.values()),
        hue=list(pr_type_weights.keys()),
        ax=ax2,
        palette="Set2",
        legend=False
    )
    ax2.set_title(f"{username}'s Contribution Score by PR Type", fontsize=16)
    ax2.set_xlabel("PR Type", fontsize=10)
    ax2.set_ylabel("Weight", fontsize=14)
    sns.despine(left=True, bottom=True, ax=ax2)
    ax2.yaxis.grid(True, linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.savefig(f"data/developer/{username}/{username}_pr_types.png", dpi=150)

# 编程语言使用能力
def language_skill(username):
    """
    统计用户的编程语言使用情况
    """

    # 加载扩展名 -> 语言 的映射
    ext_to_lang = extension_to_language()

    # 获取commit修改文件的编程语言
    with open(f"data/developer/{username}/{username}_commits.json", 'r', encoding='utf-8') as f:
        commits = json.load(f)
    lang_counts = {}
    for commit in commits:
        files = commit['files']
        weight = 0.2 + 0.8 / (2025 - datetime.strptime(commit['date'], '%Y-%m-%dT%H:%M:%SZ').year) # 用艾斯宾遗忘曲线计算权重
        for file_obj in files:
            filename = file_obj['filename']
            ext = os.path.splitext(filename)[1]
            if ext == '':
                continue
            lang = ext_to_lang.get(ext, 'Others')
            lang_counts[lang] = weight if lang not in lang_counts else lang_counts[lang] + weight

    # 排序，但'Others'放在最后
    lang_counts = dict(sorted(lang_counts.items(), key=lambda x: x[1], reverse=True))
    if 'Others' in lang_counts:
        others_count = lang_counts.pop('Others')
        lang_counts['Others'] = others_count
    # print(f"Language counts for {username}: {lang_counts}")

    # 绘制条形图
    sns.set_theme(style="white")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=list(lang_counts.keys()), y=list(lang_counts.values()), width=0.4, ax=ax)
    ax.set_title(f"{username}'s Programming Language Usage", fontsize=14)
    ax.set_xlabel("Programming Language", fontsize=12)
    ax.set_ylabel("Number of Files", fontsize=12)
    sns.despine(left=True, bottom=True)
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f"data/developer/{username}/{username}_language_usage.png", dpi=150)

    # return lang_counts

# 领域能力
def domain_skill(username):
    """
    统计用户的领域能力
    """
    if os.path.exists(f"data/developer/{username}/{username}_domain.json"):
        with open(f"data/developer/{username}/{username}_domain.json", 'r', encoding='utf-8') as f:
            domains = json.load(f)
    else:
        with open(f"data/developer/{username}/{username}_repos.json", 'r', encoding='utf-8') as f:
            repos = json.load(f)
        repo_names = [repo['full_name'] for repo in repos]
        readme_contents = get_readmes(repo_names)
        domains = {}
        for repo in tqdm(repos):
            description = repo['description']
            readme_content = readme_contents.get(repo['full_name'], '')
            domain = get_domain(description, readme_content)
            new_domains = domain.split(', ')
            for d in new_domains:
                if d not in domains:
                    domains[d] = 1
                else:
                    domains[d] += 1
        with open(f"data/developer/{username}/{username}_domain.json", 'w', encoding='utf-8') as f:
            json.dump(domains, f, ensure_ascii=False, indent=4) 

    print(f"Domain skills for {username}: {domains}")
    # 绘制词云图
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate_from_frequencies(domains)
    plt.figure(figsize=(10, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.title(f"{username}'s Domain Skills", fontsize=20)
    plt.tight_layout()
    plt.savefig(f"data/developer/{username}/{username}_domain_skills.png", dpi=150)
    plt.close()

# 问题解决能力
def problem_solving_skill(username):
    """
    用户的问题解决能力，考虑 1）项目难度 2）贡献重要度 3）贡献类型
    """
    # with open(f"data/developer/{username}/{username}_commits.json", 'r', encoding='utf-8') as f:
    #     commits = json.load(f)

    # 获取项目难度
    p_w_dic = project_weights()
    # 获取项目模块及模块修改数
    m_w_dic = module_weights()
    # 获取用户的pr类型
    pr_types_dic = user_pr_types(username)

    # print("Calculating commit weights...")
    # commit_weights = {}
    # for commit in tqdm(commits):
    #     if commit['repo'] not in commit_weights:
    #         commit_weights[commit['repo']] = {}

    #     # 1.项目难度
    #     repo_full_name = commit['repo']
    #     p_w = p_w_dic.get(repo_full_name, 0)

    #     # 2.贡献重要度
    #     # 1）loc
    #     files = commit['files']
    #     loc = math.log10(sum(file['changes'] for file in files) + 1)
    #     # 2）模块重要度
    #     modules = m_w_dic.get(repo_full_name, {})
    #     m_w = 0
    #     for file in files:
    #         filename = file['filename']
    #         parts = filename.split('/')
    #         # 只取前两级目录作为模块名 eg: src/module1/file.py -> src/module1
    #         if len(parts) > 2:
    #             module = '/'.join(parts[:2])
    #         else:
    #             module = parts[0]
    #         weight = modules.get(module, 0)
    #         m_w += weight
    #     m_w = m_w / len(files) if files else 0  # 平均模块重要度

    #     commit_weights[repo_full_name][commit['sha']] =  m_w * p_w * loc

    # print("Calculating pr weights...")
    with open(f"data/developer/{username}/{username}_prs.json", 'r', encoding='utf-8') as f:
        prs = json.load(f)
    prs = [pr for pr in prs if pr['merged'] == True]  # 只考虑已合并的PR
    pr_weights = {}
    for pr in prs:
        if pr['repo'] not in pr_weights:
            pr_weights[pr['repo']] = {}

        # 1.项目难度
        repo_full_name = pr['repo']
        p_w = p_w_dic.get(repo_full_name, 0)

        # 2.贡献重要度
        # 1）loc
        loc = math.log10(pr['additions'] + pr['deletions'] + 1)
        # 2）模块重要度
        modules = m_w_dic.get(repo_full_name, {})
        m_w = 0
        files = pr['files']
        for file in files:
            filename = file['filename']
            parts = filename.split('/')
            # 只取前两级目录作为模块名 eg: src/module1/file.py -> src/module1
            if len(parts) > 2:
                module = '/'.join(parts[:2])
            else:
                module = parts[0]
            weight = modules.get(module, 0)
            m_w += weight
        m_w = m_w / len(files) if files else 0  # 平均模块重要度

        pr_weights[repo_full_name][pr['number']] =  m_w * p_w * loc

    # 3.pr类型
    pr_types = ['Bug fix', 'Documentation', 'Test', 'Build', 'Enhancement', 'New feature', 'Others']
    pr_type_origin = {p: 0 for p in pr_types}
    pr_type_weights = {ptype: 0 for ptype in pr_types}
    # print("Calculating PR types...")
    for pr in prs:
        repo_full_name = pr['repo']
        pr_type = pr_types_dic[repo_full_name][str(pr['number'])]
        pr_weight = pr_weights[repo_full_name].get(pr['number'], 0)
        if pr_type in pr_type_weights:
            pr_type_origin[pr_type] += 1
            pr_type_weights[pr_type] += pr_weight
        else:
            pr_type_origin['Others'] += 1
            pr_type_weights['Others'] += pr_weight

    plot_pr_types(username, pr_type_origin, pr_type_weights)

    # 最终问题解决能力分数
    total_score = sum(pr_type_weights.values())
    print(f"{username}'s Problem Solving Skill Score: {total_score}")

def hardskill(username):
    """
    用户的硬技能分析
    """
    # 1.编程语言使用能力
    language_skill(username)

    # 2.领域能力
    domain_skill(username)

    # 3.问题解决能力
    problem_solving_skill(username)

if __name__ == "__main__":

    logging.basicConfig(
        format="%(asctime)s (PID %(process)d) [%(levelname)s] %(filename)s:%(lineno)d %(message)s",
        level=logging.WARNING,
    )

    # username = 'dune0310421'
    username = 'Aurelius84'

    # language_skill(username)
    # domain_skill(username)
    # _ = user_pr_types(username)
    # problem_solving_skill(username)

    hardskill(username)

