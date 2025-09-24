# 语音处理API文档

## 概述

语音处理API提供了完整的语音功能，包括TTS（文本转语音）、STT（语音转文本）、音色管理和音频文件处理。

## API端点

### 1. 文本转语音 (TTS)

**POST** `/api/v1/voice/tts`

将文本转换为语音文件。

#### 请求参数

- `text` (必需): 要转换的文本内容（最大600字符）
- `voice` (可选): 音色名称，如 "Dylan", "Cherry" 等
- `audio_format` (可选): 音频格式，默认 "wav"
- `sample_rate` (可选): 采样率，默认 24000

#### 响应示例

```json
{
  "success": true,
  "message": "语音生成成功",
  "data": {
    "audio_data": "UklGRnoGAABXQVZFZm10IBAAAAABAAEA...",
    "content_type": "audio/wav",
    "voice": "Dylan",
    "duration_sec": 3.5,
    "model": "qwen3-tts-flash"
  }
}
```

#### 使用示例

```bash
curl -X POST "http://localhost:8000/api/v1/voice/tts" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "text": "你好，我是大黄鸭！",
    "voice": "Cherry",
    "audio_format": "wav"
  }'
```

### 2. 语音转文本 (STT)

**POST** `/api/v1/voice/stt`

将语音文件转换为文本。

#### 请求参数

- `audio_url` (必需): 音频文件的公网可访问URL
- `model` (可选): 识别模型，默认 "qwen3-asr-flash"
- `prompt` (可选): 提示文本
- `response_format` (可选): 响应格式，默认 "json"
- `temperature` (可选): 温度参数

#### 响应示例

```json
{
  "success": true,
  "message": "语音识别成功",
  "data": {
    "text": "你好，我是大黄鸭！",
    "language": "zh",
    "duration_sec": 3.5,
    "model": "qwen3-asr-flash",
    "words": []
  }
}
```

#### 使用示例

```bash
curl -X POST "http://localhost:8000/api/v1/voice/stt" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "audio_url": "https://example.com/audio/sample.wav",
    "model": "qwen3-asr-flash"
  }'
```

### 3. 获取可用音色列表

**GET** `/api/v1/voice/voices`

获取可用的音色列表。

#### 查询参数

- `provider` (可选): 音色提供方，默认 "qwen3-tts"

#### 响应示例

```json
{
  "success": true,
  "message": "获取音色列表成功",
  "data": {
    "voices": [
      {
        "voice": "Cherry",
        "name": "芊悦",
        "description": "阳光积极、亲切自然小姐姐。",
        "preview_url": null,
        "is_active": true
      },
      {
        "voice": "Dylan",
        "name": "北京-晓东",
        "description": "北京胡同里长大的少年。",
        "preview_url": null,
        "is_active": true
      }
    ],
    "provider": "qwen3-tts",
    "total": 17
  }
}
```

### 4. 上传音频文件

**POST** `/api/v1/voice/upload-audio`

上传音频文件到云存储。

#### 请求参数

- `file` (必需): 音频文件（支持 wav, mp3, m4a 等格式，最大10MB）

#### 响应示例

```json
{
  "success": true,
  "message": "音频文件上传成功",
  "data": {
    "audio_url": "https://example.com/audio/uploaded_file.wav",
    "filename": "sample.wav",
    "content_type": "audio/wav",
    "size": 1024000
  }
}
```

## 对话中的语音回复

### 启用语音回复

在对话编排服务中，当 `ConversationSettings.enable_tts` 为 `true` 时，系统会自动为角色回复生成语音。

#### 音色选择逻辑

系统会根据角色名称自动选择合适的音色：

1. **女性角色**: 包含"女"、"姐"、"妹"、"娘"、"甜"、"温柔"等关键词
   - 可选音色: Cherry, Jennifer, Katerina, Jada, Sunny, Kiki

2. **男性角色**: 包含"男"、"哥"、"弟"、"爷"、"叔"、"强"等关键词
   - 可选音色: Ethan, Ryan, Elias, Dylan, Marcus, Roy, Peter, Rocky, Eric

3. **默认音色**: Dylan（北京-晓东）

#### 语音回复流程

1. 用户发送消息
2. LLM生成角色回复文本
3. 如果启用TTS，系统自动选择音色
4. 调用TTS服务生成语音
5. 将音频文件保存到云存储
6. 返回音频URL给前端

#### 响应格式

```json
{
  "success": true,
  "user_message": {...},
  "character_message": {...},
  "character_response": {...},
  "audio_url": "https://storage.example.com/audio/tts_角色名_20241201_143022.wav",
  "usage": {...}
}
```

## 音色目录

### 支持的音色

系统预置了17种Qwen3-TTS音色：

| 音色代码 | 音色名称 | 描述 | 性别 |
|---------|---------|------|------|
| Cherry | 芊悦 | 阳光积极、亲切自然小姐姐 | 女 |
| Ethan | 晨煦 | 标准普通话，带部分北方口音 | 男 |
| Nofish | 不吃鱼 | 不会翘舌音的设计师 | 男 |
| Jennifer | 詹妮弗 | 品牌级、电影质感般美语女声 | 女 |
| Ryan | 甜茶 | 节奏拉满，戏感炸裂 | 男 |
| Katerina | 卡捷琳娜 | 御姐音色，韵律回味十足 | 女 |
| Elias | 墨讲师 | 严谨叙事，适合知识讲解 | 男 |
| Jada | 上海-阿珍 | 沪上阿姐，风风火火 | 女 |
| Dylan | 北京-晓东 | 北京胡同里长大的少年 | 男 |
| Sunny | 四川-晴儿 | 甜到你心里的川妹子 | 女 |
| li | 南京-老李 | 耐心的瑜伽老师 | 男 |
| Marcus | 陕西-秦川 | 面宽话短，心实声沉 | 男 |
| Roy | 闽南-阿杰 | 诙谐直爽、市井活泼 | 男 |
| Peter | 天津-李彼得 | 相声捧哏风格 | 男 |
| Rocky | 粤语-阿强 | 幽默风趣，在线陪聊 | 男 |
| Kiki | 粤语-阿清 | 甜美港风闺蜜 | 女 |
| Eric | 四川-程川 | 一个跳脱市井的四川成都男子 | 男 |

## 错误处理

### 常见错误

1. **文本为空**: `400 Bad Request - 文本内容不能为空`
2. **文本过长**: `400 Bad Request - 文本长度不能超过600字符`
3. **音频URL无效**: `400 Bad Request - 音频URL必须是公网可访问的HTTP链接`
4. **文件类型不支持**: `400 Bad Request - 只支持音频文件`
5. **文件过大**: `400 Bad Request - 文件大小不能超过10MB`
6. **API密钥未配置**: `500 Internal Server Error - QWEN_API_KEY 未配置`

### 错误响应格式

```json
{
  "detail": "错误描述信息"
}
```

## 配置要求

### 环境变量

```bash
# 千问API密钥
QWEN_API_KEY=your_qwen_api_key

# 七牛云存储配置
QINIU_ACCESS_KEY=your_access_key
QINIU_SECRET_KEY=your_secret_key
QINIU_BUCKET_NAME=your_bucket_name
QINIU_DOMAIN=your_domain
```

### 依赖服务

- **千问TTS服务**: 用于文本转语音
- **千问ASR服务**: 用于语音转文本
- **七牛云存储**: 用于音频文件存储
- **PostgreSQL**: 用于音色目录管理

## 性能优化

### TTS优化

1. **文本长度限制**: 单次请求最大600字符
2. **音色缓存**: 缓存常用音色配置
3. **音频缓存**: 相同文本和音色的音频文件可以复用

### STT优化

1. **文件大小限制**: 音频文件不超过10MB
2. **格式支持**: 支持多种音频格式
3. **并发处理**: 支持多个语音识别请求并发

## 使用建议

1. **音色选择**: 根据角色特征选择合适的音色
2. **文本处理**: 长文本建议分段处理
3. **错误重试**: 网络错误时建议重试
4. **音频质量**: 使用高质量音频文件获得更好的识别效果
5. **缓存策略**: 相同内容的语音可以缓存避免重复生成
