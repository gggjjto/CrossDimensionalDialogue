# 图片生成 API 文档

图片生成模块提供AI图片生成功能，支持多种风格和尺寸的图片生成。

## 基础信息

- **基础路径**: `/image`
- **认证**: 需要用户登录
- **内容类型**: `application/json`

## 接口列表

### 1. 生成图片

使用AI生成指定风格的图片。

**接口**: `POST /image/generate`

**请求参数**:
- `prompt` (查询参数, 必需): 图片生成提示词
- `size` (查询参数, 可选): 图片尺寸，默认 "720*1280"
- `style` (查询参数, 可选): 图片风格，默认 "realistic"
- `quality` (查询参数, 可选): 图片质量，默认 "standard"

**请求示例**:
```
POST /image/generate?prompt=a beautiful sunset over mountains&size=720*1280&style=realistic&quality=standard
```

**参数说明**:
- `prompt` (string): 描述要生成的图片内容
- `size` (string): 图片尺寸，支持格式如 "720*1280", "1024*1024" 等
- `style` (string): 图片风格，可选值：
  - `realistic`: 写实风格
  - `anime`: 动漫风格
  - `cartoon`: 卡通风格
  - `artistic`: 艺术风格
- `quality` (string): 图片质量，可选值：
  - `standard`: 标准质量
  - `high`: 高质量
  - `ultra`: 超高质量

**响应**:
```json
{
  "success": true,
  "data": {
    "url": "https://example.com/generated-image.jpg",
    "filename": "generated_image_123.jpg",
    "size": "720*1280",
    "style": "realistic",
    "quality": "standard"
  },
  "message": "图片生成成功"
}
```

**响应字段说明**:
- `success` (bool): 请求是否成功
- `data` (object): 生成结果数据
  - `url` (string): 图片的公网访问URL
  - `filename` (string): 生成的文件名
  - `size` (string): 图片尺寸
  - `style` (string): 使用的风格
  - `quality` (string): 使用的质量设置
- `message` (string): 响应消息

**状态码**:
- `200`: 生成成功
- `400`: 请求参数错误
- `401`: 未认证
- `500`: 生成失败

## 错误处理

所有接口都遵循统一的错误响应格式：

```json
{
  "success": false,
  "error": "错误描述信息"
}
```

常见错误类型：
- `400 Bad Request`: 请求参数错误，如提示词为空
- `401 Unauthorized`: 未认证或认证失败
- `500 Internal Server Error`: 图片生成失败

## 使用示例

### 基础图片生成

```bash
curl -X POST "https://api.example.com/image/generate?prompt=a cute cat sitting on a windowsill&size=720*1280&style=realistic" \
  -H "Authorization: Bearer your_token"
```

### 动漫风格图片生成

```bash
curl -X POST "https://api.example.com/image/generate?prompt=a magical forest with glowing trees&size=1024*1024&style=anime&quality=high" \
  -H "Authorization: Bearer your_token"
```

### 艺术风格图片生成

```bash
curl -X POST "https://api.example.com/image/generate?prompt=abstract painting with vibrant colors&size=720*1280&style=artistic&quality=ultra" \
  -H "Authorization: Bearer your_token"
```

## 支持的参数值

### 图片尺寸 (size)
- `720*1280`: 竖屏手机尺寸
- `1024*1024`: 正方形
- `1280*720`: 横屏尺寸
- `512*512`: 小尺寸正方形
- `2048*2048`: 大尺寸正方形

### 图片风格 (style)
- `realistic`: 写实风格，适合真实场景
- `anime`: 动漫风格，适合二次元内容
- `cartoon`: 卡通风格，适合儿童内容
- `artistic`: 艺术风格，适合创意表达

### 图片质量 (quality)
- `standard`: 标准质量，生成速度快
- `high`: 高质量，平衡速度和质量
- `ultra`: 超高质量，生成时间较长

## 注意事项

1. 所有接口都需要用户认证，请在请求头中包含有效的访问令牌
2. 提示词建议使用英文，效果更好
3. 提示词长度建议控制在200字符以内
4. 生成的图片会自动上传到云存储，返回公网可访问的URL
5. 不同质量和尺寸会影响生成时间和成本
6. 生成的图片会保存在用户的个人存储空间中
7. 建议在生成前预览提示词，确保描述准确清晰

## 最佳实践

### 提示词编写建议

1. **具体描述**: 使用具体的形容词和细节描述
   - 好的例子: "a majestic golden retriever sitting on a wooden porch with autumn leaves"
   - 不好的例子: "a dog"

2. **风格指定**: 在提示词中明确指定风格
   - 好的例子: "in the style of Van Gogh, a starry night over a village"
   - 不好的例子: "a night scene"

3. **避免冲突**: 避免在提示词中包含矛盾的描述
   - 避免: "a black and white colorful painting"

4. **使用关键词**: 使用专业术语提高效果
   - 好的例子: "photorealistic, high resolution, detailed"
   - 不好的例子: "nice picture"

### 性能优化建议

1. 选择合适的尺寸，避免不必要的超大尺寸
2. 根据需求选择质量等级，标准质量通常足够
3. 批量生成时注意API调用频率限制
4. 缓存常用的生成结果，避免重复生成
