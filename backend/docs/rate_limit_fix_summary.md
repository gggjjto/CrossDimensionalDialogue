# API限流问题修复总结

## 问题分析

### 原始错误
```
ERROR:app.services.tts_service:响应结构: {"status_code": 429, "request_id": "aaf8c18f-3e62-4205-bc4d-0dae3770b710", "code": "Throttling.RateQuota", "message": "Requests rate limit exceeded, please try again later.", "output": null, "usage": null}
ERROR:app.services.tts_service:TTS合成失败: TTS响应格式错误：缺少output字段
```

### 问题原因
1. **API限流**：DashScope TTS API有速率限制，短时间内发送太多请求会被限流
2. **错误处理不完整**：原始代码没有检查API调用的状态码
3. **批量请求**：音色示例语音生成时同时发送多个请求，触发限流

## 修复方案

### 1. TTS服务错误处理增强

#### 添加状态码检查
```python
# 检查API调用是否成功
if hasattr(response, 'status_code') and response.status_code != 200:
    error_msg = f"TTS API调用失败: {response.status_code}"
    if hasattr(response, 'message'):
        error_msg += f" - {response.message}"
    if hasattr(response, 'code'):
        error_msg += f" (错误码: {response.code})"
    logger.error(f"TTS API错误: {error_msg}")
    raise ValueError(error_msg)
```

#### 支持的错误类型
- **429 限流错误**：`Throttling.RateQuota`
- **其他API错误**：网络错误、认证错误等
- **响应格式错误**：缺少必要字段

### 2. 音色示例语音生成服务重试机制

#### 添加重试参数
```python
async def generate_demo_audio_for_voice(
    self,
    session: Session,
    voice_catalog: VoiceCatalog,
    demo_text: Optional[str] = None,
    max_retries: int = 3,        # 最大重试次数
    retry_delay: float = 5.0,    # 重试延迟时间（秒）
) -> Optional[str]:
```

#### 指数退避重试策略
```python
for attempt in range(max_retries + 1):
    try:
        # TTS调用逻辑
        pass
    except ValueError as e:
        error_msg = str(e)
        # 检查是否是限流错误
        if "Requests rate limit exceeded" in error_msg or "Throttling" in error_msg:
            if attempt < max_retries:
                wait_time = retry_delay * (2 ** attempt)  # 指数退避
                logger.warning(f"遇到限流，第 {attempt + 1} 次重试，等待 {wait_time} 秒...")
                await asyncio.sleep(wait_time)
                continue
            else:
                logger.error(f"重试 {max_retries} 次后仍然限流")
                return None
```

#### 重试时间表
- 第1次重试：等待 5 秒
- 第2次重试：等待 10 秒  
- 第3次重试：等待 20 秒
- 第4次重试：等待 40 秒

### 3. 批量请求限流控制

#### 添加请求间隔
```python
for i, voice in enumerate(voices):
    # 添加延迟以避免API限流
    if i > 0:  # 第一个请求不需要延迟
        await asyncio.sleep(2)  # 每个请求间隔2秒
    
    # 生成示例语音
    audio_url = await self.generate_demo_audio_for_voice(session, voice)
```

#### 限流控制策略
- **请求间隔**：每个请求间隔2秒
- **重试机制**：单个请求失败时自动重试
- **错误分类**：区分限流错误和其他错误

## 修复后的错误处理流程

### 1. TTS服务调用流程
```
1. 调用DashScope API
2. 检查响应状态码
   ├─ 200: 正常处理
   ├─ 429: 抛出限流错误
   └─ 其他: 抛出相应错误
3. 检查响应结构
   ├─ 有output: 处理音频数据
   └─ 无output: 抛出格式错误
4. 返回结果
```

### 2. 音色示例语音生成流程
```
1. 遍历所有音色
2. 检查是否已有预览URL
   ├─ 有且不强制重新生成: 跳过
   └─ 无或强制重新生成: 继续
3. 添加请求间隔延迟
4. 调用TTS服务生成语音
   ├─ 成功: 上传到七牛云，更新数据库
   ├─ 限流错误: 等待后重试
   └─ 其他错误: 记录错误，继续下一个
5. 返回统计结果
```

## 使用示例

### 基本TTS调用
```python
from app.services.tts_service import TTSService, TTSRequest

tts_service = TTSService()
request = TTSRequest(
    text="测试文本",
    voice="Cherry",
    audio_format="wav",
    sample_rate=24000
)

try:
    response = await tts_service.synthesize(request)
    print(f"生成成功: {len(response.audio_bytes)} 字节")
except ValueError as e:
    if "限流" in str(e):
        print("遇到限流，请稍后重试")
    else:
        print(f"其他错误: {e}")
```

### 音色示例语音生成
```python
from app.services.voice_demo_service import voice_demo_service

# 生成单个音色的示例语音
audio_url = await voice_demo_service.generate_demo_audio_for_voice(
    session=session,
    voice_catalog=voice_catalog,
    demo_text="自定义示例文本",
    max_retries=3,
    retry_delay=5.0
)

# 批量生成所有音色的示例语音
result = await voice_demo_service.generate_demo_audio_for_all_voices(
    session=session,
    provider="qwen3-tts",
    force_regenerate=False
)
```

## 配置建议

### 1. 环境变量
```bash
# 必需的环境变量
export QWEN_API_KEY=your_dashscope_api_key
export QINIU_ACCESS_KEY=your_qiniu_access_key
export QINIU_SECRET_KEY=your_qiniu_secret_key
export QINIU_BUCKET_NAME=your_bucket_name
```

### 2. 重试配置
```python
# 推荐的重试配置
max_retries = 3          # 最大重试3次
retry_delay = 5.0        # 基础延迟5秒
request_interval = 2.0   # 请求间隔2秒
```

### 3. 日志配置
```python
import logging
logging.basicConfig(level=logging.INFO)

# 查看详细的重试日志
logger = logging.getLogger("app.services.voice_demo_service")
```

## 监控和调试

### 1. 日志监控
```bash
# 查看限流相关日志
grep "限流\|Throttling\|RateQuota" logs/app.log

# 查看重试日志
grep "重试\|retry" logs/app.log
```

### 2. 错误统计
```python
# 查看生成结果统计
result = await voice_demo_service.generate_demo_audio_for_all_voices(session)
print(f"成功: {result['success_count']}")
print(f"失败: {result['failed_count']}")
print(f"跳过: {result['skipped_count']}")
```

### 3. 性能优化
- **减少并发**：避免同时发送太多请求
- **增加延迟**：在请求间隔和重试延迟之间找到平衡
- **分批处理**：将大量音色分批处理

## 注意事项

1. **API配额**：注意DashScope API的每日配额限制
2. **重试次数**：不要设置过多的重试次数，避免长时间等待
3. **错误处理**：区分可重试的错误和不可重试的错误
4. **日志记录**：记录详细的错误信息以便调试
5. **监控告警**：设置限流错误的监控告警

这次修复解决了API限流问题，使音色示例语音生成功能更加稳定可靠。
