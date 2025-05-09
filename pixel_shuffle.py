#pixel_shuffle v13

import hashlib
import numpy as np
from PIL import Image

def get_sha256(input: str) -> str:
    """计算字符串的SHA-256哈希值"""
    return hashlib.sha256(input.encode('utf-8')).hexdigest()

def get_range(input: str, offset: int, range_len=4) -> str:
    offset = offset % len(input)
    return (input*2)[offset:offset+range_len]

def shuffle_arr(arr: np.ndarray, key: str) -> None:
    """原地打乱数组"""
    sha_key = get_sha256(key)
    arr_len = len(arr)
    for i in range(arr_len):
        idx = arr_len - i - 1
        to_index = int(get_range(sha_key, i, range_len=8), 16) % (arr_len - i)
        arr[idx], arr[to_index] = arr[to_index], arr[idx]

def encrypt_image(image: Image.Image, password: str) -> np.ndarray | None:
    """像素重排加密"""
    try:
        width, height = image.width, image.height
        x_arr = np.arange(width)
        y_arr = np.arange(height)
        shuffle_arr(x_arr, password)
        shuffle_arr(y_arr, get_sha256(password))
        arr = np.array(image)
        arr = arr[y_arr, :, ...]
        arr = np.transpose(arr, (1, 0, 2))
        arr = arr[x_arr, :, ...]
        arr = np.transpose(arr, (1, 0, 2))
        return arr
    except Exception:
        return None

def decrypt_image(image: Image.Image, password: str) -> np.ndarray | None:
    """像素重排解密"""
    try:
        width, height = image.width, image.height
        x_arr = np.arange(width)
        y_arr = np.arange(height)
        shuffle_arr(x_arr, password)
        shuffle_arr(y_arr, get_sha256(password))
        arr = np.array(image)
        arr = np.transpose(arr, (1, 0, 2))
        inv_x = np.argsort(x_arr)
        arr = arr[inv_x, :, ...]
        arr = np.transpose(arr, (1, 0, 2))
        inv_y = np.argsort(y_arr)
        arr = arr[inv_y, :, ...]
        return arr
    except Exception:
        return None