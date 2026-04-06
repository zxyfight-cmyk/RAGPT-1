from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb
import os
from src.config import COLLECTION_NAME, EMBEDDING_MODEL
from src.loader import load_all_documents
from src.utils import compute_md5, load_metadata, save_metadata
from src.users import get_user_folder, get_user_meta, get_user_db

# 中文文本分块
def split_text(text):
    splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", "。", "！", "？", " "],
        chunk_size=500,
        chunk_overlap=100
    )
    return splitter.split_text(text)

# 文档入库（用户隔离）
def ingest_documents(username):
    user_folder = get_user_folder(username)
    meta_path = get_user_meta(username)
    user_db_path = get_user_db(username)
    
    files = load_all_documents(user_folder)
    metadata = load_metadata(meta_path)
    new_metadata = {}

    # 加载向量模型
    model = SentenceTransformer(EMBEDDING_MODEL)
    client = chromadb.PersistentClient(path=user_db_path)
    collection_name = f"{COLLECTION_NAME}_{username}"
    
    # 清空旧数据
    try:
        client.delete_collection(collection_name)
    except:
        pass
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )

    all_texts, all_ids, all_metas = [], [], []
    for idx, (file_path, text) in enumerate(files.items()):
        if not text.strip():
            continue
        file_md5 = compute_md5(file_path)
        new_metadata[file_path] = file_md5
        chunks = split_text(text)
        for i, chunk in enumerate(chunks):
            all_texts.append(chunk)
            all_ids.append(f"{idx}_{i}")
            all_metas.append({"source": os.path.basename(file_path)})
    
    # 批量入库
    if all_texts:
        embeddings = model.encode(all_texts, convert_to_numpy=True).tolist()
        collection.add(
            ids=all_ids,
            embeddings=embeddings,
            metadatas=all_metas,
            documents=all_texts
        )
    save_metadata(meta_path, new_metadata)