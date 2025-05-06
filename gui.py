import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import threading
import os
from utils.file_utils import is_image_file, batch_files, image_to_bytes, bytes_to_image
from crypto.symmetric import encrypt_aes, decrypt_aes
from Crypto.Random import get_random_bytes

def generate_key_file():
    # 弹出对话框让用户选择密钥长度
    length = simpledialog.askinteger("生成密钥", "输入密钥长度（16/24/32）字节：", minvalue=16, maxvalue=32)
    if length not in (16, 24, 32):
        messagebox.showerror("错误", "密钥长度只能为16、24或32字节")
        return
    key = get_random_bytes(length)
    path = filedialog.asksaveasfilename(defaultextension=".bin", filetypes=[("二进制文件", "*.bin")], title="保存密钥文件")
    if path:
        with open(path, "wb") as f:
            f.write(key)
        messagebox.showinfo("成功", f"密钥已保存到：{path}")

def get_key_bytes(key_path):
    with open(key_path, 'rb') as kf:
        key = kf.read()
        if len(key) not in (16, 24, 32):
            raise ValueError(f"密钥长度为{len(key)}字节，AES仅支持16/24/32字节密钥")
        return key

class ImageCryptoGUI:
    def __init__(self, root):
        self.root = root
        root.title("图片加密与解密系统")
        self.tab = ttk.Notebook(root)
        self.tab_encrypt = ttk.Frame(self.tab)
        self.tab_decrypt = ttk.Frame(self.tab)
        self.tab.add(self.tab_encrypt, text='加密')
        self.tab.add(self.tab_decrypt, text='解密')
        self.tab.pack(expand=1, fill="both")
        self.build_encrypt_tab()
        self.build_decrypt_tab()

    def build_encrypt_tab(self):
        frm = self.tab_encrypt
        self.encrypt_files = []
        self.encrypt_key = ""
        ttk.Label(frm, text="选择图片文件或文件夹：").grid(row=0, column=0, sticky='w')
        ttk.Button(frm, text="选择文件", command=self.choose_encrypt_files).grid(row=0, column=1)
        ttk.Button(frm, text="选择文件夹", command=self.choose_encrypt_folder).grid(row=0, column=2)
        self.encrypt_files_label = ttk.Label(frm, text="")
        self.encrypt_files_label.grid(row=1, column=0, columnspan=3, sticky='w')
        ttk.Label(frm, text="选择密钥文件：").grid(row=2, column=0, sticky='w')
        ttk.Button(frm, text="选择", command=self.choose_encrypt_key).grid(row=2, column=1)
        ttk.Button(frm, text="生成密钥", command=generate_key_file).grid(row=2, column=2)  # 新增自动生成密钥按钮
        self.encrypt_key_label = ttk.Label(frm, text="")
        self.encrypt_key_label.grid(row=3, column=0, columnspan=3, sticky='w')
        ttk.Label(frm, text="输出目录：").grid(row=4, column=0, sticky='w')
        ttk.Button(frm, text="选择", command=self.choose_encrypt_output).grid(row=4, column=1)
        self.encrypt_output_label = ttk.Label(frm, text="")
        self.encrypt_output_label.grid(row=5, column=0, columnspan=3, sticky='w')
        self.encrypt_progress = ttk.Progressbar(frm, orient="horizontal", length=300, mode="determinate")
        self.encrypt_progress.grid(row=6, column=0, columnspan=3, pady=(10,0))
        ttk.Button(frm, text="加密", command=self.start_encrypt).grid(row=7, column=1, pady=10)

    def build_decrypt_tab(self):
        frm = self.tab_decrypt
        self.decrypt_files = []
        self.decrypt_key = ""
        ttk.Label(frm, text="选择加密文件或文件夹：").grid(row=0, column=0, sticky='w')
        ttk.Button(frm, text="选择文件", command=self.choose_decrypt_files).grid(row=0, column=1)
        ttk.Button(frm, text="选择文件夹", command=self.choose_decrypt_folder).grid(row=0, column=2)
        self.decrypt_files_label = ttk.Label(frm, text="")
        self.decrypt_files_label.grid(row=1, column=0, columnspan=3, sticky='w')
        ttk.Label(frm, text="选择密钥文件：").grid(row=2, column=0, sticky='w')
        ttk.Button(frm, text="选择", command=self.choose_decrypt_key).grid(row=2, column=1)
        ttk.Button(frm, text="生成密钥", command=generate_key_file).grid(row=2, column=2)  # 新增自动生成密钥按钮
        self.decrypt_key_label = ttk.Label(frm, text="")
        self.decrypt_key_label.grid(row=3, column=0, columnspan=3, sticky='w')
        ttk.Label(frm, text="输出目录：").grid(row=4, column=0, sticky='w')
        ttk.Button(frm, text="选择", command=self.choose_decrypt_output).grid(row=4, column=1)
        self.decrypt_output_label = ttk.Label(frm, text="")
        self.decrypt_output_label.grid(row=5, column=0, columnspan=3, sticky='w')
        self.decrypt_progress = ttk.Progressbar(frm, orient="horizontal", length=300, mode="determinate")
        self.decrypt_progress.grid(row=6, column=0, columnspan=3, pady=(10,0))
        ttk.Button(frm, text="解密", command=self.start_decrypt).grid(row=7, column=1, pady=10)

    # 选择与回显
    def choose_encrypt_files(self):
        files = filedialog.askopenfilenames(filetypes=[("图片文件", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
        self.encrypt_files = list(files)
        self.encrypt_files_label.config(text="已选"+str(len(self.encrypt_files))+"个文件")
    def choose_encrypt_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.encrypt_files = batch_files(folder)
            self.encrypt_files_label.config(text="已选"+str(len(self.encrypt_files))+"个文件")
    def choose_encrypt_key(self):
        key = filedialog.askopenfilename(title="选择密钥文件")
        if key:
            try:
                key_bytes = get_key_bytes(key)
            except Exception as e:
                messagebox.showerror("密钥错误", str(e))
                return
            self.encrypt_key = key
            self.encrypt_key_label.config(text=os.path.basename(key) + f"（{len(key_bytes)}字节）")
    def choose_encrypt_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.encrypt_output = folder
            self.encrypt_output_label.config(text=folder)

    def choose_decrypt_files(self):
        files = filedialog.askopenfilenames(filetypes=[("加密文件", "*.enc")])
        self.decrypt_files = list(files)
        self.decrypt_files_label.config(text="已选"+str(len(self.decrypt_files))+"个文件")
    def choose_decrypt_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.decrypt_files = [os.path.join(folder, fn) for fn in os.listdir(folder) if fn.endswith('.enc')]
            self.decrypt_files_label.config(text="已选"+str(len(self.decrypt_files))+"个文件")
    def choose_decrypt_key(self):
        key = filedialog.askopenfilename(title="选择密钥文件")
        if key:
            try:
                key_bytes = get_key_bytes(key)
            except Exception as e:
                messagebox.showerror("密钥错误", str(e))
                return
            self.decrypt_key = key
            self.decrypt_key_label.config(text=os.path.basename(key) + f"（{len(key_bytes)}字节）")
    def choose_decrypt_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.decrypt_output = folder
            self.decrypt_output_label.config(text=folder)

    # 加密与解密线程
    def start_encrypt(self):
        if not self.encrypt_files or not hasattr(self, 'encrypt_output') or not self.encrypt_key:
            messagebox.showerror("错误", "请填写所有信息")
            return
        try:
            key_bytes = get_key_bytes(self.encrypt_key)
        except Exception as e:
            messagebox.showerror("密钥错误", str(e))
            return
        threading.Thread(target=self.encrypt_files_thread, args=(key_bytes,)).start()

    def encrypt_files_thread(self, key_bytes):
        count = len(self.encrypt_files)
        self.encrypt_progress["maximum"] = count
        for idx, file in enumerate(self.encrypt_files):
            try:
                data = image_to_bytes(file)
                enc_data = encrypt_aes(data, key_bytes)
                out_name = os.path.splitext(os.path.basename(file))[0] + ".enc"
                out_path = os.path.join(self.encrypt_output, out_name)
                with open(out_path, 'wb') as f:
                    f.write(enc_data)
            except Exception as e:
                with open("log/app.log", "a") as logf:
                    logf.write(f"加密失败:{file} {e}\n")
            self.encrypt_progress["value"] = idx + 1
            self.root.update_idletasks()
        messagebox.showinfo("完成", "加密操作完成！")

    def start_decrypt(self):
        if not self.decrypt_files or not hasattr(self, 'decrypt_output') or not self.decrypt_key:
            messagebox.showerror("错误", "请填写所有信息")
            return
        try:
            key_bytes = get_key_bytes(self.decrypt_key)
        except Exception as e:
            messagebox.showerror("密钥错误", str(e))
            return
        threading.Thread(target=self.decrypt_files_thread, args=(key_bytes,)).start()

    def decrypt_files_thread(self, key_bytes):
        count = len(self.decrypt_files)
        self.decrypt_progress["maximum"] = count
        for idx, file in enumerate(self.decrypt_files):
            try:
                with open(file, 'rb') as f:
                    enc_data = f.read()
                dec_data = decrypt_aes(enc_data, key_bytes)
                out_name = os.path.splitext(os.path.basename(file))[0] + "_dec.png"
                out_path = os.path.join(self.decrypt_output, out_name)
                bytes_to_image(dec_data, out_path)
            except Exception as e:
                with open("log/app.log", "a") as logf:
                    logf.write(f"解密失败:{file} {e}\n")
            self.decrypt_progress["value"] = idx + 1
            self.root.update_idletasks()
        messagebox.showinfo("完成", "解密操作完成！")