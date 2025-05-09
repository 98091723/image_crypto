
#config.py v13
import os

# 应用标题和描述
UI_TITLE = "图片像素重排加密系统"
UI_DESCRIPTION = (
    "一个简单、安全的图片像素重排加密/解密工具，直接操作图像像素，保持图像格式不变，但使内容无法识别。"
)
UI_THEME = "default"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp")
LOG_LEVEL = "INFO"

SUPPORTED_FORMATS = [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"]
ENCRYPTED_EXTENSION = SUPPORTED_FORMATS  # 保持原格式

ENCRYPTION_ALGORITHMS = {
    'PIXEL_SHUFFLE': '像素重排加密'
}