from tqdm import tqdm
from collections import defaultdict
from pyAPI import execCommand
from basic_info import EXT_TO_LANG
from oscar import *
import math
import matplotlib.pyplot as plt
from basic_info import getKeyofUser, getCommitsOfUser
from util import read_file, write_file
import os
'''
三. 硬实力：
- 常用语言
- 代码能力：commit重要性。对于每种语言，用遗忘曲线加权commit的复用次数
'''
##############

'''
1. 常用语言
'''
#给定一个file，返回语言
def getLangOfModifiedFile(file):
    _, ext = os.path.splitext(file)
    if ext in EXT_TO_LANG:
        return EXT_TO_LANG[ext]
    else: 
        return 'Others'

#给定所有commits，返回所有的语言使用次数
def getLangCntOfCommit():
    print('Start to get language of commits...')
    langWeightOfCommit = defaultdict(int)
    # with open('./developer_data/cache/cmt_hash.txt', 'w') as f:
    #     for commit in commits:
    #         f.write(commit.hash)
    #         f.write('\n')
    commits_files = list(execCommand('c2fbb', './developer_data/cache/cmt_hash.txt', True))
    commits_files = [file.strip('(').strip(')').split(',')[0].strip('\'') for file in commits_files]
    # print(commits_files[:2])
    print(f'commits_files cnt: {len(commits_files)}')
    for file in commits_files:
        lang = getLangOfModifiedFile(file)
        langWeightOfCommit[lang] += 1
    langWeightOfCommit = {k:v for k,v in langWeightOfCommit.items() if k is not None}
    # 按照value排序
    langWeightOfCommit = dict(sorted(langWeightOfCommit.items(), key=lambda x:x[1], reverse=True))
    plt.cla()
    plt.figure(figsize = [8,5])
    plt.bar(langWeightOfCommit.keys(), langWeightOfCommit.values(), color='#B0C4DE', width=0.4)
    plt.title('commit number of differnt languages')
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.show()
    plt.savefig(f'./developer_data/imgs/language_cnt.png')
    return langWeightOfCommit


'''
2. 代码能力: commit重要性。对于每种语言，用遗忘曲线加权commit的复用次数
'''
#input: commit， output: how many project involved in commit
def numbers2weight(projects_len):
    return math.log(max(math.e, projects_len))

def getCmtImportance(commits):
    print('Start to get Code Ability...')
    # with open('./developer_data/cache/cmt_hash.txt', 'w') as f:
    #     for commit in commits:
    #         f.write(commit.hash)
    #         f.write('\n')

    weight = []
    # 对于每个commit，计算其复用次数
    for commit in tqdm(commits):
        commit_projects = execCommand('c2p', commit.hash)
        created_year = commit.committed_at.year
        commitWeight = (0.2 + 0.8 / (2025 - created_year)) * numbers2weight(len(commit_projects))
        weight.append(commitWeight)

    # 将weight保存到文件
    write_file('./developer_data/cache/commit_weight.cache', weight)

    # 绘制散点图
    plt.cla()
    plt.figure(figsize = [5,5])
    plt.scatter(range(len(weight)), weight, color='#B0C4DE', size=1) # x轴是commit的index, y轴是commit的重要性
    plt.xlabel('commit index')
    plt.ylabel('commit importance')
    plt.title('commit importance')
    plt.show()
    plt.savefig(f'./developer_data/imgs/commit_importance.png')

    # 计算平均值
    weight = sum(weight) / len(weight)    
    score = weight / len(commits)
    return score



if __name__ == '__main__':

    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    usrdict = {}
    usrdict['name'] = 'Aurelius84'
    usrdict['email'] = 'liujiezhangbupt@gmail.com'
    usrKey = getKeyofUser(usrdict['name'], usrdict['email'])
    # usrKey = getKeyofUser('Hanmin Qin', 'qinhanmin2005@sina.com')
    print(usrKey + ' open source resume')

    commits = getCommitsOfUser(usrKey)
    # getLangCntOfCommit() # 语言分布

    avg_w = getCmtImportance(commits) # 代码能力
    print(f'avg commit importance: {avg_w}')

