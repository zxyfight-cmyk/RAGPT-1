from sentence_transformers import SentenceTransformer
import chromadb
from src.config import COLLECTION_NAME, EMBEDDING_MODEL
from src.users import get_user_db

# 模型只加载一次（提升速度）
_model = None
def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model

# 检索上下文（用户隔离）
def retrieve_context(question, username, similarity_threshold=0.2, top_k=5):
    user_db_path = get_user_db(username)
    client = chromadb.PersistentClient(path=user_db_path)
    
    try:
        collection = client.get_collection(f"{COLLECTION_NAME}_{username}")
    except:
        return []

    model = get_model()
    query_embedding = model.encode(question).tolist()
    
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    source_list = []
    seen_files = set()
    if results["documents"]:
        for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
            filename = meta.get("source", "未知文件")
            similarity = round(1 - dist, 2)
            if similarity >= similarity_threshold and similarity >= 0 and filename not in seen_files:
                seen_files.add(filename)
                source_list.append({
                    "source": filename,
                    "similarity": similarity,
                    "content": doc
                })
    return source_list