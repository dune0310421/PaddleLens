import numpy as np
import uuid
import datetime
import pandas as pd
import base64
import plotly.graph_objects as go
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from developer_analyzer import DeveloperAnalyzer

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to PaddleLens!"}

@app.get("/favicon.ico")
def ignore_favicon():
    return ""


# 程序员能力度量

class AnalyzeRequest(BaseModel):
    github_user: str

def clean_data(obj):
    if isinstance(obj, go.Figure):
        return clean_data(obj.to_dict()) # plotly图片先转dict，再处理dict中的每一项
    elif isinstance(obj, bytes):
        return base64.b64encode(obj).decode()
    elif isinstance(obj, (np.integer, np.int32, np.int64, np.uint32, np.uint64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.ndarray,)):
        return [clean_data(o) for o in obj.tolist()]
    elif isinstance(obj, (pd.Timestamp, datetime.datetime)):
        return obj.isoformat()
    elif isinstance(obj, (pd.Timedelta, datetime.timedelta)):
        return str(obj)
    elif isinstance(obj, (dict,)):
        return {clean_data(k): clean_data(v) for k, v in obj.items()}  # 处理dict中的每一项
    elif isinstance(obj, (list, tuple, set)):  # 处理list/tuple/set中的每一项
        return [clean_data(v) for v in obj]
    else:
        return obj


@app.post("/analyze/")
def analyze_skills(request_data: AnalyzeRequest) -> dict:
    """
    分析开发者技能，返回技能分析结果。
    """
    username = request_data.github_user
    analyzer = DeveloperAnalyzer(username)
    result = analyzer.analyze_skills()
    result = clean_data(result)

    return JSONResponse(content=result)