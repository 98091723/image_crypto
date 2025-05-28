
# crypto_core.py v13
import os
import time
import logging
from typing import Callable, Optional
from PIL import Image, UnidentifiedImageError
import config
import pixel_shuffle

logger = logging.getLogger("img-crypto")

class ImageCrypto:
    """图片像素重排加密/解密批处理"""

    def __init__(self):
        # 状态回调函数，用于进度或状态更新
        self._status_callback: Optional[Callable[[str, int], None]] = None
        # 停止操作标志
        self._stop_requested = False

    def set_status_callback(self, callback: Callable[[str, int], None]):
        """设置状态回调函数"""
        self._status_callback = callback

    def _update_status(self, msg: str, progress: int = -1):
        """内部方法：更新状态并记录日志"""
        if self._status_callback:
            self._status_callback(msg, progress)
        logger.info(msg)

    def stop_operations(self):
        """请求停止批量操作"""
        self._stop_requested = True

    def encrypt_image(self, image_path: str, output_dir: str, password: str) -> tuple[bool, str]:
        """
        加密单张图片
        参数:
            image_path: 原图片路径
            output_dir: 输出目录
            password: 加密密码
        返回:
            (是否成功, 消息)
        """
        try:
            if not os.path.exists(image_path):
                return False, f"文件不存在: {image_path}"
            ext = os.path.splitext(image_path)[1].lower()
            if ext not in config.SUPPORTED_FORMATS:
                return False, f"不支持的文件类型: {ext}"
            try:
                img = Image.open(image_path)
            except UnidentifiedImageError:
                return False, f"无法识别的图片: {image_path}"
            # 像素加密
            arr = pixel_shuffle.encrypt_image(img, password)
            if arr is None:
                return False, f"像素重排加密失败: {image_path}"
            # 构造输出文件名
            out_name = os.path.splitext(os.path.basename(image_path))[0] + "_enc" + ext
            os.makedirs(output_dir, exist_ok=True)
            out_path = os.path.join(output_dir, out_name)
            # 保存加密图片
            Image.fromarray(arr).save(out_path, format=img.format or "PNG")
            img.close()
            return True, f"{image_path} -> {out_path}"
        except Exception as e:
            logger.error(f"加密失败: {e}")
            return False, f"加密失败: {image_path} - {e}"

    def decrypt_image(self, enc_path: str, output_dir: str, password: str) -> tuple[bool, str]:
        """
        解密单张图片
        参数:
            enc_path: 加密图片路径
            output_dir: 输出目录
            password: 解密密码
        返回:
            (是否成功, 消息)
        """
        try:
            if not os.path.exists(enc_path):
                return False, f"文件不存在: {enc_path}"
            try:
                img = Image.open(enc_path)
            except UnidentifiedImageError:
                return False, f"无法识别的图片: {enc_path}"
            # 像素解密
            arr = pixel_shuffle.decrypt_image(img, password)
            if arr is None:
                return False, f"解密失败: 密码错误或文件损坏"
            name, ext = os.path.splitext(os.path.basename(enc_path))
            if name.endswith("_enc"):
                name = name[:-4]
            os.makedirs(output_dir, exist_ok=True)
            out_path = os.path.join(output_dir, f"{name}{ext}")
            # 保存解密图片
            Image.fromarray(arr).save(out_path, format=img.format or "PNG")
            img.close()
            return True, f"{enc_path} -> {out_path}"
        except Exception as e:
            logger.error(f"解密失败: {e}")
            return False, f"解密失败: {enc_path} - {e}"

    def batch_encrypt(self, image_paths: list[str], output_dir: str, password: str) -> tuple[bool, str, list[str]]:
        """
        批量加密图片
        参数:
            image_paths: 图片路径列表
            output_dir: 输出目录
            password: 加密密码
        返回:
            (是否全部成功, 消息, 失败的文件列表)
        """
        self._stop_requested = False
        failed = []
        total = len(image_paths)
        for i, path in enumerate(image_paths):
            if self._stop_requested:
                self._update_status("加密操作已取消", int((i/total)*100))
                return False, "操作已取消", failed
            self._update_status(f"加密中: {os.path.basename(path)}", int((i/total)*100))
            success, _ = self.encrypt_image(path, output_dir, password)
            if not success:
                failed.append(path)
        self._update_status(f"批量加密完成。成功: {total-len(failed)}/{total}", 100)
        return True, "批量加密完成", failed

    def batch_decrypt(self, enc_paths: list[str], output_dir: str, password: str) -> tuple[bool, str, list[str]]:
        """
        批量解密图片
        参数:
            enc_paths: 加密图片路径列表
            output_dir: 输出目录
            password: 解密密码
        返回:
            (是否全部成功, 消息, 失败的文件列表)
        """
        self._stop_requested = False
        failed = []
        total = len(enc_paths)
        for i, path in enumerate(enc_paths):
            if self._stop_requested:
                self._update_status("解密操作已取消", int((i/total)*100))
                return False, "操作已取消", failed
            self._update_status(f"解密中: {os.path.basename(path)}", int((i/total)*100))
            success, _ = self.decrypt_image(path, output_dir, password)
            if not success:
                failed.append(path)
        self._update_status(f"批量解密完成。成功: {total-len(failed)}/{total}", 100)
        return True, "批量解密完成", failed
