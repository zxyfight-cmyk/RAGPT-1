import os
from dotenv import load_dotenv
from pathlib import Path

# 加载环境变量
load_dotenv()

# 核心：自动创建桌面/ai+rag 主文件夹
BASE_DIR = Path("./runtime_data")
BASE_DIR.mkdir(exist_ok=True)

# 向量库/模型配置
COLLECTION_NAME = "rag_db"
EMBEDDING_MODEL = "shibing624/text2vec-base-chinese"

# 大模型密钥
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")
BAIDU_API_KEY = os.getenv("BAIDU_API_KEY")

# 默认检索参数
RETRIEVE_TOP_K = 3
RETRIEVE_SCORE_THRESHOLD = 0.2

# 自动生成用户专属路径
def get_user_dirs(username):
    user_root = BASE_DIR / username
    data_dir = user_root / "data"
    db_dir = user_root / "db"
    meta_dir = user_root / "metadata"
    # 自动创建所有文件夹
    data_dir.mkdir(parents=True, exist_ok=True)
    db_dir.mkdir(parents=True, exist_ok=True)
    meta_dir.mkdir(parents=True, exist_ok=True)
    return {
        "data": str(data_dir),
        "db": str(db_dir),
        "meta": str(meta_dir / f"{username}_file_index.json")
    }