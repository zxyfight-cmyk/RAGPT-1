import os
from pathlib import Path
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

import streamlit as st
from src.ingest import ingest_documents
from src.rag import generate_answer
from src.config import BASE_DIR

st.set_page_config(page_title="RAG系统", layout="wide")

# ===== 获取最近用户 =====
def get_latest_user():
    if not BASE_DIR.exists():
        return ""
    user_folders = [f for f in BASE_DIR.iterdir() if f.is_dir()]
    return max(user_folders, key=lambda x: os.path.getmtime(x)).name if user_folders else ""

# ===== 初始化 =====
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ================= Sidebar =================
with st.sidebar:
    st.markdown("## 🤖 RAG智能问答")

    username = st.text_input("👤 用户名", value=get_latest_user())

    st.markdown("### 📂 知识库")
    uploaded_files = st.file_uploader(
        "上传文件",
        type=["pdf", "docx", "txt", "md"],
        accept_multiple_files=True
    )

    if st.button("📥 更新知识库"):
        if username:
            with st.spinner("处理中..."):
                from src.users import get_user_folder
                user_folder = get_user_folder(username)

                for f in uploaded_files:
                    with open(os.path.join(user_folder, f.name), "wb") as f_out:
                        f_out.write(f.read())

                ingest_documents(username)
                st.success("✅ 完成")

    st.markdown("### 🔍 检索参数")
    top_k = st.slider("召回数量", 1, 10, 3)
    score_threshold = st.slider("相似度阈值", 0.0, 1.0, 0.3)

    st.markdown("### 🌐 联网搜索")
    use_search = st.toggle("启用联网搜索", value=False)

# ================= 主界面 =================
st.title("💬 智能问答")
st.markdown("""
### 💡 使用提示（建议先试试这些问题）：

- 🤖 你是谁？
- 🧠 你能做什么？
- ⚔️ 你和 ChatGPT 有什么区别？

📌 使用步骤：
1. 左侧上传你的文档
2. 点击「更新知识库」
3. 开始提问（如：这个方案的核心内容是什么？）
""")

# ===== 历史对话 =====
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        if "sources" in msg:
            with st.expander("📚 查看来源"):
                if msg["sources"]["local"]:
                    st.markdown("**📄 本地知识库：**")
                    for s in msg["sources"]["local"]:
                        st.markdown(f"- {s}")

                if msg["sources"]["web"]:
                    st.markdown("**🌐 联网来源：**")
                    for s in msg["sources"]["web"]:
                        st.markdown(f"- {s}")

# ===== 输入 =====
question = st.chat_input("请输入你的问题...")

if question and username:
    st.session_state.chat_history.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.spinner("思考中..."):
        answer, sources, _ = generate_answer(
            question=question,
            username=username,
            use_external_search=use_search,
            similarity_threshold=score_threshold,
            top_k=top_k,
            chat_history=st.session_state.chat_history
        )

        with st.chat_message("assistant"):
            st.markdown(answer)

            with st.expander("📚 数据来源"):
                if sources["local"]:
                    st.markdown("**📄 本地知识库：**")
                    for s in sources["local"]:
                        st.markdown(f"- {s}")

                if sources["web"]:
                    st.markdown("**🌐 联网来源：**")
                    for s in sources["web"]:
                        st.markdown(f"- {s}")

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer,
            "sources": sources
        })