# 语音对话API文档

## 概述

语音对话API提供了完整的语音交互功能，支持用户发送语音消息，系统自动进行语音识别、AI生成回复，并返回语音回复。

## 完整流程

### 1. 用户发送语音消息流程

```
用户录音 → 上传音频文件 → STT语音识别 → LLM生成回复 → TTS语音合成 → 返回语音回复
```

### 2. API端点

#### 2.1 上传音频文件

**POST** `/api/v1/voice/upload-audio`

上传用户的语音文件到云存储，获取公网可访问的URL。

**请求参数:**
- `file`: 音频文件（multipart/form-data）

**响应示例:**
```json
{
  "success": true,
  "audio_url": "https://storage.example.com/audio/voice_123_20241201_143022.wav",
  "filename": "voice_123_20241201_143022.wav",
  "file_size": 1024000
}
```

#### 2.2 处理语音消息

**POST** `/api/v1/voice/message`

完整的语音对话处理，包括STT、LLM、TTS。

**请求体:**
```json
{
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
  "audio_file_url": "https://storage.example.com/audio/voice_123_20241201_143022.wav",
  "voice_preference": "Cherry"
}
```

**响应示例:**
```json
{
  "success": true,
  "user_message_id": "123e4567-e89b-12d3-a456-426614174001",
  "character_message_id": "123e4567-e89b-12d3-a456-426614174002",
  "text_response": "你好！很高兴听到你的声音，有什么我可以帮助你的吗？",
  "audio_response_url": "https://storage.example.com/audio/tts_角色名_20241201_143025.wav",
  "voice_used": "Cherry",
  "stt_text": "你好，我想和你聊天"
}
```

## 使用示例

### 前端实现示例

```javascript
// 1. 录音并上传
async function recordAndUpload() {
  const mediaRecorder = new MediaRecorder(stream);
  const chunks = [];
  
  mediaRecorder.ondataavailable = (event) => {
    chunks.push(event.data);
  };
  
  mediaRecorder.onstop = async () => {
    const audioBlob = new Blob(chunks, { type: 'audio/wav' });
    const formData = new FormData();
    formData.append('file', audioBlob);
    
    // 上传音频文件
    const uploadResponse = await fetch('/api/v1/voice/upload-audio', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });
    
    const uploadResult = await uploadResponse.json();
    
    if (uploadResult.success) {
      // 处理语音消息
      await processVoiceMessage(uploadResult.audio_url);
    }
  };
  
  mediaRecorder.start();
  // 录音逻辑...
  mediaRecorder.stop();
}

// 2. 处理语音消息
async function processVoiceMessage(audioUrl) {
  const response = await fetch('/api/v1/voice/message', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      conversation_id: currentConversationId,
      audio_file_url: audioUrl,
      voice_preference: selectedVoice
    })
  });
  
  const result = await response.json();
  
  if (result.success) {
    // 显示文本回复
    displayTextMessage(result.text_response);
    
    // 播放语音回复
    if (result.audio_response_url) {
      playAudio(result.audio_response_url);
    }
  }
}

// 3. 播放音频
function playAudio(audioUrl) {
  const audio = new Audio(audioUrl);
  audio.play();
}
```

### curl示例

```bash
# 1. 上传音频文件
curl -X POST "http://localhost:8000/api/v1/voice/upload-audio" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@voice_recording.wav"

# 2. 处理语音消息
curl -X POST "http://localhost:8000/api/v1/voice/message" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
    "audio_file_url": "https://storage.example.com/audio/voice_123_20241201_143022.wav",
    "voice_preference": "Cherry"
  }'
```

## 技术实现

### 1. 语音识别 (STT)

- **服务**: 千问ASR Flash模型
- **输入**: 音频文件URL
- **输出**: 识别的文本内容
- **支持格式**: WAV, MP3, M4A等

### 2. AI生成回复 (LLM)

- **服务**: 千问Plus模型
- **输入**: 用户文本 + 角色设定 + 对话历史
- **输出**: 角色回复文本
- **特点**: 保持角色一致性

### 3. 语音合成 (TTS)

- **服务**: 千问TTS Flash模型
- **输入**: 文本 + 音色选择
- **输出**: 音频文件
- **音色**: 17种预置音色可选

### 4. 云存储

- **服务**: 七牛云存储
- **功能**: 音频文件存储和管理
- **特点**: 高可用、CDN加速

## 音色选择

### 音色选择优先级

系统按以下优先级选择音色：

1. **用户偏好音色** - 用户通过 `voice_preference` 参数指定
2. **角色默认音色** - 角色设置的 `default_voice` 字段
3. **全局默认音色** - Cherry（芊悦）音色

### 角色默认音色

每个角色可以设置自己的默认音色：

```json
{
  "name": "小美",
  "short_bio": "温柔可爱的AI助手",
  "default_voice": "Cherry",  // 角色的默认音色
  "persona_text": "..."
}
```

### 用户偏好音色

用户可以通过 `voice_preference` 参数指定偏好的音色：

```json
{
  "voice_preference": "Jennifer"  // 指定使用詹妮弗音色
}
```

### 全局默认音色

如果角色没有设置默认音色或音色不可用，系统使用 **Cherry（芊悦）** 音色。

### 可用音色列表

系统支持17种预置音色，用户可以根据喜好选择：

- **Cherry（芊悦）**: 阳光积极、亲切自然小姐姐（默认）
- **Jennifer（詹妮弗）**: 品牌级、电影质感般美语女声
- **Katerina（卡捷琳娜）**: 御姐音色，韵律回味十足
- **Jada（上海-阿珍）**: 沪上阿姐，风风火火
- **Sunny（四川-晴儿）**: 甜到你心里的川妹子
- **Kiki（粤语-阿清）**: 甜美港风闺蜜
- **Ethan（晨煦）**: 标准普通话，带部分北方口音
- **Ryan（甜茶）**: 节奏拉满，戏感炸裂
- **Elias（墨讲师）**: 严谨叙事，适合知识讲解
- **Dylan（北京-晓东）**: 北京胡同里长大的少年
- **Marcus（陕西-秦川）**: 面宽话短，心实声沉
- **Roy（闽南-阿杰）**: 诙谐直爽、市井活泼
- **Peter（天津-李彼得）**: 相声捧哏风格
- **Rocky（粤语-阿强）**: 幽默风趣，在线陪聊
- **Eric（四川-程川）**: 一个跳脱市井的四川成都男子

## 错误处理

### 常见错误

1. **文件类型错误**: `400 Bad Request - 只支持音频文件`
2. **文件过大**: `400 Bad Request - 文件大小不能超过10MB`
3. **音频URL无效**: `400 Bad Request - 音频URL无效`
4. **语音识别失败**: `500 Internal Server Error - 语音识别失败`
5. **AI生成失败**: `500 Internal Server Error - AI生成回复失败`
6. **语音合成失败**: `500 Internal Server Error - 语音合成失败`

### 错误响应格式

```json
{
  "success": false,
  "error": "错误描述信息"
}
```

## 性能优化

### 1. 音频文件优化

- **格式**: 推荐使用WAV格式，采样率24kHz
- **大小**: 单次录音建议不超过10MB
- **时长**: 单次语音建议不超过60秒

### 2. 缓存策略

- **相同文本**: 相同文本和音色的TTS结果可以缓存
- **音色配置**: 音色列表可以缓存
- **用户偏好**: 用户音色偏好可以缓存

### 3. 并发处理

- **STT并发**: 支持多个语音识别请求并发
- **TTS并发**: 支持多个语音合成请求并发
- **存储并发**: 支持多个文件上传并发

## 配置要求

### 环境变量

```bash
# 千问API配置
QWEN_API_KEY=your_qwen_api_key

# 七牛云存储配置
QINIU_ACCESS_KEY=your_access_key
QINIU_SECRET_KEY=your_secret_key
QINIU_BUCKET_NAME=your_bucket_name
QINIU_DOMAIN=your_domain

# 文件大小限制
MAX_AUDIO_FILE_SIZE=10485760  # 10MB
```

### 依赖服务

- **千问ASR**: 语音识别服务
- **千问TTS**: 语音合成服务
- **千问LLM**: AI生成服务
- **七牛云**: 文件存储服务
- **PostgreSQL**: 数据存储

## 最佳实践

### 1. 前端录音

- 使用Web Audio API进行高质量录音
- 设置合适的采样率和位深度
- 实现录音状态指示和进度显示

### 2. 错误处理

- 实现重试机制
- 提供用户友好的错误提示
- 记录详细的错误日志

### 3. 用户体验

- 提供录音状态反馈
- 实现语音播放控制
- 支持音色预览和选择

### 4. 性能监控

- 监控API响应时间
- 跟踪语音识别准确率
- 监控存储使用情况

## 扩展功能

### 1. 实时语音

- WebRTC实时语音通话
- 流式语音识别
- 实时语音合成

### 2. 多语言支持

- 多语言语音识别
- 多语言语音合成
- 自动语言检测

### 3. 情感分析

- 语音情感识别
- 情感化语音合成
- 情感化回复生成

### 4. 个性化

- 用户音色训练
- 个性化回复风格
- 语音偏好学习
