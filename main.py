import os
from basic_info import getKeyofUser, getCommitsOfUser, getCommitTimeDistribution, getTimeZoneDistribution
from experience import getHistoryOfUser, getProjects
from hardskill import getLangCntOfCommit, getCmtImportance


if __name__ == '__main__':

    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    usrdict = {}
    usrdict['name'] = 'Aurelius84'
    usrdict['email'] = 'liujiezhangbupt@gmail.com'
    usr_key = getKeyofUser(usrdict['name'], usrdict['email'])
    print(f'{usr_key} open source resume')

    print('basic information and experience:')
    print('--------time distribution and commits distribution-------')
    commits = getCommitsOfUser(usr_key)
    getCommitTimeDistribution(commits)
    getTimeZoneDistribution(commits)
    year, commit_cnt = getHistoryOfUser(commits)
    usrdict['year'] = year
    usrdict['commit_cnt'] = commit_cnt
    print(f'development year {year}, development commit number {commit_cnt}')
    print('see plots in imgs')

    # print('---------project distribution-------------')
    # p,m,c,a = getProjects(usr_key, commits)
    # print(f'All project number: {len(a)}')
    # print('see plot in imgs')

    
    # print('-------------------------------------------')
    # print('hardskill')

    # # print('----------langdistribution---------------')
    # print('see plots in imgs')
    # lang_cnt_dict = getLangCntOfCommit(commits)
    # code_ability_score = getCmtImportance(commits)