# utils.py v13
import os
import random
import string
import re
import logging
import time
import config

def setup_logging():
    """初始化日志系统"""
    log_dir = os.path.join(config.BASE_DIR, "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(log_dir, f"crypto_{time.strftime('%Y%m%d')}.log")),
            logging.StreamHandler()
        ]
    )

def setup_folders():
    """确保必要的文件夹存在"""
    for folder in [config.TEMP_DIR, os.path.join(config.BASE_DIR, "logs")]:
        if not os.path.exists(folder):
            os.makedirs(folder)

def validate_password(password: str) -> tuple[bool, str]:
    """密码验证：8-32位，包含大写、小写和数字"""
    if not password:
        return False, "密码不能为空"
    if not (8 <= len(password) <= 32):
        return False, "密码长度需为8~32位"
    if not re.search(r'[A-Z]', password):
        return False, "密码必须包含大写字母"
    if not re.search(r'[a-z]', password):
        return False, "密码必须包含小写字母"
    if not re.search(r'[0-9]', password):
        return False, "密码必须包含数字"
    return True, "密码有效"

def generate_secure_password(length: int = 16) -> str:
    """生成随机安全密码"""
    if length < 8:
        length = 8
    elif length > 32:
        length = 32
    chars = string.ascii_letters + string.digits + "!@#$%&*+-=?"
    password = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits)
    ]
    password += [random.choice(chars) for _ in range(length - 3)]
    random.shuffle(password)
    return ''.join(password)

setup_logging()