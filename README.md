# 图片加密解密工具

## 简介
本项目是一个基于 Gradio 的图片加解密桌面工具，支持批量图片像素级加密与解密，界面美观，操作简单。适合个人隐私图片保护、简单图像信息隐藏等应用场景。

## 主要特性

- 支持批量图片加密与解密，界面操作简单
- 加密解密算法基于像素重排，安全性较高
- 密码强度校验，输入不合规即时提示
- 输出目录、密码等参数自动记忆
- 操作过程进度实时展示，支持一键打开输出目录
- 支持中文/英文界面切换
- 操作日志与详细错误信息可展开查看
- 内置帮助文档，常见问题一键查阅

## 环境依赖

- Python 3.8+
- gradio >= 3.0
- numpy
- pillow

安装依赖：
```bash
pip install gradio numpy pillow
```

## 运行方式

1. 克隆或下载本项目代码  
2. 确保 `config.py`、`utils.py`、`crypto_core.py`、`pixel_shuffle.py` 与 `gui.py`、`main.py` 在同一目录下
3. 命令行下执行：

```bash
python main.py
```

出现 Gradio 界面后，按提示操作即可。

## 目录结构

```
image_crypto/
├── main.py              # 程序入口
├── gui.py               # Gradio界面及交互逻辑
├── crypto_core.py       # 图片加解密核心算法
├── utils.py             # 工具函数（如密码校验等）
├── config.py            # 配置文件（文件类型等）
├── pixel_shuffle.py     # 像素重排算法（加解密核心见下文）
├── history_params.json  # 历史参数自动保存（程序自动生成）
├── README.md
```

## pixel_shuffle.py 说明

`pixel_shuffle.py` 实现了核心的像素级重排加解密算法。如下：

```python
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
```

### 算法简介

- **加密**：基于用户密码，生成伪随机序列，对图片像素的`x`、`y`坐标轴分别重排。经过两次转置和重排，实现图片像素的复杂混淆。
- **解密**：使用相同密码生成同样的重排顺序，利用逆置换（`np.argsort`），恢复原有像素顺序。

**注意事项**：  
- 加密和解密过程必须使用完全相同的密码，否则无法恢复原图。
- 仅支持 pillow 能读取的图片格式。

---

## 使用说明

### 1. 图片加密
- 选择要加密的图片（支持多选）
- 输入8-32位含大小写字母和数字的密码
- 选择本地输出目录（建议新建空文件夹）
- 点击“开始加密”，完成后可点击“打开输出目录”直接访问文件夹

### 2. 图片解密
- 选择已加密的图片文件（支持多选）
- 输入加密时使用的密码
- 选择输出目录
- 点击“开始解密”，完成后可点击“打开输出目录”直接访问文件夹

### 3. 其他功能
- **一键重置**：快速清空所有输入项
- **语言切换**：支持中文/英文
- **密码与目录自动记忆**：自动保存上次使用参数
- **错误日志**：操作出错时可展开查看详细日志

### 4. 常见问题
- **密码必须满足格式要求，否则无法加解密。**
- **加密图片用同样的密码方可解密恢复，忘记密码无法找回。**
- **输出目录建议为空文件夹，避免覆盖原有文件。**

## 常见问题

- **Q: 为什么解密不成功？**  
  A: 请确认输入的密码与加密时一致，且图片未被损坏。
- **Q: 支持哪些图片格式？**  
  A: 支持常见图片格式如 jpg、png、bmp 等，具体见 config.py 配置。
- **Q: 进度条不动？**  
  A: 请检查图片数量和尺寸，超大图片或批量处理时需耐心等待。

## 免责声明

本工具仅供学习与个人隐私保护用途，请勿用于非法用途。加解密算法不保证绝对安全，勿用于高强度安全需求场景。

---

如有建议或问题欢迎在 Issues 区反馈！
