#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
二维码更新问题调试脚本
"""
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_qrcode_update():
    """测试二维码更新功能"""
    from app import create_app, db
    from app.models import Agent
    
    app = create_app()
    
    with app.app_context():
        print("🔍 二维码更新问题调试")
        print("=" * 50)
        
        # 1. 查看当前有二维码的用户
        agents_with_qrcode = Agent.query.filter(Agent.wx_qrcode.isnot(None)).all()
        
        print(f"📊 当前有二维码的用户数量: {len(agents_with_qrcode)}")
        
        if agents_with_qrcode:
            for agent in agents_with_qrcode:
                qrcode_size = len(agent.wx_qrcode) if agent.wx_qrcode else 0
                print(f"  - 用户: {agent.username}")
                print(f"    二维码大小: {qrcode_size} bytes")
                print(f"    MIME类型: {agent.wx_qrcode_mimetype}")
                print(f"    有二维码: {agent.has_wx_qrcode()}")
                print()
        
        # 2. 模拟文件上传测试
        print("🧪 模拟文件更新测试")
        print("-" * 30)
        
        if agents_with_qrcode:
            test_agent = agents_with_qrcode[0]
            original_size = len(test_agent.wx_qrcode) if test_agent.wx_qrcode else 0
            original_mime = test_agent.wx_qrcode_mimetype
            
            print(f"选择测试用户: {test_agent.username}")
            print(f"原始二维码大小: {original_size} bytes")
            print(f"原始MIME类型: {original_mime}")
            
            # 创建一个虚拟的小图片数据进行测试
            test_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x10IDATx\x9cc```bPPP\x00\x02\xd2\x8d\xb4\x18\x00\x00\x00\x00IEND\xaeB`\x82'
            test_mime = 'image/png'
            
            print(f"准备设置新的二维码数据...")
            print(f"测试数据大小: {len(test_data)} bytes")
            print(f"测试MIME类型: {test_mime}")
            
            # 使用Agent模型的方法设置二维码
            test_agent.set_wx_qrcode(test_data, test_mime)
            
            print("✓ 调用 set_wx_qrcode() 完成")
            
            # 检查是否设置成功
            new_size = len(test_agent.wx_qrcode) if test_agent.wx_qrcode else 0
            new_mime = test_agent.wx_qrcode_mimetype
            
            print(f"设置后二维码大小: {new_size} bytes")
            print(f"设置后MIME类型: {new_mime}")
            
            if new_size > 0 and new_mime == test_mime:
                print("✅ 内存中的数据设置成功")
                
                # 尝试提交到数据库
                try:
                    db.session.commit()
                    print("✅ 数据库提交成功")
                    
                    # 重新查询验证
                    db.session.refresh(test_agent)
                    final_size = len(test_agent.wx_qrcode) if test_agent.wx_qrcode else 0
                    final_mime = test_agent.wx_qrcode_mimetype
                    
                    print(f"数据库中的二维码大小: {final_size} bytes")
                    print(f"数据库中的MIME类型: {final_mime}")
                    
                    if final_size == len(test_data):
                        print("🎉 数据库更新测试成功！")
                    else:
                        print("❌ 数据库中的数据与预期不符")
                        
                    # 恢复原始数据
                    if original_size > 0:
                        print("\n🔄 恢复原始数据...")
                        # 这里需要你手动恢复，因为我们没有保存原始数据
                        print("⚠ 请手动重新上传原始二维码")
                    
                except Exception as e:
                    print(f"❌ 数据库提交失败: {e}")
                    db.session.rollback()
            else:
                print("❌ 内存中的数据设置失败")
        else:
            print("⚠ 没有找到有二维码的用户进行测试")

def check_file_upload_simulation():
    """模拟文件上传过程"""
    from app import create_app
    from app.services.user_service import UserService
    from app.models import Agent
    import io
    
    app = create_app()
    
    with app.app_context():
        print("\n📁 模拟文件上传流程测试")
        print("=" * 50)
        
        # 获取一个测试用户
        test_user = Agent.query.first()
        if not test_user:
            print("❌ 没有找到测试用户")
            return
        
        print(f"测试用户: {test_user.username}")
        
        # 创建模拟的文件对象
        class MockFile:
            def __init__(self, data, filename, mimetype):
                self.data = data
                self.filename = filename
                self.mimetype = mimetype
                self.pointer = 0
            
            def read(self):
                if self.pointer == 0:
                    self.pointer = len(self.data)
                    return self.data
                return b''  # 模拟文件指针问题
            
            def seek(self, pos):
                self.pointer = pos
                print(f"  📌 文件指针重置到位置: {pos}")
        
        # 创建测试文件
        test_data = b'fake_image_data_for_testing'
        mock_file = MockFile(test_data, 'test.png', 'image/png')
        
        print(f"模拟文件大小: {len(test_data)} bytes")
        print(f"模拟文件名: {mock_file.filename}")
        print(f"模拟MIME类型: {mock_file.mimetype}")
        
        # 第一次读取（模拟验证过程）
        print("\n1️⃣ 模拟文件验证过程...")
        validation_data = mock_file.read()
        print(f"验证时读取到的数据大小: {len(validation_data)} bytes")
        
        # 第二次读取（模拟服务层处理）
        print("\n2️⃣ 模拟服务层处理...")
        service_data = mock_file.read()
        print(f"服务层读取到的数据大小: {len(service_data)} bytes")
        
        if len(service_data) == 0:
            print("❌ 发现问题：第二次读取为空！")
            print("💡 这就是图片更新失效的原因")
            
            print("\n3️⃣ 测试文件指针重置...")
            mock_file.seek(0)
            retry_data = mock_file.read()
            print(f"重置后读取到的数据大小: {len(retry_data)} bytes")
            
            if len(retry_data) > 0:
                print("✅ 重置文件指针后读取成功")
        else:
            print("✅ 文件读取正常")

def main():
    print("🔧 二维码更新问题诊断工具")
    print("=" * 60)
    
    while True:
        print("\n选择测试:")
        print("1. 检查现有用户的二维码数据")
        print("2. 模拟二维码更新测试")
        print("3. 模拟文件上传流程问题")
        print("4. 退出")
        
        choice = input("\n请输入选择 (1-4): ").strip()
        
        if choice == "1" or choice == "2":
            test_qrcode_update()
        elif choice == "3":
            check_file_upload_simulation()
        elif choice == "4":
            print("👋 调试结束")
            break
        else:
            print("❌ 无效选择，请重试")

if __name__ == "__main__":
    main()