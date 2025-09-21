import os
import json
import re
import numpy as np
import pandas as pd
import joblib

from utils.cmt_msg_processor import process_commit_messages, BertEmbedding
# from utils.content_processor import get_commit_type

def get_features(commits: list[dict]) -> np.ndarray:
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

def get_commit_msg_type(commits: list[dict]) -> list[dict]:
    """ 
    预测commit message的类型
    """
    # for commit in tqdm(commits):
    #     type_number = get_commit_type(commit.get('message', ''), TOKEN)
    #     commit['why_what_label'] = type_number

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

    return commits

if __name__ == "__main__":
    # 测试
    with open('data/paddle_repos.json', 'r', encoding='utf-8') as f:
        repos = json.load(f)
    for repo in repos:
        owner, repo_name = repo['full_name'].split('/')
        with open(f"data/paddle_commits/{owner}_{repo_name}_commits.json", 'r', encoding='utf-8') as f:
            commits = json.load(f)
        result = get_commit_msg_type(commits)
        with open(f"data/paddle_commits1/{owner}_{repo_name}_commits.json", 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
