# 图片加密与解密系统

## 功能
- 支持JPEG/PNG/BMP/GIF等图片批量加密与解密（AES对称加密，密钥自定义）
- 支持文件/文件夹批量操作
- 图形用户界面，操作简单
- 错误日志记录

## 运行方法
1. 安装依赖：
   ```
   pip install -r requirements.txt
   ```
2. 运行主程序：
   ```
   python main.py
   ```

## 使用说明
- 生成密钥：可用`openssl rand -out mykey.bin 16`生成16字节的密钥文件
- 保管好密钥文件，遗失无法找回原图
- 日志在`log/app.log`

## 扩展说明
- 支持AES-128/192/256（即密钥16/24/32字节）
- 可扩展RSA/混合加密算法（见`crypto/`）