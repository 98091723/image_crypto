
# gui.py_v13
import os
import gradio as gr
import time
from typing import Optional
import config
import utils
import crypto_core
import threading

# 新增
import tkinter as tk
from tkinter import filedialog

class CryptoGUI:
    def __init__(self):
        self.crypto = crypto_core.ImageCrypto()
        utils.setup_folders()
        self.status_message = ""
        self.progress = 0
        self.operation_thread: Optional[threading.Thread] = None
        self.result_files: Optional[list[str]] = None
        self.build_interface()

    # 新增本地目录选择弹窗功能
    def select_local_directory(self):
        import tkinter as tk
        from tkinter import filedialog

        try:
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口
            root.wm_attributes('-topmost', 1)  # 弹窗置顶
            # 使弹窗居中
            root.update_idletasks()
            # 调用文件夹选择对话框
            folder = filedialog.askdirectory(title="选择输出目录", parent=root)
            root.destroy()
            if folder:
                return gr.update(value=folder)
            else:
                return gr.update()
        except Exception as e:
            return gr.update(value=f"选择目录出错：{e}")

    def build_interface(self):
        with gr.Blocks(title=config.UI_TITLE, theme=config.UI_THEME) as self.interface:
            gr.Markdown(f"# {config.UI_TITLE}")
            gr.Markdown(config.UI_DESCRIPTION)

            with gr.Tab("图片加密"):
                with gr.Row():
                    with gr.Column():
                        encrypt_password = gr.Textbox(
                            label="加密密码",
                            placeholder="请输入8~32位，包含大小写字母和数字",
                            type="password"
                        )
                        generate_btn = gr.Button("生成随机密码")
                        encrypt_show_password = gr.Checkbox(
                            label="显示密码",
                            value=False
                        )
                        encrypt_files = gr.File(
                            label="选择要加密的图片文件",
                            file_count="multiple",
                            file_types=config.SUPPORTED_FORMATS,
                            type="filepath"
                        )
                        gr.Markdown("**密码要求**：8-32位，必须包含大写字母、小写字母和数字")
                        with gr.Row():
                            encrypt_output_dir = gr.Textbox(
                                label="输出目录(可选)",
                                value=""
                            )
                            # 新增本地选择目录按钮
                            encrypt_dir_btn = gr.Button("本地选择输出目录", elem_id="btn-local-dir-encrypt")
                        encrypt_btn = gr.Button("开始加密", variant="primary")
                        encrypt_cancel_btn = gr.Button("取消操作")
                    with gr.Column():
                        encrypt_info = gr.Textbox(
                            label="信息",
                            interactive=False,
                            lines=6
                        )
                        encrypt_progress = gr.Slider(
                            minimum=0, maximum=100, value=0, step=1, label="进度"
                        )
                        encrypt_result = gr.File(
                            label="加密结果",
                            file_count="multiple",
                            interactive=False,
                            type="filepath",
                            visible=False
                        )

            with gr.Tab("图片解密"):
                with gr.Row():
                    with gr.Column():
                        decrypt_password = gr.Textbox(
                            label="解密密码",
                            type="password",
                            placeholder="与加密时一致"
                        )
                        decrypt_show_password = gr.Checkbox(
                            label="显示密码",
                            value=False
                        )
                        decrypt_files = gr.File(
                            label="选择要解密的文件",
                            file_count="multiple",
                            file_types=config.ENCRYPTED_EXTENSION,
                            type="filepath"
                        )
                        with gr.Row():
                            decrypt_output_dir = gr.Textbox(
                                label="输出目录(可选)",
                                value=""
                            )
                            # 新增本地选择目录按钮
                            decrypt_dir_btn = gr.Button("本地选择输出目录", elem_id="btn-local-dir-decrypt")
                        decrypt_btn = gr.Button("开始解密", variant="primary")
                        decrypt_cancel_btn = gr.Button("取消操作")
                    with gr.Column():
                        decrypt_info = gr.Textbox(
                            label="信息",
                            interactive=False,
                            lines=6
                        )
                        decrypt_progress = gr.Slider(
                            minimum=0, maximum=100, value=0, step=1, label="进度"
                        )
                        decrypt_result = gr.File(
                            label="解密结果",
                            file_count="multiple",
                            interactive=False,
                            type="filepath",
                            visible=False
                        )

            with gr.Tab("帮助说明"):
                gr.Markdown("""
### 使用说明

**加密：**
1. 上传图片，输入合法密码（8-32位，含大写、小写、数字）。
2. 可手动填写输出目录，或点击“本地选择输出目录”按钮弹窗选择。
3. 点击“开始加密”，完成后可下载加密文件。

**解密：**
1. 上传加密后文件，输入密码。
2. 可手动填写输出目录，或点击“本地选择输出目录”按钮弹窗选择。
3. 点击“开始解密”，完成后可下载解密图片。
                """)

            # 本地选择目录按钮绑定
            encrypt_dir_btn.click(
                fn=lambda: self.select_local_directory(),
                outputs=[encrypt_output_dir]
            )
            decrypt_dir_btn.click(
                fn=lambda: self.select_local_directory(),
                outputs=[decrypt_output_dir]
            )

            # 密码显示/隐藏与生成
            generate_btn.click(
                fn=utils.generate_secure_password,
                outputs=[encrypt_password]
            )
            def toggle_password_visibility(password, show_password):
                return gr.update(value=password, type="text" if show_password else "password")
            encrypt_show_password.change(
                fn=toggle_password_visibility,
                inputs=[encrypt_password, encrypt_show_password],
                outputs=[encrypt_password]
            )
            decrypt_show_password.change(
                fn=toggle_password_visibility,
                inputs=[decrypt_password, decrypt_show_password],
                outputs=[decrypt_password]
            )

            # ========== 加密/解密按钮 ===========
            encrypt_btn.click(
                fn=self.start_encrypt,
                inputs=[encrypt_files, encrypt_password, encrypt_output_dir],
                outputs=[encrypt_info, encrypt_progress, encrypt_result]
            )
            encrypt_cancel_btn.click(
                fn=self.cancel_operation,
                outputs=[encrypt_info]
            )
            decrypt_btn.click(
                fn=self.start_decrypt,
                inputs=[decrypt_files, decrypt_password, decrypt_output_dir],
                outputs=[decrypt_info, decrypt_progress, decrypt_result]
            )
            decrypt_cancel_btn.click(
                fn=self.cancel_operation,
                outputs=[decrypt_info]
            )

            self.crypto.set_status_callback(self.update_status)

    def launch(self, share=False):
        self.interface.launch(share=share)

    def start_encrypt(self, files, password, output_dir):
        if not files:
            return "请选择要加密的图片", 0, None
        is_valid, msg = utils.validate_password(password)
        if not is_valid:
            return msg, 0, None
        if not output_dir:
            output_dir = os.path.join(config.TEMP_DIR, f"enc_{int(time.time())}")
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                return f"创建输出目录失败: {e}", 0, None
        if not os.access(output_dir, os.W_OK):
            return f"输出目录无写权限: {output_dir}", 0, None

        def encrypt_thread():
            self.crypto.batch_encrypt(files, output_dir, password)
            try:
                result_files = []
                for f in os.listdir(output_dir):
                    fpath = os.path.join(output_dir, f)
                    if os.path.isfile(fpath) and f.endswith("_enc"+os.path.splitext(f)[1]):
                        result_files.append(fpath)
                self.status_message = f"加密完成：{len(result_files)}个文件"
                self.result_files = result_files if result_files else None
            except Exception as e:
                self.status_message = f"结果文件获取失败: {e}"
                self.result_files = None

        self.status_message = "正在加密，请稍候..."
        self.progress = 0
        self.result_files = None
        self.operation_thread = threading.Thread(target=encrypt_thread)
        self.operation_thread.start()
        return self.status_message, self.progress, None

    def start_decrypt(self, files, password, output_dir):
        if not files:
            return "请选择要解密的文件", 0, None
        if not password:
            return "请输入解密密码", 0, None
        if not output_dir:
            output_dir = os.path.join(config.TEMP_DIR, f"dec_{int(time.time())}")
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                return f"创建输出目录失败: {e}", 0, None
        if not os.access(output_dir, os.W_OK):
            return f"输出目录无写权限: {output_dir}", 0, None

        def decrypt_thread():
            self.crypto.batch_decrypt(files, output_dir, password)
            try:
                result_files = []
                for f in os.listdir(output_dir):
                    fpath = os.path.join(output_dir, f)
                    if os.path.isfile(fpath) and os.path.splitext(f)[1].lower() in config.SUPPORTED_FORMATS:
                        result_files.append(fpath)
                self.status_message = f"解密完成：{len(result_files)}个文件"
                self.result_files = result_files if result_files else None
            except Exception as e:
                self.status_message = f"结果文件获取失败: {e}"
                self.result_files = None

        self.status_message = "正在解密，请稍候..."
        self.progress = 0
        self.result_files = None
        self.operation_thread = threading.Thread(target=decrypt_thread)
        self.operation_thread.start()
        return self.status_message, self.progress, None

    def cancel_operation(self):
        self.status_message = "正在取消操作..."
        self.crypto.stop_operations()
        return self.status_message

    def update_status(self, message, progress):
        self.status_message = message
        if progress >= 0:
            self.progress = progress
