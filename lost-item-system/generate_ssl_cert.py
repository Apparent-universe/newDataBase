#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSL证书生成脚本 - 改进版
用于生成开发环境的自签名SSL证书，以支持HTTPS和地理定位功能
"""

import os
import datetime
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import ipaddress
import socket

def get_local_ip():
    """获取本机IP地址"""
    try:
        # 方法1：连接外部地址获取本机IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        try:
            # 方法2：使用hostname
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
        except:
            return "192.168.1.100"  # 默认值

def generate_ssl_certificate(custom_ip=None):
    """生成自签名SSL证书"""
    
    print("正在生成SSL证书...")
    
    # 生成私钥
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # 获取IP地址
    if custom_ip:
        local_ip = custom_ip
        print(f"使用指定IP: {local_ip}")
    else:
        local_ip = get_local_ip()
        print(f"检测到本机IP: {local_ip}")
    
    # 验证IP地址格式
    try:
        ipaddress.ip_address(local_ip)
    except ValueError:
        print(f"❌ 无效的IP地址: {local_ip}")
        return False
    
    # 证书主题信息
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "CN"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Beijing"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Beijing"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Lost Item System"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Development"),
        x509.NameAttribute(NameOID.COMMON_NAME, local_ip),
    ])
    
    # 构建SAN列表
    san_list = [
        x509.DNSName("localhost"),
        x509.DNSName("127.0.0.1"),
        x509.IPAddress(ipaddress.ip_address("127.0.0.1")),
    ]
    
    # 添加自定义IP
    if local_ip not in ["127.0.0.1", "localhost"]:
        san_list.extend([
            x509.DNSName(local_ip),
            x509.IPAddress(ipaddress.ip_address(local_ip))
        ])
    
    # 创建证书
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.now(datetime.UTC)
    ).not_valid_after(
        datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName(san_list),
        critical=False,
    ).sign(private_key, hashes.SHA256())
    
    # 保存证书文件
    cert_path = "cert.pem"
    key_path = "key.pem"
    
    # 写入证书
    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    # 写入私钥
    with open(key_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    print(f"✅ SSL证书生成成功!")
    print(f"   证书文件: {os.path.abspath(cert_path)}")
    print(f"   私钥文件: {os.path.abspath(key_path)}")
    print(f"   有效期: 365天")
    print(f"   支持的地址:")
    print(f"     - https://localhost:5050")
    print(f"     - https://127.0.0.1:5050")
    if local_ip not in ["127.0.0.1", "localhost"]:
        print(f"     - https://{local_ip}:5050")
    print()
    print("⚠️  浏览器安全提醒:")
    print("   由于这是自签名证书，浏览器会显示安全警告")
    print("   请在浏览器中点击'高级'然后选择'继续访问'")
    print("   这在开发环境中是安全的")
    
    return True

def main():
    print("=== SSL证书生成工具 (改进版) ===")
    print("用于失物招领系统的HTTPS支持")
    print()
    
    # 获取用户输入
    detected_ip = get_local_ip()
    print(f"自动检测到的IP: {detected_ip}")
    print()
    print("请选择操作:")
    print("1. 使用检测到的IP地址")
    print("2. 手动输入IP地址 (推荐：192.168.31.133)")
    print("3. 仅支持localhost (127.0.0.1)")
    
    choice = input("\n请输入选择 (1/2/3): ").strip()
    
    if choice == "1":
        target_ip = detected_ip
    elif choice == "2":
        target_ip = input("请输入您的IP地址 (例如: 192.168.31.133): ").strip()
        if not target_ip:
            print("❌ IP地址不能为空")
            return
    elif choice == "3":
        target_ip = "127.0.0.1"
    else:
        print("❌ 无效选择")
        return
    
    print(f"\n将为以下IP生成证书: {target_ip}")
    
    try:
        if generate_ssl_certificate(target_ip):
            print("\n🎉 证书生成完成！现在可以使用HTTPS启动系统了")
            print("运行命令: python run.py")
        else:
            print("\n❌ 证书生成失败")
    except Exception as e:
        print(f"\n❌ 证书生成失败: {e}")

if __name__ == "__main__":
    main()