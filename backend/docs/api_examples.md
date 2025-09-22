# 角色管理API使用示例

## 认证

所有API请求都需要Bearer Token认证：

```bash
# 获取认证令牌（需要先实现用户认证）
TOKEN="your_jwt_token_here"

# 在请求头中添加认证
curl -H "Authorization: Bearer $TOKEN" ...
```

## 角色管理

### 1. 创建角色

```bash
curl -X POST "http://localhost:8000/api/v1/characters/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "苏格拉底",
    "short_bio": "古希腊哲学家，以问答法著称，相信通过不断的提问和思考可以发现真理",
    "avatar_url": "https://example.com/socrates.jpg",
    "persona_text": "我是苏格拉底，古希腊的哲学家。我以问答法闻名，相信通过不断的提问和思考，我们可以发现真理。我总是说'我知道我什么都不知道'，这体现了我对知识的谦逊态度。",
    "example_lines": [
      "我知道我什么都不知道",
      "未经审视的人生不值得过",
      "美德即知识"
    ],
    "source": "古希腊哲学",
    "is_active": true,
    "tag_ids": ["tag-uuid-1", "tag-uuid-2"]
  }'
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "id": "6abc75e4-9146-4b2f-9d5f-ee74dc2c21f3",
    "name": "苏格拉底",
    "short_bio": "古希腊哲学家，以问答法著称，相信通过不断的提问和思考可以发现真理",
    "avatar_url": "https://example.com/socrates.jpg",
    "persona_text": "我是苏格拉底，古希腊的哲学家...",
    "example_lines": ["我知道我什么都不知道", "未经审视的人生不值得过", "美德即知识"],
    "source": "古希腊哲学",
    "is_active": true,
    "created_at": "2024-09-22T09:26:32.488401",
    "updated_at": "2024-09-22T09:26:32.488401",
    "tags": [
      {
        "id": "tag-uuid-1",
        "name": "哲学",
        "description": "哲学相关角色",
        "color": "#FF5733"
      }
    ]
  },
  "msg": "角色创建成功"
}
```

### 2. 获取角色列表

```bash
# 基本查询
curl "http://localhost:8000/api/v1/characters/?limit=10&offset=0&is_active=true" \
  -H "Authorization: Bearer $TOKEN"

# 带分页的查询
curl "http://localhost:8000/api/v1/characters/?limit=5&offset=10" \
  -H "Authorization: Bearer $TOKEN"
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "data": [
      {
        "id": "6abc75e4-9146-4b2f-9d5f-ee74dc2c21f3",
        "name": "苏格拉底",
        "short_bio": "古希腊哲学家，以问答法著称",
        "avatar_url": "https://example.com/socrates.jpg",
        "persona_text": "我是苏格拉底，古希腊的哲学家...",
        "example_lines": ["我知道我什么都不知道"],
        "source": "古希腊哲学",
        "is_active": true,
        "created_at": "2024-09-22T09:26:32.488401",
        "updated_at": "2024-09-22T09:26:32.488401",
        "tags": []
      }
    ],
    "count": 1
  },
  "msg": "查询成功"
}
```

### 3. 获取单个角色

```bash
curl "http://localhost:8000/api/v1/characters/6abc75e4-9146-4b2f-9d5f-ee74dc2c21f3" \
  -H "Authorization: Bearer $TOKEN"
```

### 4. 更新角色

```bash
curl -X PUT "http://localhost:8000/api/v1/characters/6abc75e4-9146-4b2f-9d5f-ee74dc2c21f3" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "苏格拉底（更新）",
    "short_bio": "更新后的简介",
    "persona_text": "更新后的人格文本",
    "is_active": true
  }'
```

### 5. 删除角色

```bash
curl -X DELETE "http://localhost:8000/api/v1/characters/6abc75e4-9146-4b2f-9d5f-ee74dc2c21f3" \
  -H "Authorization: Bearer $TOKEN"
```

## 角色搜索

### 1. 文本搜索

```bash
# 基本文本搜索
curl "http://localhost:8000/api/v1/characters/search?query=哲学家&search_type=text&limit=10" \
  -H "Authorization: Bearer $TOKEN"

# 带标签过滤的搜索
curl "http://localhost:8000/api/v1/characters/search?query=哲学&search_type=text&tag_ids=tag-uuid-1&limit=5" \
  -H "Authorization: Bearer $TOKEN"
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "character": {
          "id": "6abc75e4-9146-4b2f-9d5f-ee74dc2c21f3",
          "name": "苏格拉底",
          "short_bio": "古希腊哲学家，以问答法著称",
          "persona_text": "我是苏格拉底，古希腊的哲学家...",
          "example_lines": ["我知道我什么都不知道"],
          "source": "古希腊哲学",
          "is_active": true,
          "created_at": "2024-09-22T09:26:32.488401",
          "updated_at": "2024-09-22T09:26:32.488401",
          "tags": []
        },
        "score": null,
        "match_type": "text"
      }
    ],
    "total": 1,
    "query": "哲学家",
    "search_type": "text"
  },
  "msg": "搜索成功"
}
```

### 2. 向量搜索

```bash
# 向量搜索（基于语义相似度）
curl "http://localhost:8000/api/v1/characters/search?query=古希腊思想家&search_type=vector&limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "character": {
          "id": "6abc75e4-9146-4b2f-9d5f-ee74dc2c21f3",
          "name": "苏格拉底",
          "short_bio": "古希腊哲学家，以问答法著称",
          "persona_text": "我是苏格拉底，古希腊的哲学家...",
          "example_lines": ["我知道我什么都不知道"],
          "source": "古希腊哲学",
          "is_active": true,
          "created_at": "2024-09-22T09:26:32.488401",
          "updated_at": "2024-09-22T09:26:32.488401",
          "tags": []
        },
        "score": 0.5323,
        "match_type": "vector"
      }
    ],
    "total": 1,
    "query": "古希腊思想家",
    "search_type": "vector"
  },
  "msg": "搜索成功"
}
```

### 3. 混合搜索

```bash
# 混合搜索（结合文本和向量搜索）
curl "http://localhost:8000/api/v1/characters/search?query=古希腊哲学智慧&search_type=hybrid&limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "character": {
          "id": "6abc75e4-9146-4b2f-9d5f-ee74dc2c21f3",
          "name": "苏格拉底",
          "short_bio": "古希腊哲学家，以问答法著称",
          "persona_text": "我是苏格拉底，古希腊的哲学家...",
          "example_lines": ["我知道我什么都不知道"],
          "source": "古希腊哲学",
          "is_active": true,
          "created_at": "2024-09-22T09:26:32.488401",
          "updated_at": "2024-09-22T09:26:32.488401",
          "tags": []
        },
        "score": 0.3726,
        "match_type": "hybrid"
      }
    ],
    "total": 1,
    "query": "古希腊哲学智慧",
    "search_type": "hybrid"
  },
  "msg": "搜索成功"
}
```

## 标签管理

### 1. 创建标签

```bash
curl -X POST "http://localhost:8000/api/v1/characters/tags/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "哲学",
    "description": "哲学相关角色",
    "color": "#FF5733"
  }'
```

### 2. 获取标签列表

```bash
curl "http://localhost:8000/api/v1/characters/tags/" \
  -H "Authorization: Bearer $TOKEN"
```

### 3. 更新标签

```bash
curl -X PUT "http://localhost:8000/api/v1/characters/tags/tag-uuid-1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "哲学（更新）",
    "description": "更新后的描述",
    "color": "#00FF00"
  }'
```

### 4. 删除标签

```bash
curl -X DELETE "http://localhost:8000/api/v1/characters/tags/tag-uuid-1" \
  -H "Authorization: Bearer $TOKEN"
```

## 嵌入模型管理

### 1. 获取模型信息

```bash
curl "http://localhost:8000/api/v1/characters/embeddings/model-info" \
  -H "Authorization: Bearer $TOKEN"
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "provider": "aliyun",
    "model_name": "text-embedding-v4",
    "dimension": 1024
  },
  "msg": "获取模型信息成功"
}
```

### 2. 切换模型提供商

```bash
# 切换到阿里云
curl -X POST "http://localhost:8000/api/v1/characters/embeddings/switch-provider?provider=aliyun" \
  -H "Authorization: Bearer $TOKEN"

# 切换到OpenAI
curl -X POST "http://localhost:8000/api/v1/characters/embeddings/switch-provider?provider=openai" \
  -H "Authorization: Bearer $TOKEN"
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "provider": "aliyun",
    "model_name": "text-embedding-v4",
    "dimension": 1024
  },
  "msg": "已切换到 aliyun 提供商"
}
```

## Python SDK 使用示例

### 1. 基本使用

```python
import httpx
import asyncio

async def main():
    base_url = "http://localhost:8000"
    headers = {"Authorization": "Bearer your_token_here"}
    
    async with httpx.AsyncClient() as client:
        # 创建角色
        character_data = {
            "name": "测试角色",
            "short_bio": "这是一个测试角色",
            "persona_text": "我是测试角色，用于演示功能",
            "example_lines": ["你好", "再见"],
            "source": "测试"
        }
        
        response = await client.post(
            f"{base_url}/api/v1/characters/",
            json=character_data,
            headers=headers
        )
        
        if response.status_code == 200:
            character = response.json()["data"]
            print(f"创建角色成功: {character['name']}")
        
        # 搜索角色
        search_response = await client.get(
            f"{base_url}/api/v1/characters/search",
            params={
                "query": "测试",
                "search_type": "vector",
                "limit": 10
            },
            headers=headers
        )
        
        if search_response.status_code == 200:
            results = search_response.json()["data"]["results"]
            print(f"找到 {len(results)} 个角色")
            for result in results:
                print(f"- {result['character']['name']}: {result['score']}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. 批量操作

```python
async def batch_create_characters():
    characters = [
        {
            "name": "角色1",
            "short_bio": "角色1简介",
            "persona_text": "我是角色1",
            "example_lines": ["台词1"],
            "source": "测试"
        },
        {
            "name": "角色2", 
            "short_bio": "角色2简介",
            "persona_text": "我是角色2",
            "example_lines": ["台词2"],
            "source": "测试"
        }
    ]
    
    async with httpx.AsyncClient() as client:
        for character_data in characters:
            response = await client.post(
                "http://localhost:8000/api/v1/characters/",
                json=character_data,
                headers={"Authorization": "Bearer your_token_here"}
            )
            print(f"创建角色: {response.status_code}")

asyncio.run(batch_create_characters())
```

## 错误处理

### 常见错误码

- **400 Bad Request**: 请求参数错误
- **401 Unauthorized**: 认证失败
- **403 Forbidden**: 权限不足
- **404 Not Found**: 资源不存在
- **422 Unprocessable Entity**: 数据验证失败
- **500 Internal Server Error**: 服务器内部错误

### 错误响应格式

```json
{
  "success": false,
  "data": null,
  "msg": "错误描述",
  "error_code": "ERROR_CODE"
}
```

### 处理示例

```python
async def handle_api_error(response):
    if response.status_code == 200:
        return response.json()["data"]
    else:
        error_data = response.json()
        print(f"API错误: {error_data['msg']}")
        return None
```

## 性能优化建议

### 1. 分页查询
```bash
# 使用分页避免一次性加载大量数据
curl "http://localhost:8000/api/v1/characters/?limit=20&offset=0"
```

### 2. 缓存策略
```python
# 客户端缓存频繁查询的结果
import time
from functools import lru_cache

@lru_cache(maxsize=100)
def get_character(character_id, timestamp):
    # 实现缓存逻辑
    pass
```

### 3. 批量操作
```python
# 批量创建角色而不是逐个创建
characters = [character1, character2, character3]
# 使用并发请求
tasks = [create_character(char) for char in characters]
results = await asyncio.gather(*tasks)
```

## 监控和调试

### 1. 查看API文档
访问 `http://localhost:8000/docs` 查看完整的API文档。

### 2. 日志查看
```bash
# 查看应用日志
tail -f logs/app.log

# 查看特定API的日志
grep "POST /api/v1/characters" logs/app.log
```

### 3. 性能监控
```python
import time

start_time = time.time()
response = await client.get("/api/v1/characters/search?query=test")
end_time = time.time()
print(f"API响应时间: {end_time - start_time:.2f}秒")
```
