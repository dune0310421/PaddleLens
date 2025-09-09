# 开源项目健康度量指标获取

## 安装依赖
```bash
pip install -r requirements.txt
```

## 配置
新建`.env`文件，并填写以下内容：

```ini
GITHUB_TOKEN={可用的 GitHub token}
```

示例：
```ini
GITHUB_TOKEN=ghp_xxxxxxxx
```

## 使用方式

- 运行主脚本：`python main.py {owner}/{repo} --days {days} --label {label}`
  - `{owner}/{repo}`：仓库名称，如`PaddlePaddle/Paddle`
  - `{days}`：将近期限定为最近多少天的数据，例如`90`表示抓取近90天的指标
  - `{label}`：GitHub issue中表明功能需求的标签名称，例如`type/feature-request`


示例：
```bash
python main.py PaddlePaddle/Paddle --days 90 --label type/feature-request
```

- 运行成功后，数据以`.json`文件形式保存至`.metrics/{owner}/{repo}.json`

示例：
```json
{
  "vigor": {
    "communication activity": {
      "number of comments": {
        "total": 148456,
        "recent": 4566
      },
      "number of issues": {
        "total": 18916,
        "recent": 148
      }
    },
    "development activity": {
      "core developer activity": {
        "number of core developer reviews": {
          "total": 148731,
          "recent": 3145
        }
      },
      "overall development activity": {
        "number of pull requests": {
          "total": 55608,
          "recent": 1788
        },
        "number of commits": {
          "total": 55207,
          "recent": 1301
        },
        "requirement completion ratio": {
          "number of requirement issues closed": {
            "total": 233,
            "recent": 5
          },
          "number of requirement issues": {
            "total": 312,
            "recent": 14
          },
          "ratio": {
            "total": 0.7467948717948718,
            "recent": 0.35714285714285715
          }
        }
      }
    },
    "release activity": {
      "number of releases": {
        "total": 65,
        "recent": 1
      }
    }
  },
  "organization": {
    "size": {
      "number of contributors": {
        "total": 1356,
        "recent": 127
      },
      "number of core contributors": 34
    },
    "diversity": {
      "company": "Check from OSS Insight",
      "experience": {
        "acceptence rate of pull requests": {
          "number of merged pull requests": {
            "total": 41204,
            "recent": 1314
          },
          "number of pull requests": {
            "total": 55608,
            "recent": 1788
          },
          "ratio": {
            "total": 0.7409725219392893,
            "recent": 0.7348993288590604
          }
        },
        "close rate of issues": {
          "number of issues closed": {
            "total": 17928,
            "recent": 50
          },
          "number of issues": {
            "total": 18916,
            "recent": 148
          },
          "ratio": {
            "total": 0.9477690843730175,
            "recent": 0.33783783783783783
          }
        }
      }
    },
    "rules": {
      "guidance": [
        "process maturity",
        "new-comer guidance"
      ],
      "incentive system": [
        "level of gamification",
        "recognition mechanism",
        "financial support",
        "dynamic developer roles"
      ]
    }
  },
  "resilience": {
    "attraction": {
      "new contributor rate": {
        "number of new contributors": 32,
        "number of contributors": 127,
        "ratio": 0.25196850393700800 
      }
    },
    "retention": {
      "contributor retention rate": {
        "number of retention contributors": 95,
        "number of contributors before": 1324,
        "ratio": 0.07175226586102719
      }
    }
  },
  "services": {
    "value": {
      "popularity": {
        "stars": 23149,
        "forks": 5791,
        "watches": 714,
        "dependents": {
          "repositories": 8452,
          "packages": 207
        }
      }
    }
  }
}

```