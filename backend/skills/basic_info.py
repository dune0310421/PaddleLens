import json
from pathlib import Path
import logging

def basic_info(task_name: str) -> dict:
    """
    获取指定用户的基本信息，包括姓名、邮箱、创建时间、仓库等
    """
    logging.info(f"Analyzing basic info for task: {task_name}")
    
    user_cache_dir = Path("cache") / task_name

    with open(user_cache_dir / "info.json", 'r', encoding='utf-8') as f:
        info = json.load(f)
    info['public_repos_cnt'] = info.pop('public_repos')
    for key in ["created_at", "updated_at"]:
        if key in info and info[key]:
            info[key] = info[key][:10]

    # 获取用户不同身份类型的repo
    info['personal_repos_cnt'] = 0
    info['forked_repos_cnt'] = 0
    with open(user_cache_dir / "repos.json", 'r', encoding='utf-8') as f:
        repos = json.load(f)
    for repo in repos:
        if repo['parent'] is None:
            info['personal_repos_cnt'] += 1
        else:
            info['forked_repos_cnt'] += 1
    
    return info


if __name__ == "__main__":

    logging.basicConfig(
        format="%(asctime)s (PID %(process)d) [%(levelname)s] %(filename)s:%(lineno)d %(message)s",
        level=logging.INFO,
    )
    logger = logging.getLogger(__name__)

    username = 'dune0310421'
    # username = 'Aurelius84'

    info = basic_info(username)
    print(f"User {username} info: {info}")