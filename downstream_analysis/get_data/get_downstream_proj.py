import csv
import os
import sys
import subprocess
import time
import random

def get_downstream_proj(repo_owner, repo_name, output_dir):
    """
    repo_owner: GitHub repsitory owner
    repo_name: GitHub repo name
    output_dir: Directory to save the output CSV file

    使用github-dependents-info工具获取指定GitHub仓库的下游依赖信息，并保存为CSV文件
    """
    output_file = os.path.join(output_dir, f"{repo_owner}_{repo_name}_downstream.csv")
    if os.path.exists(output_file):
        print(f"file exists: {output_file}")
        return
    
    python_module_path = os.path.abspath("github-dependents-info")
    env = os.environ.copy()
    env["PYTHONPATH"] = python_module_path + os.pathsep + env.get("PYTHONPATH", "")
    cmd = [
        "python",
        "-m",
        "github_dependents_info",
        "--repo", f"{repo_owner}/{repo_name}",
        "--mergepackages",
        "--csv"
    ]
    with open(output_file, "w", encoding="utf-8") as outfile:
        print(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, stdout=outfile, env=env)


if __name__ == "__main__":

    # 获取某个项目的下游项目信息
    paddle_downstream_info = get_downstream_proj('PaddlePaddle', 'Paddle', 'data')

    # 获取一系列项目的下游项目信息
    csv_path = '../data/paddle_downstream.csv'
    output_dir = '../data/paddle_downstream_2_over100'
    # # csv_path = '../data/test.csv'
    # # output_dir = '../data/test_downstream_2_over100'
    os.makedirs(output_dir, exist_ok=True)

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)

        for row in reader:
            if not row or len(row) < 3:
                continue
            repo_owner, repo_name, stars = row[0].strip(), row[1].strip(), int(row[2].strip())
            if stars < 100:
                continue

            get_downstream_proj(repo_owner, repo_name, output_dir)

            # 延迟，防止限流封IP
            delay = random.uniform(2, 5)
            print(f"Sleeping for {delay:.2f} seconds...")
            time.sleep(delay)