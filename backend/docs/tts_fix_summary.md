# TTS服务修复总结

## 问题分析

### 原始错误
```
ERROR:app.services.tts_service:TTS合成失败: 'NoneType' object has no attribute 'audio'
ERROR:app.services.voice_demo_service:为音色 卡捷琳娜 生成示例语音失败: TTS合成失败: 'NoneType' object has no attribute 'audio'
```

### 问题原因
1. **流式vs非流式响应结构不同**：原始代码假设使用流式API，但实际使用的是非流式API
2. **响应对象结构不匹配**：非流式响应的结构是 `response.output.audio`，而不是 `chunk.output.audio`
3. **缺少空值检查**：没有检查 `chunk.output` 是否为 `None`

## 修复方案

### 1. 切换到非流式API
```python
# 之前 - 流式API
response = MultiModalConversation.call(
    api_key=self.api_key,
    model=model,
    text=req.text,
    voice=voice,
    language_type="Chinese",
    stream=True,  # 流式
)

# 现在 - 非流式API
response = MultiModalConversation.call(
    api_key=self.api_key,
    model=model,
    text=req.text,
    voice=voice,
    language_type="Chinese",
    stream=False,  # 非流式
)
```

### 2. 修复响应处理逻辑
```python
# 之前 - 流式处理
for chunk in response:
    audio = chunk.output.audio  # 这里会出错，因为chunk.output可能为None
    if audio.data is not None:
        wav_bytes = base64.b64decode(audio.data)
        audio_data_list.append(wav_bytes)

# 现在 - 非流式处理
if not hasattr(response, 'output') or response.output is None:
    raise ValueError("TTS响应格式错误：缺少output字段")

if not hasattr(response.output, 'audio') or response.output.audio is None:
    raise ValueError("TTS响应格式错误：缺少audio字段")

audio = response.output.audio
```

### 3. 支持两种音频数据格式
```python
# 检查是否有音频数据
if not hasattr(audio, 'data') or not audio.data:
    # 如果没有data字段，尝试使用url字段
    if hasattr(audio, 'url') and audio.url:
        # 下载URL中的音频数据
        async with httpx.AsyncClient() as client:
            audio_resp = await client.get(audio.url)
            if audio_resp.status_code == 200:
                audio_bytes = audio_resp.content
    else:
        raise ValueError("TTS响应中没有音频数据")
else:
    # 使用base64编码的音频数据
    audio_bytes = base64.b64decode(audio.data)
```

### 4. 添加详细的调试信息
```python
logger.info(f"开始TTS合成: 文本='{req.text[:50]}...', 音色='{voice}', 模型='{model}'")
logger.info(f"TTS API调用成功，响应类型: {type(response)}")
logger.debug(f"响应对象属性: {dir(response)}")
logger.debug(f"output对象属性: {dir(response.output)}")
logger.debug(f"audio对象属性: {dir(audio)}")
```

## 修复后的代码结构

### 主要变更
1. **API调用方式**：从流式改为非流式
2. **响应处理**：直接处理单个响应对象，而不是流式chunk
3. **错误处理**：添加了完整的空值检查和错误信息
4. **调试支持**：添加了详细的日志记录

### 支持的响应格式
根据DashScope SDK文档，非流式TTS响应格式为：
```json
{
    "output": {
        "finish_reason": "stop",
        "audio": {
            "expires_at": 1745053690,
            "data": "base64_encoded_audio_data",  // 或者为空
            "id": "audio_id",
            "url": "http://example.com/audio.wav"  // 音频文件URL
        }
    },
    "usage": {
        "input_tokens": 76,
        "output_tokens": 1082,
        "total_tokens": 1158
    },
    "request_id": "request_id"
}
```

## 测试验证

### 测试脚本
创建了 `test_tts_fix.py` 来验证修复效果：

```python
# 测试TTS服务
test_request = TTSRequest(
    text="你好，我是通义千问，很高兴为你服务！",
    voice="Cherry",
    audio_format="wav",
    sample_rate=24000,
)

response = await tts_service.synthesize(test_request)
```

### 预期结果
- ✅ 成功生成音频数据
- ✅ 正确解码base64音频或下载URL音频
- ✅ 返回完整的TTSResponse对象
- ✅ 保存测试音频文件

## 环境要求

### 必需的环境变量
```bash
export QWEN_API_KEY=your_dashscope_api_key
```

### 依赖包
```toml
dependencies = [
    "dashscope>=1.24.6",
    "httpx>=0.25.1",
    # ... 其他依赖
]
```

## 使用示例

### 基本用法
```python
from app.services.tts_service import TTSService, TTSRequest

# 创建TTS服务
tts_service = TTSService()

# 创建请求
request = TTSRequest(
    text="你好，我是通义千问",
    voice="Cherry",
    audio_format="wav",
    sample_rate=24000
)

# 生成语音
response = await tts_service.synthesize(request)

# 获取音频数据
audio_bytes = response.audio_bytes
```

### 在音色示例语音生成中使用
```python
# voice_demo_service.py 中的使用
tts_request = TTSRequest(
    text=demo_text,
    voice=voice_catalog.voice,
    audio_format="wav",
    sample_rate=24000,
)

tts_response = await self.tts_service.synthesize(tts_request)
```

## 注意事项

1. **API Key配置**：确保正确设置 `QWEN_API_KEY` 环境变量
2. **网络连接**：需要稳定的网络连接访问DashScope服务
3. **音频格式**：默认生成WAV格式，采样率24000Hz
4. **文本长度**：单次调用最大支持600字符
5. **错误处理**：现在有完整的错误处理和日志记录

## 故障排除

### 常见问题
1. **API Key错误**：检查环境变量是否正确设置
2. **网络连接失败**：检查网络连接和防火墙设置
3. **响应格式错误**：检查DashScope SDK版本是否为1.24.6+
4. **音频数据为空**：检查文本内容和音色参数

### 调试方法
```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 检查API Key
print(f"API Key: {settings.QWEN_API_KEY[:10]}...")

# 测试简单文本
test_text = "测试"
print(f"测试文本: {test_text}")
```

这次修复解决了TTS服务的核心问题，使其能够正确处理DashScope SDK的非流式响应，为音色示例语音生成功能提供了可靠的基础。
