from zhipuai import ZhipuAI
from dotenv import load_dotenv
import os

load_dotenv()

def get_llm():
    return ZhipuAI(api_key=os.getenv("ZHIPU_API_KEY"))