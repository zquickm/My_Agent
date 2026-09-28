"""全局配置：唯一从环境读取秘密的地方，其他模块只从这里 import。"""
import os
from pathlib import Path

from dotenv import load_dotenv

# 本文件在 backend/app/ 下，项目根是上一级，.env 就放在那里
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# ---- LLM（OpenAI 兼容接口，换供应商只改这三个值） ----
API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
MODEL = os.getenv("LLM_MODEL", "deepseek-flash")