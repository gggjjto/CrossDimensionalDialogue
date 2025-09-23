# 图片和文件消息支持设计

## 概述

本文档设计图片和文件消息的完整支持方案，包括数据模型、API接口、存储管理、处理流程等。

## 功能需求

### 1. 图片消息支持
- ✅ 图片上传和存储
- ✅ 图片压缩和优化
- ✅ 图片格式转换
- ✅ 图片预览和显示
- ✅ 图片元数据管理
- ✅ 图片安全检测

### 2. 文件消息支持
- ✅ 文件上传和存储
- ✅ 文件类型验证
- ✅ 文件大小限制
- ✅ 文件下载和预览
- ✅ 文件元数据管理
- ✅ 文件安全扫描

## 数据模型设计

### 1. 图片消息表 (image_messages)

```sql
CREATE TABLE image_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    file_url VARCHAR(500) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size INTEGER NOT NULL CHECK (file_size > 0),
    mime_type VARCHAR(100) NOT NULL,
    width INTEGER CHECK (width > 0),
    height INTEGER CHECK (height > 0),
    format VARCHAR(20) NOT NULL CHECK (format IN ('jpeg', 'png', 'gif', 'webp', 'bmp')),
    quality_score FLOAT CHECK (quality_score >= 0 AND quality_score <= 1),
    thumbnail_url VARCHAR(500),
    compressed_url VARCHAR(500),
    metadata JSONB,
    processing_status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- 索引
CREATE INDEX idx_image_messages_message_id ON image_messages(message_id);
CREATE INDEX idx_image_messages_format ON image_messages(format);
CREATE INDEX idx_image_messages_status ON image_messages(processing_status);
CREATE INDEX idx_image_messages_created_at ON image_messages(created_at DESC);
```

### 2. 文件消息表 (file_messages)

```sql
CREATE TABLE file_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    file_url VARCHAR(500) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size INTEGER NOT NULL CHECK (file_size > 0),
    mime_type VARCHAR(100) NOT NULL,
    file_extension VARCHAR(20) NOT NULL,
    file_type VARCHAR(50) NOT NULL CHECK (file_type IN ('document', 'image', 'video', 'audio', 'archive', 'other')),
    checksum VARCHAR(64),
    metadata JSONB,
    preview_url VARCHAR(500),
    download_count INTEGER DEFAULT 0,
    processing_status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed')),
    security_scan_status VARCHAR(20) DEFAULT 'pending' CHECK (security_scan_status IN ('pending', 'scanning', 'safe', 'unsafe', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- 索引
CREATE INDEX idx_file_messages_message_id ON file_messages(message_id);
CREATE INDEX idx_file_messages_type ON file_messages(file_type);
CREATE INDEX idx_file_messages_status ON file_messages(processing_status);
CREATE INDEX idx_file_messages_security ON file_messages(security_scan_status);
CREATE INDEX idx_file_messages_created_at ON file_messages(created_at DESC);
```

### 3. 文件处理任务表 (file_processing_tasks)

```sql
CREATE TABLE file_processing_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_message_id UUID REFERENCES file_messages(id) ON DELETE CASCADE,
    image_message_id UUID REFERENCES image_messages(id) ON DELETE CASCADE,
    task_type VARCHAR(50) NOT NULL CHECK (task_type IN ('image_compress', 'image_resize', 'image_format_convert', 'file_scan', 'thumbnail_generate')),
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    error_message TEXT,
    result_data JSONB,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- 索引
CREATE INDEX idx_file_tasks_file_message_id ON file_processing_tasks(file_message_id);
CREATE INDEX idx_file_tasks_image_message_id ON file_processing_tasks(image_message_id);
CREATE INDEX idx_file_tasks_type ON file_processing_tasks(task_type);
CREATE INDEX idx_file_tasks_status ON file_processing_tasks(status);
```

## API接口设计

### 1. 图片消息API

#### 1.1 上传图片
```
POST /api/v1/images/upload
```

**请求体**: multipart/form-data
- `file`: 图片文件
- `conversation_id`: 会话ID（可选）
- `compress`: 是否压缩（默认true）
- `max_width`: 最大宽度（默认1920）
- `max_height`: 最大高度（默认1080）
- `quality`: 压缩质量（默认85）

**响应**:
```json
{
  "code": 0,
  "msg": "图片上传成功",
  "data": {
    "id": "image-uuid",
    "file_url": "https://storage.example.com/images/uuid.jpg",
    "file_name": "image.jpg",
    "file_size": 1024000,
    "width": 1920,
    "height": 1080,
    "format": "jpeg",
    "thumbnail_url": "https://storage.example.com/thumbnails/uuid.jpg",
    "compressed_url": "https://storage.example.com/compressed/uuid.jpg",
    "processing_status": "completed"
  }
}
```

#### 1.2 获取图片详情
```
GET /api/v1/images/{image_id}
```

#### 1.3 获取图片列表
```
GET /api/v1/images/
```

**查询参数**:
- `conversation_id`: 会话ID过滤
- `format`: 图片格式过滤
- `status`: 处理状态过滤
- `skip`: 跳过的记录数
- `limit`: 返回的记录数

#### 1.4 删除图片
```
DELETE /api/v1/images/{image_id}
```

#### 1.5 图片处理
```
POST /api/v1/images/{image_id}/process
```

**请求体**:
```json
{
  "operations": [
    {
      "type": "resize",
      "width": 800,
      "height": 600
    },
    {
      "type": "compress",
      "quality": 80
    },
    {
      "type": "format_convert",
      "format": "webp"
    }
  ]
}
```

### 2. 文件消息API

#### 2.1 上传文件
```
POST /api/v1/files/upload
```

**请求体**: multipart/form-data
- `file`: 文件
- `conversation_id`: 会话ID（可选）
- `scan_security`: 是否安全扫描（默认true）

**响应**:
```json
{
  "code": 0,
  "msg": "文件上传成功",
  "data": {
    "id": "file-uuid",
    "file_url": "https://storage.example.com/files/uuid.pdf",
    "file_name": "document.pdf",
    "file_size": 2048000,
    "mime_type": "application/pdf",
    "file_type": "document",
    "checksum": "sha256:abc123...",
    "preview_url": "https://storage.example.com/previews/uuid.jpg",
    "processing_status": "completed",
    "security_scan_status": "safe"
  }
}
```

#### 2.2 获取文件详情
```
GET /api/v1/files/{file_id}
```

#### 2.3 获取文件列表
```
GET /api/v1/files/
```

#### 2.4 下载文件
```
GET /api/v1/files/{file_id}/download
```

#### 2.5 删除文件
```
DELETE /api/v1/files/{file_id}
```

#### 2.6 文件预览
```
GET /api/v1/files/{file_id}/preview
```

### 3. 消息集成API

#### 3.1 发送图片消息
```
POST /api/v1/conversations/{conversation_id}/messages
```

**请求体**:
```json
{
  "content": "这是一张图片",
  "content_type": "image",
  "image_data": {
    "image_id": "image-uuid",
    "caption": "图片说明"
  }
}
```

#### 3.2 发送文件消息
```
POST /api/v1/conversations/{conversation_id}/messages
```

**请求体**:
```json
{
  "content": "这是一个文件",
  "content_type": "file",
  "file_data": {
    "file_id": "file-uuid",
    "description": "文件说明"
  }
}
```

## 服务层设计

### 1. 图片处理服务 (ImageProcessingService)

```python
class ImageProcessingService:
    """图片处理服务"""
    
    async def upload_image(
        self,
        file: UploadFile,
        user_id: uuid.UUID,
        conversation_id: Optional[uuid.UUID] = None,
        compress: bool = True,
        max_width: int = 1920,
        max_height: int = 1080,
        quality: int = 85
    ) -> ImageMessage:
        """上传并处理图片"""
        
    async def compress_image(
        self,
        image_data: bytes,
        max_width: int,
        max_height: int,
        quality: int
    ) -> bytes:
        """压缩图片"""
        
    async def generate_thumbnail(
        self,
        image_data: bytes,
        width: int = 300,
        height: int = 300
    ) -> bytes:
        """生成缩略图"""
        
    async def convert_format(
        self,
        image_data: bytes,
        target_format: str
    ) -> bytes:
        """转换图片格式"""
        
    async def analyze_image(
        self,
        image_data: bytes
    ) -> Dict[str, Any]:
        """分析图片元数据"""
```

### 2. 文件处理服务 (FileProcessingService)

```python
class FileProcessingService:
    """文件处理服务"""
    
    async def upload_file(
        self,
        file: UploadFile,
        user_id: uuid.UUID,
        conversation_id: Optional[uuid.UUID] = None,
        scan_security: bool = True
    ) -> FileMessage:
        """上传文件"""
        
    async def scan_file_security(
        self,
        file_data: bytes,
        file_name: str
    ) -> Dict[str, Any]:
        """文件安全扫描"""
        
    async def generate_preview(
        self,
        file_data: bytes,
        file_type: str
    ) -> Optional[str]:
        """生成文件预览"""
        
    async def calculate_checksum(
        self,
        file_data: bytes
    ) -> str:
        """计算文件校验和"""
```

### 3. 存储服务 (StorageService)

```python
class StorageService:
    """存储服务"""
    
    async def upload_file(
        self,
        file_data: bytes,
        file_name: str,
        folder: str = "uploads"
    ) -> str:
        """上传文件到存储"""
        
    async def delete_file(
        self,
        file_url: str
    ) -> bool:
        """删除文件"""
        
    async def get_file_url(
        self,
        file_path: str,
        expires_in: int = 3600
    ) -> str:
        """获取文件访问URL"""
```

## 配置管理

### 1. 图片配置

```python
IMAGE_CONFIG = {
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "allowed_formats": ["jpeg", "png", "gif", "webp", "bmp"],
    "max_dimensions": {
        "width": 4096,
        "height": 4096
    },
    "thumbnail_size": {
        "width": 300,
        "height": 300
    },
    "compression": {
        "default_quality": 85,
        "max_width": 1920,
        "max_height": 1080
    },
    "storage": {
        "folder": "images",
        "cdn_url": "https://cdn.example.com"
    }
}
```

### 2. 文件配置

```python
FILE_CONFIG = {
    "max_file_size": 100 * 1024 * 1024,  # 100MB
    "allowed_types": [
        "document", "image", "video", "audio", "archive"
    ],
    "allowed_extensions": [
        ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
        ".txt", ".rtf", ".zip", ".rar", ".7z", ".tar", ".gz",
        ".mp4", ".avi", ".mov", ".wmv", ".flv", ".mp3", ".wav", ".flac"
    ],
    "security_scan": {
        "enabled": True,
        "max_scan_size": 50 * 1024 * 1024  # 50MB
    },
    "storage": {
        "folder": "files",
        "cdn_url": "https://cdn.example.com"
    }
}
```

## 安全考虑

### 1. 文件类型验证
- 白名单机制，只允许特定文件类型
- MIME类型检测，防止文件伪装
- 文件头检测，确保文件格式正确

### 2. 文件大小限制
- 单文件大小限制
- 用户总存储空间限制
- 会话文件数量限制

### 3. 安全扫描
- 病毒扫描
- 恶意代码检测
- 敏感内容检测

### 4. 访问控制
- 用户权限验证
- 会话访问控制
- 文件下载权限

## 性能优化

### 1. 图片优化
- 自动压缩和格式转换
- 缩略图生成
- CDN加速

### 2. 文件优化
- 分片上传
- 断点续传
- 压缩存储

### 3. 缓存策略
- 图片缓存
- 文件元数据缓存
- CDN缓存

## 实现优先级

### 第一阶段：基础功能（1-2周）
1. ✅ 图片上传和存储
2. ✅ 文件上传和存储
3. ✅ 基础API接口
4. ✅ 文件类型验证

### 第二阶段：处理功能（2-3周）
1. ✅ 图片压缩和优化
2. ✅ 缩略图生成
3. ✅ 文件安全扫描
4. ✅ 预览功能

### 第三阶段：高级功能（3-4周）
1. ✅ 图片格式转换
2. ✅ 文件预览生成
3. ✅ 批量处理
4. ✅ 性能优化

## 总结

这个设计提供了完整的图片和文件消息支持，包括：

1. **完整的数据模型** - 支持图片和文件的元数据管理
2. **丰富的API接口** - 覆盖上传、下载、处理、管理等功能
3. **强大的处理能力** - 图片压缩、格式转换、安全扫描等
4. **安全可靠** - 文件类型验证、安全扫描、访问控制
5. **性能优化** - 缓存策略、CDN加速、分片上传

通过这个设计，用户可以方便地发送图片和文件消息，系统会自动处理优化和安全检查，确保良好的用户体验和数据安全。
