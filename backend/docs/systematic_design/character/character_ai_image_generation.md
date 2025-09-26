# 角色AI形象图片生成功能文档

## 概述

角色AI形象图片生成功能允许用户为角色自动生成AI形象图片，支持多种风格和尺寸选择。当用户创建角色时，可以选择是否启用AI图片生成，如果没有提供头像URL，系统将自动使用AI模型生成一张符合角色特征的图片。

## 功能特性

### 1. 自动图片生成 ✅
- 创建角色时可选择启用AI图片生成
- 自动分析角色特征生成合适的形象图片
- 支持多种图片风格和尺寸

### 2. 手动图片生成 ✅
- 为现有角色生成新的AI形象图片
- 支持自定义风格和尺寸参数
- 可替换现有头像

### 3. 图片验证 ✅
- 验证角色头像图片的有效性
- 检查图片URL是否可访问
- 确保图片格式正确

## 支持的风格

| 风格 | 英文标识 | 描述 | 适用场景 |
|------|----------|------|----------|
| 写实风格 | realistic | 真实人物照片风格 | 历史人物、现代角色 |
| 动漫风格 | anime | 日式动漫风格 | 二次元角色、动漫人物 |
| 卡通风格 | cartoon | 卡通动画风格 | 儿童角色、可爱角色 |
| 艺术风格 | artistic | 艺术绘画风格 | 文艺角色、创意角色 |

## 支持的尺寸

| 尺寸 | 描述 | 适用场景 |
|------|------|----------|
| 1024x1024 | 正方形 | 头像、社交媒体 |
| 1792x1024 | 横向矩形 | 横幅、封面 |
| 1024x1792 | 纵向矩形 | 海报、宣传图 |

## API接口

### 1. 生成角色AI形象图片

**接口**: `POST /api/v1/characters/{character_id}/generate-image`

**权限**: 需要超级用户权限

**查询参数**:
- `style`: 图片风格 (realistic, anime, cartoon, artistic)
- `size`: 图片尺寸 (1024x1024, 1792x1024, 1024x1792)

**响应示例**:
```json
{
  "code": 0,
  "msg": "AI形象图片生成成功",
  "data": {
    "character_id": "uuid-string",
    "avatar_url": "https://example.com/generated-image.jpg",
    "style": "realistic",
    "size": "1024x1024"
  }
}
```

### 2. 获取支持的图片风格

**接口**: `GET /api/v1/characters/image-generation/styles`

**权限**: 公开访问

**响应示例**:
```json
{
  "code": 0,
  "msg": "获取图片风格成功",
  "data": {
    "realistic": "写实风格",
    "anime": "动漫风格",
    "cartoon": "卡通风格",
    "artistic": "艺术风格"
  }
}
```

### 3. 获取支持的图片尺寸

**接口**: `GET /api/v1/characters/image-generation/sizes`

**权限**: 公开访问

**响应示例**:
```json
{
  "code": 0,
  "msg": "获取图片尺寸成功",
  "data": {
    "1024x1024": "正方形 (1024x1024)",
    "1792x1024": "横向 (1792x1024)",
    "1024x1792": "纵向 (1024x1792)"
  }
}
```

### 4. 验证角色头像图片

**接口**: `POST /api/v1/characters/{character_id}/validate-image`

**权限**: 需要超级用户权限

**响应示例**:
```json
{
  "code": 0,
  "msg": "图片验证完成",
  "data": {
    "character_id": "uuid-string",
    "avatar_url": "https://example.com/image.jpg",
    "is_valid": true
  }
}
```

## 数据库设计

### 角色表新增字段

```sql
-- 添加AI图片生成相关字段
ALTER TABLE characters ADD COLUMN auto_generate_image BOOLEAN DEFAULT false;
ALTER TABLE characters ADD COLUMN image_style VARCHAR(20) DEFAULT 'realistic';
ALTER TABLE characters ADD COLUMN image_size VARCHAR(20) DEFAULT '1024x1024';
```

### 字段说明

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| auto_generate_image | BOOLEAN | false | 是否自动生成AI形象图片 |
| image_style | VARCHAR(20) | realistic | AI生成图片风格 |
| image_size | VARCHAR(20) | 1024x1024 | AI生成图片尺寸 |

## 配置说明

### 环境变量

```bash
# OpenAI配置（用于DALL-E图片生成）
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1

# AI图片生成配置
ENABLE_AI_IMAGE_GENERATION=true
AI_IMAGE_DEFAULT_STYLE=realistic
AI_IMAGE_DEFAULT_SIZE=1024x1024
AI_IMAGE_MAX_RETRIES=3
AI_IMAGE_TIMEOUT=60
```

### 依赖包

```toml
# pyproject.toml
dependencies = [
    "pillow>=10.0.0",  # 图片处理
    "httpx>=0.25.1",   # HTTP客户端
    "openai>=1.108.1", # OpenAI API
]
```

## 使用示例

### 1. 创建角色时自动生成AI图片

```bash
curl -X POST "http://localhost:8000/api/v1/characters/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "苏格拉底",
    "short_bio": "古希腊哲学家，以问答法著称",
    "persona_text": "我是苏格拉底，古希腊的哲学家...",
    "example_lines": ["我知道我什么都不知道"],
    "source": "古希腊哲学",
    "auto_generate_image": true,
    "image_style": "realistic",
    "image_size": "1024x1024"
  }'
```

### 2. 为现有角色生成AI图片

```bash
curl -X POST "http://localhost:8000/api/v1/characters/{character_id}/generate-image" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d "style=anime&size=1024x1024"
```

### 3. 验证角色头像图片

```bash
curl -X POST "http://localhost:8000/api/v1/characters/{character_id}/validate-image" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. 获取支持的风格和尺寸

```bash
# 获取支持的风格
curl "http://localhost:8000/api/v1/characters/image-generation/styles"

# 获取支持的尺寸
curl "http://localhost:8000/api/v1/characters/image-generation/sizes"
```

## 技术实现

### 1. 提示词构建

系统会根据角色的以下信息构建AI图片生成提示词：
- 角色名称
- 角色简介
- 人格文本中的关键词（年龄、性别、职业、外观特征等）

### 2. 关键词提取

从人格文本中自动提取以下类型的关键词：
- **年龄相关**: young, old, middle-aged, teenager, child, elderly
- **性别相关**: male, female, man, woman, boy, girl
- **职业相关**: teacher, doctor, scientist, artist, writer, philosopher
- **外观特征**: tall, short, thin, fat, muscular, beautiful, handsome
- **服装风格**: formal, casual, traditional, modern, elegant

### 3. API调用

使用OpenAI DALL-E 3 API生成图片：
- 模型: dall-e-3
- 质量: standard
- 风格: vivid
- 超时: 60秒

### 4. 错误处理

- API调用失败时记录错误日志
- 图片生成失败不影响角色创建
- 提供详细的错误信息

## 性能优化

### 1. 异步处理
- 使用异步HTTP客户端
- 非阻塞的图片生成过程

### 2. 缓存策略
- 可考虑缓存生成的图片URL
- 避免重复生成相同特征的图片

### 3. 超时控制
- 设置合理的API调用超时时间
- 避免长时间等待

## 故障排除

### 常见问题

1. **AI图片生成失败**
   - 检查OpenAI API密钥配置
   - 确认API配额充足
   - 查看错误日志

2. **图片风格不符合预期**
   - 调整角色描述信息
   - 尝试不同的风格参数
   - 优化提示词构建逻辑

3. **图片尺寸问题**
   - 确认支持的尺寸格式
   - 检查尺寸参数是否正确

### 日志查看

```bash
# 查看应用日志
tail -f logs/app.log | grep "character_image"

# 查看错误日志
tail -f logs/app.log | grep "ERROR.*character_image"
```

## 扩展计划

### 短期计划
1. **更多AI模型支持**: 集成其他图片生成模型
2. **批量生成**: 支持批量生成多个角色的图片
3. **图片编辑**: 支持对生成的图片进行简单编辑

### 中期计划
1. **自定义风格**: 允许用户上传参考图片定义风格
2. **图片优化**: 自动优化生成的图片质量
3. **多语言支持**: 支持中文提示词生成

### 长期计划
1. **3D形象生成**: 支持生成3D角色形象
2. **动画生成**: 生成角色动画效果
3. **个性化推荐**: 基于用户偏好推荐图片风格

## 总结

AI形象图片生成功能为角色管理系统增加了强大的视觉化能力，通过智能分析角色特征自动生成合适的形象图片，大大提升了用户体验和系统的智能化水平。该功能设计灵活，支持多种风格和尺寸，具有良好的扩展性和可维护性。
