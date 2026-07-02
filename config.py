import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "Quản lý kho gỗ"

DATABASE = os.getenv("DATABASE_URL")

if DATABASE is None:
    raise ValueError("Không tìm thấy DATABASE_URL")