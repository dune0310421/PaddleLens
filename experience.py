from curses import keyname
from numpy import bool_
from tqdm import tqdm
from collections import defaultdict
from datetime import timezone, timedelta
import datetime
from pyAPI import execCommand
from util import write_file, read_file
import matplotlib.pyplot as plt

from basic_info import getKeyofUser, getCommitsOfUser, EXT_TO_LANG
import os
from woc.local import WocMapsLocal
from woc.objects import init_woc_objects, Project, Commit

'''
二. 基本经验：
- 编程年限
- 总提交次数
- nonefork项目数量，个人项目数量，集体项目数量
'''
############################################
'''
1/2. 编程年限 & 总提交次数
'''

woc = WocMapsLocal()
init_woc_objects(woc)

#输入commits的list，返回年限与commits的数量
def getHistoryOfUser(commits):
    now = datetime.datetime.now(timezone(timedelta(hours=8)))
    firstCommitTime = now
    # print(firstCommitTime)
    for commit in commits:
        if commit.committed_at.year <= 1970 or commit.committed_at.year > now.year:
            continue
        if firstCommitTime >= commit.committed_at:
            firstCommitTime = commit.committed_at
    contributorYear = (now - firstCommitTime).days/365.25
    return contributorYear, len(commits)


'''
3. 参与项目数量和种类
'''
# 参与项目数量和种类
def getProjects(KeyOfUser, commits):
    print('Start to split and clean projects...')
    # c2P可能获取一些在Forked的项目做的

    projects = []
    personal_projects = []
    contributor_projects = []
    maintainer_projects = []
    project2commits = defaultdict(list)
    CACHE_PATH = 'developer_data/cache'

    for commit in commits:
        cmtP = woc.get_values('c2P', commit.hash)[0]
        project2commits[cmtP].append(commit.hash)
    # print(project2commits.keys())
    print(f'{KeyOfUser} has total {len(project2commits.keys())} non-fork projects')

    for project in tqdm(project2commits.keys()):
        print(f'Now, we are in {project}')

        pcommits = [Commit(c) for c in woc.get_values('P2c', project)]
        print(len(pcommits))

        # 提取为上游做过贡献的项目(因为可能贡献在forked的项目)
        common_commits = [] # 该dvpr在该项目的commit数量
        tmp = sorted([c.hash for c in pcommits])
        tmp.extend(sorted(c.hash for c in commits))
        tmp = sorted(tmp)
        for i in range(1, len(tmp)):
            if tmp[i] == tmp[i-1]:
                common_commits.append(tmp[i]) # 提取两个lst中相同元素
        if len(common_commits) == 0:
            project2commits.pop(project)
            continue
        print(len(common_commits))

        projects.append(project)
        # 判断项目类型
        if float(len(common_commits)) / float(len(pcommits)) >= 0.8:
            personal_projects.append(project)
        else:
            committer_FLAG = False  # 是否是maintainer
            # 判断权限，即判断committer和author是否一人
            # -----------TODO: 优化,这里寻找项目所有commiter耗时太长-----------
            if len(common_commits) < 100 and float(len(common_commits)) / float(len(pcommits)) < 0.0001:
                contributor_projects.append(project)
                continue
            for commit in pcommits:
                try:
                    tmpusr = f'{commit.committer.name} <{commit.committer.email}>'
                    if tmpusr == KeyOfUser:
                        committer_FLAG = True
                        break
                except:
                    pass
            if committer_FLAG == True:
                maintainer_projects.append(project)
            else:
                contributor_projects.append(project)

    # 转化成普通dict
    project2commits = {k:v for k,v in project2commits.items() if len(v) > 0}

    write_file(f'{CACHE_PATH}/Personal_prj.cache', personal_projects)
    write_file(f'{CACHE_PATH}/Contri_prj.cache', contributor_projects)
    write_file(f'{CACHE_PATH}/Main_prj.cache', maintainer_projects)
    write_file(f'{CACHE_PATH}/All_prj.cache', projects)
    write_file(f'{CACHE_PATH}/project2commits.cache', project2commits)
    plt.cla()
    plt.figure(figsize=[8, 5])
    plt.bar(['Personal', 'Contributor', 'Maintainer'], 
            [len(personal_projects), len(contributor_projects), len(maintainer_projects)],
            color=['#FFC0CB', '#B0C4DE', '#8FBC8F'],
            width=0.4)
    plt.title('project number of different types')
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.show()
    plt.savefig(f'./developer_data/imgs/project_distribution.png')
    
    print(f'{KeyOfUser} has {len(personal_projects)} personal projects, and is a contributor of {len(contributor_projects)} projects, and a maintainer of {len(maintainer_projects)} projects')

    return personal_projects, contributor_projects, maintainer_projects, projects


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
    # commits = [commit for commit in Author(usrKey).commits]
    # year, commit_cnt = getHistoryOfUser(commits)
    # print(year, commit_cnt)
    # p, c, m, a = getProjects(usrKey, commits)


