import os
from dotenv import load_dotenv

load_dotenv(override=True)  # 加载 .env

SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY")
SILICONFLOW_API_BASE = os.getenv("SILICONFLOW_API_BASE") 