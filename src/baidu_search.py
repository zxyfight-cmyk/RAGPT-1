import os
import json
import requests
from dotenv import load_dotenv

# 加载环境变量（必须！否则读不到API Key）
load_dotenv()
BAIDU_API_KEY = os.getenv("BAIDU_API_KEY")

def baidu_web_search(question: str, top_k: int = 3) -> list:
    """调用百度千帆AI搜索接口（国内可用）"""
    # 先检查Key是否配置
    if not BAIDU_API_KEY:
        return [{"error": "❌ 未配置百度API Key，请检查项目根目录的 .env 文件"}]
    
    url = "https://qianfan.baidubce.com/v2/ai_search/web_search"
    headers = {
        "Authorization": f"Bearer {BAIDU_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messages": [{"content": question, "role": "user"}],
        "search_source": "baidu_search_v2",
        "resource_type_filter": [{"type": "web", "top_k": top_k}],
        "search_recency_filter": "year"  # 只搜近一年内容
    }

    try:
        # 发起请求（超时30秒，避免卡死）
        response = requests.post(
            url, 
            headers=headers, 
            data=json.dumps(payload), 
            timeout=30
        )
        response.raise_for_status()  # 自动抛出HTTP错误（比如401/500）
        data = response.json()

        # 解析百度返回结果（适配官方接口格式）
        search_results = []
        # 优先取「搜索汇总」（如果有）
        if "result" in data and data["result"]:
            search_results.append({
                "title": "🔍 搜索汇总",
                "url": "",
                "content": data["result"]
            })
        # 再取「参考链接」
        if "references" in data:
            for ref in data["references"][:top_k]:
                search_results.append({
                    "title": ref.get("title", "无标题"),
                    "url": ref.get("url", "无链接"),
                    "content": ref.get("content", "无摘要")
                })
        return search_results

    except requests.exceptions.RequestException as e:
        return [{"error": f"🌐 网络请求失败：{str(e)}（检查网络/API Key是否正确）"}]
    except json.JSONDecodeError:
        return [{"error": "📝 百度返回格式异常，可能是API版本不兼容"}]