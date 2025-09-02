import json
import logging
import math
import os

logger = logging.getLogger(__name__)

def project_weights() -> dict:
    """
    获取项目难度
    """
    if os.path.exists("cache/paddle_repos_weights.json"):
        with open("cache/paddle_repos_weights.json", 'r', encoding='utf-8') as f:
            weight = json.load(f)
    else:    
        with open("data/paddle_repos.json", 'r', encoding='utf-8') as f:
            paddle_repos = json.load(f)        
        weight = {}
        for repo in paddle_repos:
            repo_name = repo['full_name']
            weight[repo_name] = math.log10(repo['size'] + 1)/10 # 项目大小作为难度指标
        with open("cache/paddle_repos_weights.json", 'w', encoding='utf-8') as f:
            json.dump(weight, f, indent=4, ensure_ascii=False)

    return weight

def module_weights() -> dict:
    """
    获取模块重要度
    """
    if os.path.exists("cache/paddle_repos_module_weights.json"):
        with open("cache/paddle_repos_module_weights.json", 'r', encoding='utf-8') as f:
            module_weights = json.load(f)
    else:
        with open("data/paddle_repos.json", 'r', encoding='utf-8') as f:
            paddle_repos = json.load(f)
        module_weights = {}
        for repo in paddle_repos:
            repo_owner, repo_name = repo['full_name'].split('/')            
            with open(f"data/paddle_commits/{repo_owner}_{repo_name}_commits.json", 'r', encoding='utf-8') as f:
                commits = json.load(f)
            modules = {}
            for commit in commits:
                files = commit['files']
                for file in files:
                    filename = file['filename']
                    parts = filename.split('/')
                    # 只取前两级目录作为模块名 eg: src/module1/file.py -> src/module1
                    if len(parts) > 2:
                        module = '/'.join(parts[:2])
                    else:
                        module = parts[0] # 一级及以下用第一级目录/文件名
                    modules[module] = modules.get(module, 0) + 1
            # 归一化
            log_counts = {k: math.log(v + 1) for k, v in modules.items()}
            max_log = max(log_counts.values()) if log_counts else 1 # 取最大值作为标准计算相对权重
            repo_module_weights = {k: v / max_log for k, v in log_counts.items()} # 归一化权重
            module_weights[repo['full_name']] = repo_module_weights
        with open("cache/paddle_repos_module_weights.json", 'w', encoding='utf-8') as f:
            json.dump(module_weights, f, indent=4, ensure_ascii=False)

    return module_weights

if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s (PID %(process)d) [%(levelname)s] %(filename)s:%(lineno)d %(message)s",
        level=logging.INFO,
    )

    _ = project_weights()
    _ = module_weights()
    print('done')