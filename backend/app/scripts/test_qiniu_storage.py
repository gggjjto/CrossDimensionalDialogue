#!/usr/bin/env python3
"""
七牛云存储测试脚本

用于测试七牛云存储功能是否正常工作
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings
from app.services.qiniu_storage_service import qiniu_storage_service
from app.utils.qiniu_storage import qiniu_client, QiniuStorageError


def test_configuration():
    """测试配置是否正确"""
    print("🔧 检查七牛云配置...")

    required_configs = [
        "QINIU_ACCESS_KEY",
        "QINIU_SECRET_KEY",
        "QINIU_BUCKET_NAME",
        "QINIU_DOMAIN",
    ]

    missing_configs = []
    for config in required_configs:
        if not getattr(settings, config, None):
            missing_configs.append(config)

    if missing_configs:
        print(f"❌ 缺少配置: {', '.join(missing_configs)}")
        print("请在 .env 文件中添加七牛云配置")
        return False

    print("✅ 配置检查通过")
    return True


def test_client_initialization():
    """测试客户端初始化"""
    print("\n🚀 测试客户端初始化...")

    try:
        # 测试基础客户端
        client = qiniu_client
        print("✅ 基础客户端初始化成功")

        # 测试服务客户端
        service = qiniu_storage_service
        print("✅ 存储服务初始化成功")

        return True
    except QiniuStorageError as e:
        print(f"❌ 客户端初始化失败: {e}")
        return False


def test_bucket_access():
    """测试存储空间访问"""
    print("\n📦 测试存储空间访问...")

    try:
        # 尝试列出文件（限制1个）
        result = qiniu_client.list_files(limit=1)
        print("✅ 存储空间访问成功")
        print(f"   存储空间: {settings.QINIU_BUCKET_NAME}")
        print(f"   域名: {settings.QINIU_DOMAIN}")
        return True
    except Exception as e:
        print(f"❌ 存储空间访问失败: {e}")
        return False


def test_file_operations():
    """测试文件操作"""
    print("\n📁 测试文件操作...")

    # 创建测试文件
    test_file = Path("test_qiniu.txt")
    test_content = "Hello, 七牛云存储测试!"

    try:
        # 写入测试文件
        test_file.write_text(test_content, encoding="utf-8")
        print(f"✅ 创建测试文件: {test_file}")

        # 测试上传
        print("   上传文件...")
        result = qiniu_client.upload_file(
            file_path=test_file, key="test/upload_test.txt", overwrite=True
        )
        print(f"✅ 文件上传成功: {result['url']}")

        # 测试获取文件信息
        print("   获取文件信息...")
        file_info = qiniu_client.get_file_info("test/upload_test.txt")
        if file_info:
            print(f"✅ 文件信息获取成功: {file_info['fsize']} bytes")
        else:
            print("❌ 文件信息获取失败")
            return False

        # 测试删除文件
        print("   删除文件...")
        success = qiniu_client.delete_file("test/upload_test.txt")
        if success:
            print("✅ 文件删除成功")
        else:
            print("❌ 文件删除失败")
            return False

        return True

    except Exception as e:
        print(f"❌ 文件操作失败: {e}")
        return False
    finally:
        # 清理测试文件
        if test_file.exists():
            test_file.unlink()
            print(f"🧹 清理测试文件: {test_file}")


def test_service_operations():
    """测试服务操作"""
    print("\n🔧 测试存储服务...")

    # 创建测试图片文件（模拟）
    test_image = Path("test_image.jpg")
    test_content = b"fake image content for testing"

    try:
        # 写入测试文件
        test_image.write_bytes(test_content)
        print(f"✅ 创建测试图片: {test_image}")

        # 测试上传图片
        print("   上传测试图片...")
        result = qiniu_storage_service.upload_image_file(
            file_path=test_image,
            user_id=999,  # 测试用户ID
            category="test",
            file_type="image",
        )
        print(f"✅ 图片上传成功: {result['url']}")

        # 测试获取缩略图URL
        print("   生成缩略图URL...")
        thumbnail_url = qiniu_storage_service.get_image_thumbnail_url(
            key=result["key"], width=100, height=100
        )
        print(f"✅ 缩略图URL: {thumbnail_url}")

        # 测试删除文件
        print("   删除测试图片...")
        success = qiniu_client.delete_file(result["key"])
        if success:
            print("✅ 测试图片删除成功")
        else:
            print("❌ 测试图片删除失败")
            return False

        return True

    except Exception as e:
        print(f"❌ 服务操作失败: {e}")
        return False
    finally:
        # 清理测试文件
        if test_image.exists():
            test_image.unlink()
            print(f"🧹 清理测试图片: {test_image}")


def test_storage_stats():
    """测试存储统计"""
    print("\n📊 测试存储统计...")

    try:
        # 获取全局统计
        stats = qiniu_storage_service.get_storage_stats()
        print(f"✅ 全局存储统计:")
        print(f"   总文件数: {stats['total_files']}")
        print(f"   总大小: {stats['total_size_mb']} MB")

        # 获取用户统计
        user_stats = qiniu_storage_service.get_storage_stats(user_id=999)
        print(f"✅ 用户存储统计:")
        print(f"   用户文件数: {user_stats['total_files']}")
        print(f"   用户大小: {user_stats['total_size_mb']} MB")

        return True

    except Exception as e:
        print(f"❌ 存储统计失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🧪 七牛云存储功能测试")
    print("=" * 50)

    tests = [
        ("配置检查", test_configuration),
        ("客户端初始化", test_client_initialization),
        ("存储空间访问", test_bucket_access),
        ("文件操作", test_file_operations),
        ("服务操作", test_service_operations),
        ("存储统计", test_storage_stats),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ {test_name} 异常: {e}")

    print("\n" + "=" * 50)
    print(f"📋 测试结果: {passed}/{total} 通过")

    if passed == total:
        print("🎉 所有测试通过！七牛云存储功能正常")
        return 0
    else:
        print("⚠️  部分测试失败，请检查配置和网络连接")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
