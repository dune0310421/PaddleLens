from tqdm import tqdm
from woc.local import WocMapsLocal
from woc.objects import init_woc_objects, Author
from collections import defaultdict
import datetime
from util import read_file
import matplotlib.pyplot as plt
import os
from pyAPI import execCommand


'''
一. 基础信息：
- load commits / Projects / usr_key
- 时间段分布
'''
###################################
'''
1. load各种信息
'''

woc = WocMapsLocal()
init_woc_objects(woc)

# 时间段分布
TIME_RANGE_NEW = {
    x:[datetime.time(x,0,0), datetime.time(x,59,59)] for x in range(0,24)
}
# language to extension
EXT_TO_LANG = read_file('./cache/language.cache')

# 输入基本信息，返回key of user
def getKeyofUser(name, email):
    return name + ' ' + '<' + email +'>'

# 所有commit
def getCommitsOfUser(KeyOfUser):
    print('Start to get commits...')
    commit_list = []
    commits = Author(KeyOfUser).commits
    for commit in tqdm(commits):
        commit_list.append(commit)
    with open('./developer_data/cache/cmt_hash.txt', 'w') as f:
        for commit in commits:
            f.write(commit.hash)
            f.write('\n')
    return commit_list

# commit时间段分布
def getCommitTimeDistribution(commits, yearlimit=1970, timezone=8):
    print('Start to get commit time distribution...')
    ATZ = datetime.timezone(datetime.timedelta(hours=timezone)) # 设置时区
    activeTimeRange = defaultdict(int)

    for commit in commits:
        if commit.committed_at.year <= yearlimit:
            continue        
        createdTime = commit.committed_at.astimezone(ATZ) # 转换为当前时区
        #print(createdTime.year, createdTime.month, createdTime.day)
        for cur in TIME_RANGE_NEW:
            if cur not in activeTimeRange:
                activeTimeRange[cur] = 0 # 保证后续plt默认值
            if createdTime.time() >= TIME_RANGE_NEW[cur][0] and createdTime.time() < TIME_RANGE_NEW[cur][1] :
                activeTimeRange[cur] += 1
                continue
    sortedvalue = sorted(activeTimeRange.items(),key=lambda x:x[0])

    plt.cla()
    plt.figure(figsize = [10,5])
    plt.bar([x[0] for x in sortedvalue], [x[1] for x in sortedvalue], color='#B0C4DE')
    plt.xticks([x[0] for x in sortedvalue])
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.xlabel('time')
    plt.ylabel('commit num')
    plt.title('commit number of different hours')
    plt.show()
    plt.savefig('./developer_data/imgs/time_dis.png')

    print('done.')

    return activeTimeRange

# commit时区分布
def getTimeZoneDistribution(commits, yearlimit=1968):
    print('Start to get timezone distribution...')
    TimeZoneDistribution = {k:0 for k in range(-12,12)}
    for commit in commits:
        if commit.committed_at.year <= yearlimit:
            continue
        # print(str(commit.committed_at.tzinfo).split())
        commitTimeZone = int(str(commit.committed_at.tzinfo)[3:6] if len(str(commit.committed_at.tzinfo)) > 3 else 0)
        TimeZoneDistribution[commitTimeZone] += 1
    sortedvalue = sorted(TimeZoneDistribution.items(),key=lambda x:x[0])
    plt.cla()
    plt.figure(figsize = [10,5])
    plt.bar([x[0] for x in sortedvalue], [x[1] for x in sortedvalue], color='#B0C4DE')
    plt.xticks([x[0] for x in sortedvalue])
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.xlabel('timezone')
    plt.ylabel('commit num')
    plt.title('commit number of different timezone')
    plt.show()
    plt.savefig('./developer_data/imgs/timezone_dis.png')

    print('done.')
    return sortedvalue

# 所有projects
def getNonForkProjectsOfUser(usr_key): 
    print('Start to get projects...')
    nonForkProject = list(execCommand('a2P', usr_key))
    return nonForkProject

# def drawCommitPlot(commits, shift = 1, timezone = 8):
#     print('Start to draw commit plot...')
#     now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=timezone)))
#     if shift:
#         now = now - datetime.timedelta(days = 365 * shift)
#     title = 'commits history of last 1 year'# till {}'.format(str(now).split()[0])
#     weekday = now.isoweekday()
#     myheatmap = pd.DataFrame(index = range(1,8), columns = range(0,54))
#     for j in range(0,54):
#         myheatmap[j] = 0
#     ATZ = datetime.timezone(datetime.timedelta(hours=timezone))
#     mapdict = {}
#     keylist = []
#     for date in range(weekday+1,8):
#         myheatmap.loc[date,53] = -1
#     for week in range(53,-1,-1):
#         for date in range(weekday,0,-1):
#             mapdict[str(now)] = (date,week)
#             keylist.append(str(now))
#             now -= datetime.timedelta(days=1)
#         weekday = 7
#     keylist = [x for x in reversed(keylist)]
#     trans_keylist = [time.split()[0] for time in keylist]
#     #print(trans_keylist)
#     trans_now = str(now).split()[0]
#     for commit in commits:
#         commit_time = str(commit.committed_at.astimezone(ATZ)).split()[0]
#        #print(commit_time, trans_now)
#         for i, time in enumerate(keylist):
#             if commit_time > trans_now and commit_time < trans_keylist[i]:
#                 date, week = mapdict[time]
#                 myheatmap.loc[date, week] += 1
#                 break
#     plt.cla()
#     sb.heatmap(myheatmap, linewidth = 0.3)
#     plt.gcf().set_size_inches(20, 4)
#     plt.xlabel('week')
#     plt.ylabel('weekday')
#     plt.title(title)
#     plt.show()
#     plt.savefig('./developer_data/imgs/commit_distribution.png')

if __name__ == '__main__':

    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    usrdict = {}
    usrdict['name'] = 'Aurelius84'
    usrdict['email'] = 'liujiezhangbupt@gmail.com'
    usr_key = getKeyofUser(usrdict['name'], usrdict['email'])
    print(usr_key + ' open source resume')

    commits = getCommitsOfUser(usr_key)
    # getCommitTimeDistribution(commits)
    # getTimeZoneDistribution(commits)

    projects = getNonForkProjectsOfUser(usr_key)
    # print(projects)

    # drawCommitPlot(commits, 3)