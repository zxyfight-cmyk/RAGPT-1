from src.config import get_user_dirs

# 获取用户上传文件的文件夹
def get_user_folder(username: str) -> str:
    return get_user_dirs(username)["data"]

# 获取用户元数据文件路径
def get_user_meta(username: str) -> str:
    return get_user_dirs(username)["meta"]

# 获取用户专属向量库路径
def get_user_db(username: str) -> str:
    return get_user_dirs(username)["db"]