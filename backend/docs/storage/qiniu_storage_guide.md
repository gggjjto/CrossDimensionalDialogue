# 七牛云存储使用指南

## 概述

本项目集成了七牛云对象存储服务，用于存储和管理各种类型的文件，包括音频、图片、文档等。七牛云存储提供了高可用性、高并发访问和CDN加速等特性。

## 功能特性

- ✅ 文件上传（支持本地文件和字节数据）
- ✅ 文件下载和访问URL生成
- ✅ 文件删除（单个和批量）
- ✅ 文件复制和移动
- ✅ CDN缓存刷新
- ✅ 图片处理（缩略图生成）
- ✅ 文件信息查询
- ✅ 存储统计
- ✅ 私有文件访问控制

## 配置说明

### 环境变量配置

在 `.env` 文件中添加以下配置：

```bash
# 七牛云存储配置
QINIU_ACCESS_KEY=your_access_key
QINIU_SECRET_KEY=your_secret_key
QINIU_BUCKET_NAME=your_bucket_name
QINIU_DOMAIN=your_domain.com
QINIU_USE_HTTPS=true
QINIU_CDN_DOMAIN=your_cdn_domain.com  # 可选，用于CDN加速
```

### 配置参数说明

| 参数 | 说明 | 必填 | 默认值 |
|------|------|------|--------|
| `QINIU_ACCESS_KEY` | 七牛云访问密钥 | 是 | - |
| `QINIU_SECRET_KEY` | 七牛云秘密密钥 | 是 | - |
| `QINIU_BUCKET_NAME` | 存储空间名称 | 是 | - |
| `QINIU_DOMAIN` | 存储空间绑定的域名 | 是 | - |
| `QINIU_USE_HTTPS` | 是否使用HTTPS | 否 | true |
| `QINIU_CDN_DOMAIN` | CDN加速域名 | 否 | 使用QINIU_DOMAIN |

## 基础使用

### 1. 导入模块

```python
from app.services.qiniu_storage_service import qiniu_storage_service
from app.utils.qiniu_storage import qiniu_client
```

### 2. 上传文件

#### 上传音频文件

```python
# 上传用户音频文件
result = qiniu_storage_service.upload_audio_file(
    file_path="path/to/audio.mp3",
    user_id=123,
    conversation_id=456,
    file_type="audio"
)

print(f"上传成功: {result['url']}")
print(f"文件大小: {result['file_size']} bytes")
```

#### 上传图片文件

```python
# 上传用户图片
result = qiniu_storage_service.upload_image_file(
    file_path="path/to/image.jpg",
    user_id=123,
    category="avatar",
    file_type="image"
)

print(f"图片URL: {result['url']}")
```

#### 上传角色头像

```python
# 上传角色头像
result = qiniu_storage_service.upload_character_avatar(
    file_path="path/to/character_avatar.png",
    character_id=789,
    file_type="avatar"
)

print(f"角色头像URL: {result['url']}")
```

#### 上传文档

```python
# 上传文档文件
result = qiniu_storage_service.upload_document(
    file_path="path/to/document.pdf",
    user_id=123,
    document_type="manual",
    file_type="document"
)

print(f"文档URL: {result['url']}")
```

### 3. 获取文件访问URL

```python
# 获取公开访问URL
public_url = qiniu_storage_service.get_file_url("20241201/abc123_image.jpg")

# 获取私有访问URL（带签名，1小时后过期）
private_url = qiniu_storage_service.get_file_url(
    "20241201/abc123_image.jpg", 
    private=True, 
    expires=3600
)
```

### 4. 图片处理

```python
# 获取图片缩略图URL
thumbnail_url = qiniu_storage_service.get_image_thumbnail_url(
    key="20241201/abc123_image.jpg",
    width=200,
    height=200,
    quality=80,
    format="jpg"
)

# 获取图片信息
image_info = qiniu_storage_service.get_image_info("20241201/abc123_image.jpg")
if image_info:
    print(f"图片大小: {image_info['size']} bytes")
    print(f"图片类型: {image_info['mime_type']}")
```

### 5. 文件管理

```python
# 删除单个文件
success = qiniu_client.delete_file("20241201/abc123_image.jpg")

# 批量删除文件
result = qiniu_client.delete_files([
    "20241201/abc123_image1.jpg",
    "20241201/abc123_image2.jpg"
])

# 删除用户所有文件
result = qiniu_storage_service.delete_user_files(
    user_id=123, 
    file_type="image"  # 可选，指定文件类型
)
```

### 6. 存储统计

```python
# 获取用户存储统计
stats = qiniu_storage_service.get_storage_stats(user_id=123)
print(f"用户文件总数: {stats['total_files']}")
print(f"存储大小: {stats['total_size_mb']} MB")

# 获取全局存储统计
global_stats = qiniu_storage_service.get_storage_stats()
print(f"总文件数: {global_stats['total_files']}")
```

## 高级功能

### 1. 直接使用客户端

```python
from app.utils.qiniu_storage import qiniu_client

# 上传字节数据
data = b"Hello, World!"
result = qiniu_client.upload_data(
    data=data,
    key="test/hello.txt",
    content_type="text/plain"
)

# 复制文件
success = qiniu_client.copy_file(
    src_key="source/file.jpg",
    dest_key="destination/file.jpg"
)

# 移动文件
success = qiniu_client.move_file(
    src_key="old/location/file.jpg",
    dest_key="new/location/file.jpg"
)
```

### 2. CDN缓存刷新

```python
# 刷新CDN缓存
urls = [
    "https://your-domain.com/image1.jpg",
    "https://your-domain.com/image2.jpg"
]
result = qiniu_client.refresh_cdn(urls)
print(f"刷新结果: {result['success']}")
```

### 3. 获取上传Token

```python
# 获取上传token（用于前端直传）
token = qiniu_client.get_upload_token(
    key="user/upload/file.jpg",
    expires=3600
)

# 获取无限制上传token
token = qiniu_client.get_upload_token(expires=3600)
```

## 文件组织结构

项目采用以下文件组织结构：

```
存储空间/
├── audio/                    # 音频文件
│   └── {user_id}/
│       ├── conversation/     # 对话相关音频
│       │   └── {conversation_id}/
│       └── {timestamp}/      # 按日期分组
├── images/                   # 图片文件
│   └── {user_id}/
│       ├── avatar/           # 用户头像
│       ├── general/          # 普通图片
│       └── {timestamp}/      # 按日期分组
├── characters/               # 角色相关文件
│   └── {character_id}/
│       └── avatar/           # 角色头像
└── documents/                # 文档文件
    └── {user_id}/
        ├── manual/           # 手册文档
        ├── general/          # 普通文档
        └── {timestamp}/      # 按日期分组
```

## 错误处理

```python
from app.utils.qiniu_storage import QiniuStorageError

try:
    result = qiniu_storage_service.upload_audio_file(
        file_path="invalid_file.txt",
        user_id=123
    )
except QiniuStorageError as e:
    print(f"上传失败: {e}")
except FileNotFoundError:
    print("文件不存在")
```

## 最佳实践

### 1. 文件命名规范

- 使用有意义的文件名前缀
- 避免使用特殊字符
- 建议使用时间戳避免重名

### 2. 文件大小限制

- 音频文件：最大50MB
- 图片文件：建议不超过10MB
- 文档文件：建议不超过100MB

### 3. 安全考虑

- 敏感文件使用私有URL
- 定期清理过期文件
- 监控存储使用量

### 4. 性能优化

- 使用CDN加速域名
- 合理设置缓存策略
- 批量操作时使用批量API

## 常见问题

### Q: 如何获取七牛云配置信息？

A: 登录七牛云控制台，在"个人中心" -> "密钥管理"中获取AccessKey和SecretKey，在"对象存储"中创建存储空间并绑定域名。

### Q: 上传失败怎么办？

A: 检查以下几点：
1. 配置信息是否正确
2. 文件是否存在
3. 文件大小是否超限
4. 网络连接是否正常

### Q: 如何实现文件预览？

A: 对于图片文件，可以直接使用公开URL；对于其他文件，可以使用七牛云的文件预览服务或第三方预览服务。

### Q: 如何备份重要文件？

A: 可以定期将重要文件同步到其他存储服务，或使用七牛云的数据迁移功能。

## 相关链接

- [七牛云官方文档](https://developer.qiniu.com/kodo/1242/python)
- [七牛云Python SDK](https://github.com/qiniu/python-sdk)
- [七牛云控制台](https://portal.qiniu.com/)
