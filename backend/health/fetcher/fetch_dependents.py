import os
import re
import tempfile

from bs4 import BeautifulSoup
import requests


def fetch_dependents_from_html(owner, repo):
    url = f"https://github.com/{owner}/{repo}/network/dependents"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/116.0.0.0 Safari/537.36"
    }

    # 请求页面
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        raise Exception(f"请求失败: {r.status_code}")

    # 保存 HTML
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", delete=True, suffix=".html"
    ) as tmp_file:
        tmp_file.write(r.text)
        file_path = tmp_file.name
        print(f"页面已保存到: {file_path}")

        # 解析 HTML 提取数量
        soup = BeautifulSoup(r.text, "lxml")
        counts = {}

        for a in soup.select("a.btn-link"):
            try:
                text = a.get_text(" ", strip=True)
                # Repositories 数量
                m_repo = re.search(r"([\d,]+)\s+Repositories", text)
                if m_repo:
                    counts["repositories"] = int(m_repo.group(1).replace(",", ""))
                # Packages 数量
                m_pkg = re.search(r"([\d,]+)\s+Packages", text)
                if m_pkg:
                    counts["packages"] = int(m_pkg.group(1).replace(",", ""))
            except Exception as e:
                print(f"解析时出错: {e}")
                continue

        return counts


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    owner = os.getenv("GITHUB_OWNER")
    repo = os.getenv("GITHUB_REPO")

    counts = fetch_dependents_from_html(owner, repo)
    print(f"{owner}/{repo} 被依赖情况: {counts}")
