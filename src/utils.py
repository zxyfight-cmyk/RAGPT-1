import os
import json
import hashlib

def compute_md5(file_path: str) -> str:
    """计算文件 MD5，用于判断文件是否修改"""
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def load_metadata(meta_path: str) -> dict:
    """加载 JSON 元数据，如果损坏则返回空字典"""
    if not os.path.exists(meta_path):
        return {}
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_metadata(meta_path: str, metadata: dict):
    """保存 JSON 元数据"""
    os.makedirs(os.path.dirname(meta_path), exist_ok=True)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)