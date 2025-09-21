import json
import os
from config import  NOWDATE

class GovernanceAnalyzer:
    """
    分析飞桨的治理规则得分
    """
    def __init__(self, repo: str = "PaddlePaddle/Paddle"):
        self.repo = repo
        self.date = NOWDATE.strftime("%Y-%m-%d")
        self.scores = {
            "usage": {
                "installation_guide": 0,
                "usage_guide": 0,
                "security_policy": 0,
                "license": 0
            },
            "contribution": {
                "contribution_guidelines": {
                    "contribution_types": 0,
                    "cla": 0,
                    "communication_way": 0,
                    "mentorship": 0,
                    "local_environment_setup": 0,
                },
                "contribution_submission": {
                    "writing_standards": 0,
                    "submission_standards": 0,
                    "code_of_conduct": 0,
                },
                "contribution_acceptance": {
                    "review_standards": 0,
                    "review_process": 0,
                    "ci_description": 0
                }
            },
            "organization": {
                "role_management": {
                    "role_definition": 0,
                    "role_assignment_standards": 0,
                    "role_assignment_process": 0
                },
                "release_management": 0
            }
        }
    
    def analyze_governance(self):
        files = [
            os.path.join("data/governance_scores", f)
            for f in os.listdir("data/governance_scores")
            if f.endswith(".json")
        ]
        if not files:
            raise FileNotFoundError("找不到评分文件。")
        latest_file = max(files, key=os.path.getctime)

        with open(latest_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.scores = data

        results = {
            "date": self.date,
            "scores": self.scores,
        }
            
        return results