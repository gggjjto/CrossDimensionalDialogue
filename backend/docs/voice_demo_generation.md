# 音色示例语音生成功能

## 功能概述

为每个音色生成示例语音，上传到七牛云存储，并将预览URL存储到数据库中。用户可以在音色选择界面听到每个音色的效果。

## 功能特性

### 1. 自动生成示例语音
- 为每个音色生成个性化的示例文本
- 使用TTS服务生成高质量音频
- 支持17种不同的音色

### 2. 云存储集成
- 自动上传音频到七牛云存储
- 生成公网可访问的URL
- 支持音频文件管理

### 3. 数据库管理
- 将预览URL存储到数据库
- 支持增量更新
- 避免重复生成

## API接口

### 1. 获取音色示例语音状态
```http
GET /api/v1/voice-demo/status?provider=qwen3-tts
Authorization: Bearer <token>
```

**响应示例:**
```json
{
  "success": true,
  "data": {
    "total": 17,
    "with_demo": 15,
    "without_demo": 2,
    "completion_rate": 88.24,
    "voices": [
      {
        "id": "uuid",
        "name": "芊悦",
        "voice": "Cherry",
        "has_demo": true,
        "preview_url": "https://example.com/demo.wav"
      }
    ]
  }
}
```

### 2. 为所有音色生成示例语音
```http
POST /api/v1/voice-demo/generate-all?provider=qwen3-tts&force_regenerate=false
Authorization: Bearer <superuser_token>
```

**参数说明:**
- `provider`: 音色提供方，默认为 "qwen3-tts"
- `force_regenerate`: 是否强制重新生成，默认为 false

**响应示例:**
```json
{
  "success": true,
  "data": {
    "total": 17,
    "success_count": 15,
    "failed_count": 2,
    "skipped_count": 0,
    "results": [
      {
        "voice": "Cherry",
        "name": "芊悦",
        "status": "success",
        "url": "https://example.com/demo.wav"
      }
    ]
  }
}
```

### 3. 为指定音色生成示例语音
```http
POST /api/v1/voice-demo/generate/{voice_id}?demo_text=自定义文本
Authorization: Bearer <superuser_token>
```

**参数说明:**
- `voice_id`: 音色ID
- `demo_text`: 自定义示例文本（可选）

## 使用方法

### 1. 初始化音色目录和示例语音

```bash
# 运行初始化脚本
cd backend
python scripts/init_voice_demos.py
```

### 2. 通过API生成示例语音

```bash
# 获取认证token
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=changethis" | jq -r '.access_token')

# 为所有音色生成示例语音
curl -X POST "http://localhost:8000/api/v1/voice-demo/generate-all" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"

# 查看状态
curl -X GET "http://localhost:8000/api/v1/voice-demo/status" \
  -H "Authorization: Bearer $TOKEN"
```

### 3. 测试功能

```bash
# 运行测试脚本
cd backend
python test_voice_demo_generation.py
```

## 音色列表

系统支持以下17种音色：

| 音色名称 | 音色标识 | 描述 | 示例文本 |
|---------|---------|------|---------|
| 芊悦 | Cherry | 阳光积极、亲切自然小姐姐 | 你好，我是芊悦，很高兴认识你！ |
| 晨煦 | Ethan | 标准普通话，带部分北方口音 | 大家好，我是晨煦，阳光温暖的声音陪伴你。 |
| 不吃鱼 | Nofish | 不会翘舌音的设计师 | 嗨，我是不吃鱼，虽然不会翘舌音，但声音很特别哦！ |
| 詹妮弗 | Jennifer | 品牌级、电影质感般美语女声 | Hello, I'm Jennifer, your professional English voice assistant. |
| 甜茶 | Ryan | 节奏拉满，戏感炸裂 | 我是甜茶，节奏拉满，戏感炸裂，准备好听我的声音了吗？ |
| 卡捷琳娜 | Katerina | 御姐音色，韵律回味十足 | 你好，我是卡捷琳娜，御姐音色，韵律回味十足。 |
| 墨讲师 | Elias | 严谨叙事，适合知识讲解 | 大家好，我是墨讲师，严谨叙事，适合知识讲解。 |
| 上海-阿珍 | Jada | 沪上阿姐，风风火火 | 侬好，我是上海阿珍，风风火火的上海阿姐。 |
| 北京-晓东 | Dylan | 北京胡同里长大的少年 | 您好，我是北京晓东，胡同里长大的北京爷们儿。 |
| 四川-晴儿 | Sunny | 甜到你心里的川妹子 | 你好，我是四川晴儿，甜到你心里的川妹子。 |
| 南京-老李 | li | 耐心的瑜伽老师 | 你好，我是南京老李，耐心的瑜伽老师。 |
| 陕西-秦川 | Marcus | 面宽话短，心实声沉 | 你好，我是陕西秦川，面宽话短，心实声沉。 |
| 闽南-阿杰 | Roy | 诙谐直爽、市井活泼的台湾哥仔 | 你好，我是闽南阿杰，诙谐直爽的台湾哥仔。 |
| 天津-李彼得 | Peter | 相声捧哏风格 | 你好，我是天津李彼得，相声捧哏风格。 |
| 粤语-阿强 | Rocky | 幽默风趣，在线陪聊 | 你好，我是粤语阿强，幽默风趣，在线陪聊。 |
| 粤语-阿清 | Kiki | 甜美港风闺蜜 | 你好，我是粤语阿清，甜美港风闺蜜。 |
| 四川-程川 | Eric | 一个跳脱市井的四川成都男子 | 你好，我是四川程川，跳脱市井的成都男子。 |

## 技术实现

### 1. 服务架构
- `VoiceDemoService`: 核心服务类
- `TTSService`: 文本转语音服务
- `QiniuStorageService`: 七牛云存储服务
- `VoiceCatalogCRUD`: 音色目录数据库操作

### 2. 文件结构
```
backend/
├── app/
│   ├── services/
│   │   └── voice_demo_service.py      # 音色示例语音生成服务
│   ├── api/routes/voice/
│   │   └── voice_demo.py              # API路由
│   └── models/
│       └── voice_catalog.py           # 音色目录模型
├── scripts/
│   └── init_voice_demos.py            # 初始化脚本
└── test_voice_demo_generation.py      # 测试脚本
```

### 3. 数据库表结构
```sql
CREATE TABLE voice_catalog (
    id UUID PRIMARY KEY,
    provider VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    voice VARCHAR(100) NOT NULL,
    preview_url VARCHAR(500),           -- 示例语音URL
    description VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

## 环境要求

### 1. 环境变量
```bash
# 阿里云通义语音API
QWEN_API_KEY=your_qwen_api_key

# 七牛云存储
QINIU_ACCESS_KEY=your_access_key
QINIU_SECRET_KEY=your_secret_key
QINIU_BUCKET_NAME=your_bucket_name
```

### 2. 依赖服务
- 阿里云通义语音TTS服务
- 七牛云对象存储服务
- PostgreSQL数据库

## 注意事项

1. **权限要求**: 生成示例语音需要超级用户权限
2. **API限制**: 注意TTS服务的API调用限制
3. **存储成本**: 音频文件会占用七牛云存储空间
4. **网络要求**: 需要稳定的网络连接访问外部API
5. **错误处理**: 生成失败时会记录详细错误信息

## 故障排除

### 1. 常见问题
- **TTS服务失败**: 检查API密钥和网络连接
- **存储上传失败**: 检查七牛云配置和权限
- **数据库更新失败**: 检查数据库连接和权限

### 2. 日志查看
```bash
# 查看应用日志
tail -f logs/app.log | grep "voice_demo"
```

### 3. 手动修复
```python
# 重新生成特定音色的示例语音
from app.services.voice_demo_service import voice_demo_service
from app.crud.voice_catalog import voice_catalog_crud

# 获取音色
voice = voice_catalog_crud.get_by_voice(session, provider="qwen3-tts", voice="Cherry")

# 重新生成
audio_url = await voice_demo_service.generate_demo_audio_for_voice(session, voice)
```
