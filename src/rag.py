from src.assistant_identity import get_system_intro
from src.retrieve import retrieve_context
from src.llm import get_llm
from src.baidu_search import baidu_web_search

def generate_answer(question, username, use_external_search=False, similarity_threshold=0.2, top_k=3, chat_history=None):
    # ===== 0. 系统身份类问题拦截 =====
    intro_answer = get_system_intro(question)
    if intro_answer:
        return intro_answer, {"local": [], "web": []}, None

    # ===== 1. 本地检索 =====
    local_data = retrieve_context(question, username, similarity_threshold, top_k)

    # ===== 2. 无数据直接返回（防幻觉）=====
    if not local_data and not use_external_search:
        return (
            "❌ 知识库中未找到相关内容，请上传资料或开启联网搜索。",
            {"local": [], "web": []},
            None
        )

    # ===== 3. 联网（可选）=====
    search_results = []
    if use_external_search:
        search_results = baidu_web_search(question, top_k)

    # ===== 4. 构建上下文（限制长度）=====
    local_context = "\n".join([item["content"][:300] for item in local_data])

    prompt = f"""
你是一个知识助手，请基于提供的内容回答问题。

问题：
{question}

参考资料：
{local_context}

要求：
1. 用自然语言流畅回答
2. 不要逐字复制原文
3. 不要编造信息
4. 不要重复问题
5. 优先基于参考资料内容回答
"""

    # ===== 5. LLM调用 =====
    llm = get_llm()
    resp = llm.chat.completions.create(
        model="glm-4-flash",
        messages=[{"role": "user", "content": prompt}]
    )

    answer = resp.choices[0].message.content.strip()

    # ===== 6. 构建“参考原文片段”（核心升级）=====
    reference_text = "\n\n---\n### 📄 参考原文片段\n"

    for item in local_data:
        source = item["source"]
        similarity = item["similarity"]

        # 原文截断（防太长）
        snippet = item["content"][:120].replace("\n", "").strip()

        reference_text += f"""
**来源：{source}（相似度：{similarity}）**  
原文：{snippet}……
"""

    # ===== 7. 来源结构 =====
    sources = {
        "local": [
            f"{item['source']}（相似度:{item['similarity']}）"
            for item in local_data
        ],
        "web": []
    }

    # ===== 8. 联网补充（如果开启）=====
    if use_external_search and search_results:
        online_text = "\n\n📌 联网补充：\n"

        for res in search_results:
            content = res.get("content", "")
            if content:
                online_text += f"\n- {content[:100]}...\n"

        answer += online_text

        for res in search_results:
            title = res.get("title", "")
            url = res.get("url", "")
            if url:
                sources["web"].append(f"[{title}]({url})")
            else:
                sources["web"].append(title)

    # ===== 9. 最终输出 =====
    final_answer = answer + reference_text

    return final_answer, sources, None