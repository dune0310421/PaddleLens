import argparse
from glob import glob
import json
import os
import sys

from dotenv import load_dotenv
import requests

save_count = 0

TEMP_DIR = "temp_data"

os.makedirs(TEMP_DIR, exist_ok=True)


metrics = {
    "vigor": {
        "communication activity": {
            "number of comments": {
                "total": 0,
                "recent": 0,
            },
            "number of issues": {
                "total": 0,
                "recent": 0,
            },
        },
        "development activity": {
            "core developer activity": {
                "number of core developer reviews": {
                    "total": 0,
                    "recent": 0,
                },
            },
            "overall development activity": {
                "number of pull requests": {
                    "total": 0,
                    "recent": 0,
                },
                "number of commits": {
                    "total": 0,
                    "recent": 0,
                },
                "requirement completion ratio": {
                    "number of requirement issues closed": {
                        "total": 0,
                        "recent": 0,
                    },
                    "number of requirement issues": {
                        "total": 0,
                        "recent": 0,
                    },
                    "ratio": {
                        "total": 0,
                        "recent": 0,
                    },
                },
            },
        },
        "release activity": {
            "number of releases": {
                "total": 0,
                "recent": 0,
            },
        },
    },
    "organization": {
        "size": {
            "number of contributors": {
                "total": 0,
                "recent": 0,
            },
            "number of core contributors": 0,
        },
        "diversity": {
            "company": "Check from OSS Insight",
            "experience": {
                "acceptence rate of pull requests": {
                    "number of merged pull requests": {
                        "total": 0,
                        "recent": 0,
                    },
                    "number of pull requests": {
                        "total": 0,
                        "recent": 0,
                    },
                    "ratio": {
                        "total": 0,
                        "recent": 0,
                    },
                },
                "close rate of issues": {
                    "number of issues closed": {
                        "total": 0,
                        "recent": 0,
                    },
                    "number of issues": {
                        "total": 0,
                        "recent": 0,
                    },
                    "ratio": {
                        "total": 0,
                        "recent": 0,
                    },
                },
            },
        },
        "rules": {
            "guidance": [
                "process maturity",
                "new-comer guidance",
            ],
            "incentive system": [
                "level of gamification",
                "recognition mechanism",
                "financial support",
                "dynamic developer roles",
            ],
        },
    },
    "resilience": {
        "attraction": {
            "new contributor rate": {
                "number of new contributors": 0,
                "number of contributors": 0,
                "ratio": 0,
            }
        },
        "retention": {
            "contributor retention rate": {
                "number of retention contributors": 0,
                "number of contributors before": 0,
                "ratio": 0,
            }
        },
    },
    "services": {
        "value": {
            "popularity": {
                "stars": 0,
                "forks": 0,
                "watches": 0,
                "dependents": {
                    "repositories": 0,
                    "packages": 0,
                },
            }
        }
    },
}


def save_current_data():
    """保存阶段数据"""
    global save_count
    filename = os.path.join(TEMP_DIR, f"stage_{save_count}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    save_count += 1


# ********环境变量*******
load_dotenv()

token = os.getenv("GITHUB_TOKEN")

if not token:
    sys.exit("未提供 GitHub token，设置 GITHUB_TOKEN 环境变量")


# *******运行参数*******
parser = argparse.ArgumentParser(description="开源项目健康度量")
parser.add_argument("repo", help="GitHub 仓库，例如: PaddlePaddle/Paddle")
parser.add_argument(
    "--days",
    type=int,
    default=90,
    required=True,
    help="近期数据的时间范围（天数），默认为90",
)
parser.add_argument(
    "--label",
    default="type/feature-request",
    required=True,
    help="用于表示“新功能需求”的标签名称；多个标签请用英文逗号分隔",
)

args = parser.parse_args()

owner, repo = args.repo.split("/", 1)
label = args.label
days = args.days

print(
    f"将对{owner}/{repo}进行数据收集，以{label}为功能需求的标签名，将近期设为{days}天内。"
)

# ------检查一下repo名称------
url = f"https://api.github.com/repos/{owner}/{repo}"
headers = {"Authorization": f"token {token}"}
response = requests.get(url, headers=headers)

if response.status_code == 200:
    print("该仓库确认存在。")
elif response.status_code == 404:
    sys.exit("该仓库不存在，请检查参数设置。")
else:
    response.raise_for_status()

# =====COMMENTS=======
from fetcher.fetch_comments import fetch_total_count_and_comments

print("Fetching comments...")
##  all
###     issues
issue_total, issue_comments = fetch_total_count_and_comments(
    "issues", token, owner, repo
)
###     prs
pr_total, pr_comments = fetch_total_count_and_comments(
    "pullRequests", token, owner, repo
)
# total_comments_count = issue_comments + pr_comments
metrics["vigor"]["communication activity"]["number of comments"]["total"] = (
    issue_comments + pr_comments
)
save_current_data()

##  recent
###     issues
issue_recent, issue_recent_comments = fetch_total_count_and_comments(
    "issues", token, owner, repo, days
)

###     prs
pr_recent, pr_recent_comments = fetch_total_count_and_comments(
    "pullRequests", token, owner, repo, days
)
# recent_comments_count = issue_recent_comments + pr_recent_comments
metrics["vigor"]["communication activity"]["number of comments"]["recent"] = (
    issue_recent_comments + pr_recent_comments
)

save_current_data()

# ========REVIEWS=========
from fetcher.fetch_reviews import fetch_total_reviews

print("Fetching reviews...")
## all
total_pr_count, total_review_count = fetch_total_reviews(token, owner, repo)

## recent
recent_pr_count, recent_reviews_count = fetch_total_reviews(token, owner, repo, days)

metrics["vigor"]["development activity"]["core developer activity"][
    "number of core developer reviews"
]["total"] = total_review_count

metrics["vigor"]["development activity"]["core developer activity"][
    "number of core developer reviews"
]["recent"] = recent_reviews_count

save_current_data()

# ==========COMMITS============
from fetcher.fetch_commits import (
    clone_repo,
    fetch_active_contributor,
    fetch_commit_count,
    fetch_total_contributors,
)

print("Fetching commits...")
clone_repo(owner, repo)

total_commit_count = fetch_commit_count(owner, repo)
recent_commit_count = fetch_commit_count(owner, repo, days)

metrics["vigor"]["development activity"]["overall development activity"][
    "number of commits"
]["total"] = total_commit_count

metrics["vigor"]["development activity"]["overall development activity"][
    "number of commits"
]["recent"] = recent_commit_count

save_current_data()

# -----------CONTRIBUTORS----------
print("Fetching contributors...")
total_contributor_count, recent_contributor_count = fetch_total_contributors(
    owner, repo, days
)

metrics["organization"]["size"]["number of contributors"][
    "total"
] = total_contributor_count

metrics["organization"]["size"]["number of contributors"][
    "recent"
] = recent_contributor_count

save_current_data()

# ------------RECENT ACTIVE DEVELOPERS---------
print("Fetching active developers...")
(
    total_new_contributor_count,
    total_retention_contributor_count,
    total_before_contributor_count,
) = fetch_active_contributor(owner, repo, days)

# ----attraction----
attraction_ratio = total_new_contributor_count / recent_contributor_count

metrics["resilience"]["attraction"]["new contributor rate"][
    "number of new contributors"
] = total_new_contributor_count

metrics["resilience"]["attraction"]["new contributor rate"][
    "number of contributors"
] = recent_contributor_count

metrics["resilience"]["attraction"]["new contributor rate"]["ratio"] = attraction_ratio

save_current_data()

# -----retention----
retention_ratio = total_retention_contributor_count / total_before_contributor_count

metrics["resilience"]["retention"]["contributor retention rate"][
    "number of retention contributors"
] = total_retention_contributor_count

metrics["resilience"]["retention"]["contributor retention rate"][
    "number of contributors before"
] = total_before_contributor_count

metrics["resilience"]["retention"]["contributor retention rate"][
    "ratio"
] = retention_ratio

save_current_data()

# =========REQUIREMENT=========
from fetcher.fetch_requirement import fetch_request_issue

print("Fetching requirements...")
# ----total----
total_req_issues = fetch_request_issue(token, owner, repo, label)
closed_req_issues = fetch_request_issue(token, owner, repo, label, state="closed")
total_req_close_ratio = closed_req_issues / total_req_issues

metrics["vigor"]["development activity"]["overall development activity"][
    "requirement completion ratio"
]["number of requirement issues closed"]["total"] = closed_req_issues

metrics["vigor"]["development activity"]["overall development activity"][
    "requirement completion ratio"
]["number of requirement issues"]["total"] = total_req_issues

metrics["vigor"]["development activity"]["overall development activity"][
    "requirement completion ratio"
]["ratio"]["total"] = total_req_close_ratio

save_current_data()

# ----recent----
recent_req_issues = fetch_request_issue(token, owner, repo, label, days=days)
recent_closed_req_issues = fetch_request_issue(
    token, owner, repo, label, state="closed", days=days
)
recent_req_close_ratio = recent_closed_req_issues / recent_req_issues


metrics["vigor"]["development activity"]["overall development activity"][
    "requirement completion ratio"
]["number of requirement issues closed"]["recent"] = recent_closed_req_issues

metrics["vigor"]["development activity"]["overall development activity"][
    "requirement completion ratio"
]["number of requirement issues"]["recent"] = recent_req_issues

metrics["vigor"]["development activity"]["overall development activity"][
    "requirement completion ratio"
]["ratio"]["recent"] = recent_req_close_ratio

save_current_data()

# ==========RELEASES==========
from fetcher.fetch_releases import fetch_total_releases

print("Fetching releases...")
total_release_count, recent_release_count = fetch_total_releases(
    token, owner, repo, days
)

metrics["vigor"]["release activity"]["number of releases"][
    "total"
] = total_release_count
metrics["vigor"]["release activity"]["number of releases"][
    "recent"
] = recent_release_count

save_current_data()

# ===========CORE CONTRIBUTOR==========
from fetcher.fetch_core_contributors import fetch_total_core_contributors

print("Fetching core contributors...")
total_core_contributors = fetch_total_core_contributors(token, owner)

metrics["organization"]["size"]["number of core contributors"] = total_core_contributors

save_current_data()

# =========EXPERIENCE=======
# ========pr merged ratio=========
print("Fetching PR merge rate...")
from fetcher.fetch_experience import fetch_selected_pr_or_issue_count

total_merged_pr_count, recent_merged_pr_count = fetch_selected_pr_or_issue_count(
    "pr", token, owner, repo, "merged", days
)
total_all_pr_count, recent_all_pr_count = fetch_selected_pr_or_issue_count(
    "pr", token, owner, repo, None, days
)

total_merged_pr_ratio = total_merged_pr_count / total_all_pr_count
recent_merged_pr_ratio = recent_merged_pr_count / recent_all_pr_count

# ----total---
metrics["organization"]["diversity"]["experience"]["acceptence rate of pull requests"][
    "number of merged pull requests"
]["total"] = total_merged_pr_count
metrics["organization"]["diversity"]["experience"]["acceptence rate of pull requests"][
    "number of pull requests"
]["total"] = total_all_pr_count
metrics["organization"]["diversity"]["experience"]["acceptence rate of pull requests"][
    "ratio"
]["total"] = total_merged_pr_ratio

metrics["vigor"]["development activity"]["overall development activity"][
    "number of pull requests"
]["total"] = total_all_pr_count

save_current_data()

# ---recent---
metrics["organization"]["diversity"]["experience"]["acceptence rate of pull requests"][
    "number of merged pull requests"
]["recent"] = recent_merged_pr_count
metrics["organization"]["diversity"]["experience"]["acceptence rate of pull requests"][
    "number of pull requests"
]["recent"] = recent_all_pr_count
metrics["organization"]["diversity"]["experience"]["acceptence rate of pull requests"][
    "ratio"
]["recent"] = recent_merged_pr_ratio

metrics["vigor"]["development activity"]["overall development activity"][
    "number of pull requests"
]["recent"] = recent_all_pr_count

save_current_data()

# =========issue close ratio=======
print("Fetching issue close rate")
total_closed_issue_count, recent_closed_issue_count = fetch_selected_pr_or_issue_count(
    "issue", token, owner, repo, "closed", days
)
total_all_issue_count, recent_all_issue_count = fetch_selected_pr_or_issue_count(
    "issue", token, owner, repo, None, days
)

total_closed_issue_ratio = total_closed_issue_count / total_all_issue_count
recent_closed_issue_ratio = recent_closed_issue_count / recent_all_issue_count

# ---total---
metrics["organization"]["diversity"]["experience"]["close rate of issues"][
    "number of issues closed"
]["total"] = total_closed_issue_count
metrics["organization"]["diversity"]["experience"]["close rate of issues"][
    "number of issues"
]["total"] = total_all_issue_count
metrics["organization"]["diversity"]["experience"]["close rate of issues"]["ratio"][
    "total"
] = total_closed_issue_ratio

metrics["vigor"]["communication activity"]["number of issues"][
    "total"
] = total_all_issue_count

save_current_data()

# ---recent---
metrics["organization"]["diversity"]["experience"]["close rate of issues"][
    "number of issues closed"
]["recent"] = recent_closed_issue_count
metrics["organization"]["diversity"]["experience"]["close rate of issues"][
    "number of issues"
]["recent"] = recent_all_issue_count
metrics["organization"]["diversity"]["experience"]["close rate of issues"]["ratio"][
    "recent"
] = recent_closed_issue_ratio

metrics["vigor"]["communication activity"]["number of issues"][
    "recent"
] = recent_all_issue_count

save_current_data()

# ==========VALUE===============
print("Fetching repo stats...")
from fetcher.fetch_value import fetch_repo_stats

stars, forks, watches = fetch_repo_stats(token, owner, repo)

metrics["services"]["value"]["popularity"]["stars"] = stars
metrics["services"]["value"]["popularity"]["forks"] = forks
metrics["services"]["value"]["popularity"]["watches"] = watches

save_current_data()

# -------dependents--------
print("Fetching dependents...")
from fetcher.fetch_dependents import fetch_dependents_from_html

total_dependents_count = fetch_dependents_from_html(owner, repo)
metrics["services"]["value"]["popularity"]["dependents"] = total_dependents_count

save_current_data()

# ==========保存数据=========
output_file = f"./metrics/{owner}/{repo}.json"
os.makedirs(os.path.dirname(output_file), exist_ok=True)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(metrics, f, ensure_ascii=False, indent=2)

print(f"指标已保存到 {output_file} ✅")

# 删除临时文件
for file in glob(os.path.join(TEMP_DIR, "stage_*.json")):
    os.remove(file)
os.rmdir(TEMP_DIR)
